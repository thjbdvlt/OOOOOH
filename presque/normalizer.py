import re
import spacy.lookups
import itertools
from presque import default
from presque import chars
from presque import ecriture_inclusive
import spacy.util

REGISTERED_NAME = "presque_normalizer"


class Normalizer:
    def __init__(
        self,
        nlp,
        words_files=[],
        exc={},
        fn_agg_suff=None,
        suff_sep_char="·",
        use_default_word_list=True,
    ):
        """Initier un Normalizer.

        Args:
            nlp:  le modèle chargé par spacy avec la pipeline.
            words_files (list):  une liste de fichiers à charger pour les normes.
            exc (dict):  un dictionnaire mappant des graphie à des normes.
            fn_agg_suff (callable):  une fonction pour agréger les suffixes d'écriture inclusive.
            suff_sep_char (str):  le caractère à utiliser pour séparer le mot des suffixes inclusifs (et, éventuellement, les suffixes entre eux).
            use_default_word_list (bool):  utiliser la liste de mots fournis par défault. (default: True)
        """

        self.suff_sep_char = suff_sep_char

        # la valeur du paramètre `fn_agg_suff` doit être callable,
        if not fn_agg_suff:
            self.agrege_suffixes = default.agrege_un
        elif callable(fn_agg_suff):
            self.agrege_suffixes = fn_agg_suff
        else:
            print(fn_agg_suff, fn_agg_suff)
            raise TypeError("`fn_agg_suff` is not callable.")

        # une table qui associe, à chaque lettre accentuée, sa version non-accentuée
        self.accents_table = {}
        for letter, accentuated in {
            "c": "ç",
            "e": "éèêë",
            "u": "üûù",
            "a": "âàä",
            "o": "öô",
            "i": "îï",
        }.items():
            for acc in accentuated:
                self.accents_table[acc] = letter

        # crée deux tables de lookup: une première qui contient tous les mots (et dans laquelle seront ajoutés les variantes orthographiques, à mesure de l'analyse), et une autre qui contient les versions désaccentués, pointant vers les normes (par exemple: {"etre": "être"}).
        d = {}
        d_noacc = {}
        lines = []
        if use_default_word_list is True:
            import pkgutil

            lines.extend(
                pkgutil.get_data(__name__, "data/liste_de_mots.txt")
                .decode()
                .split("\n")
            )

        # la valeur du paramètre 'words_files' est utilisée pour ajouter des mots à la liste. il peut s'agir soit d'un fichier unique (str) soit d'une liste de fichiers.
        if isinstance(words_files, (list, tuple, set)):
            for fp in words_files:
                with open(fp, "r") as f:
                    lines.extend(f.readlines())
        elif isinstance(words_files, str):
            with open(words_files, "r") as f:
                lines.extend(f.readlines())

        # ajouter chaque mot (un par ligne) aux lookup tables
        for l in lines:
            l = l.strip()
            d[l] = l
            d_noacc[self.desaccentuer(l)] = l

        # utilise l'objet `Table` de spaCy, optimisé pour le lookup.
        self.index = spacy.lookups.Table(name="normes", data=d)
        self.index_noacc = spacy.lookups.Table(
            name="normes_sans_accents", data=d_noacc
        )

        # compile le regex qui trouve des séquences de lettres identiques (3x ou plus la même lettre d'affilé)
        self.re_multi = re.compile(
            rf"(?P<letter>[{chars.ALPHA}])(?P=letter){{2,}}"
        )

        # certains caractères sont tout simplement enlevés, parenthèses et brackets.
        self.chars_todel = set(chars.PARENTHESES + chars.BRACKETS)

        # d'autres sont uniformisés: tirets et apostrophes.
        hyphens = set(
            chars.HYPHEN + chars.PERIOD + chars.PERIOD_CENTERED
        ) - set("-")
        apostrophes = set(chars.APOSTROPHE) - set("'")
        self.chars_toreplace = {i: "-" for i in hyphens}
        self.chars_toreplace.update({i: "'" for i in apostrophes})
        self.chars_toreplace["œ"] = "oe"

        # ajouter les exceptions
        n = self.index
        for key, value in exc.items():
            n.set(key, value)

    def desaccentuer(self, word):
        """Enlève les accents sur les voyelles d'un mot.

        Args:
            word (str): le mot dont il faut enlever les accents.

        Returns (str): le mot
        """

        d = self.accents_table
        chars = [d[c] if c in d else c for c in word]
        word = "".join(chars)
        return word

    def cherche_avec_ou_sans_accents(self, word) -> str:
        """Cherche un mot dans les indexes (version accentuée et désaccentuée).

        (met à jour les indexes en même temps.)

        Args:
            - word (str): le mot.

        Returns (str): la norme trouvée (le mot tel quel, si rien n'a été trouvé).
        """

        index = self.index
        index_noacc = self.index_noacc
        if word in index:
            norm = index[word]
            return norm

        sub_noacc = self.desaccentuer(word)
        if sub_noacc in index_noacc:
            norm = index_noacc[sub_noacc]
            index[word] = norm
            return norm

        index_noacc[word] = word
        index[word] = word
        return word

    def reduce_multichars(self, word) -> str:
        """Réduit les caractères répétés pour expressivité.

        oooooh  ->  ho
        miette  ==  miette
        .....   ->  ...
        !?      ->  ?!

        Args:
            word (str): le mot

        Returns (str): le mot
        """

        # ooooh -> oh
        word = self.re_multi.sub(r"\1", word)

        # ....... -> ...
        while "...." in word:
            word = word.replace("....", "...")

        # ?!?!!!?? -> ?!
        for char in (",", "!", "?"):
            count = word.count(char)
            if count > 1:
                word = word.replace(char, "", count - 1)

        # !? -> ?!
        if "!?" in word:
            word = word.replace("!?", "?!")
        return word

    def decomposer_recomposer(self, s):
        """Décompose et recompose les mots composés et les suffixes d'écriture inclusive.

        Les suffixes d'écriture inclusives sont réorganisés uniformément: "auteur·rice·x·s" et "auteur·xrices" deviendront identique. les mots composés, eux, sont chacuns normalisés séparément et réagregés à la fin: "peùt-ètre" devient "peut-être".

        Args:
            s (str): le mot composé à décomposer-recomposer.

        Returns (str): le mot décomposé-recomposé.
        """

        coupe = s.split("-")
        coupe = [i for i in coupe if i != ""]
        sep_char = self.suff_sep_char
        cherche = self.cherche_avec_ou_sans_accents
        if len(coupe) == 0:
            return s
        elif len(coupe) == 1:
            return coupe[0]
        a = [cherche(coupe[0])]
        for k, g in itertools.groupby(
            coupe[1:], key=ecriture_inclusive.issuffix
        ):
            if k is False:
                words_agg = "-".join((cherche(i) for i in g))
                a.append(f"-{words_agg}")
            else:
                suffixes = itertools.chain.from_iterable(
                    (ecriture_inclusive.split_suffixes(i) for i in g)
                )
                # a.append(self.agrege_suffixes(suffixes, sep_char))
                a[-1] = self.agrege_suffixes(
                    word=a[-1], suffixes=suffixes, char=sep_char
                )
        return "".join(a)

    def normaliser_mot(self, word) -> str:
        """Cherche ou construit la forme normalisée d'un mot.

        Args:
            word (str): Le mot.

        Returns (str): La forme normalisée du mot.
        """

        index = self.index

        # cherche si le mot est, tel quel, dans la table lookup.
        if word in index:
            return index[word]

        # les normes sont toujours en minuscules
        word = word.lower().strip()

        # reconstruit le mot, caractère par caractère. si un caractère est dans le set 'chars_todel', il est ignoré, s'il est dans le dict 'chars_toreplace' il est remplacé (ex. '·' par '-'). dans les autres cas, il est placé tel quel.
        rep = self.chars_toreplace
        word = "".join(
            [
                rep[c] if c in rep else c
                for c in word
                if c not in self.chars_todel
            ]
        )

        # enlève les répétitions de caractères (à partir de trois)
        word = self.reduce_multichars(word)

        # cherche si le mot est, après ces transformations de normalisations, dans l'index.
        if word in index:
            return index[word]

        # une copie du mot pour des modifications destinées uniquement à chercher une norme (et non pas, comme dans les opérations précédentes, à la construire).
        s = word

        cherche = self.cherche_avec_ou_sans_accents

        if "-" in s:
            s = self.decomposer_recomposer(s)

        s = cherche(s)
        return s

    def __call__(self, doc):
        """Normalise les mots.

        Args:
            doc (Doc)

        Returns (Doc): le Doc avec les tokens normalisés (token.norm)
        """

        for token in doc:
            token.norm_ = self.normaliser_mot(token.text)
        return doc

    def to_disk(self, path, exclude=tuple()):
        path = spacy.util.ensure_path(path)
        if not path.exists():
            path.mkdir()
        for idx, filename in [
            (self.index, "index"),
            (self.index_noacc, "index_noacc"),
        ]:
            idx_path = path / filename
            with idx_path.open("wb") as f:
                f.write(idx.to_bytes())

    def from_disk(self, path, *, exclude=tuple()):
        for i in ("index", "index_noacc"):
            idx_path = path / i
            table = spacy.lookups.Table()
            with idx_path.open("rb") as f:
                table.from_bytes(f.read())
            setattr(self, i, table)


@spacy.Language.factory(
    REGISTERED_NAME,
    default_config={
        "name": "presque_normalizer",
        "words_files": [],
        "exc": {},
        "suff_sep_char": "·",
        "use_default_word_list": True,
        "fn_agg_suff": None,
    },
)
def create_presque_normalizer(
    nlp,
    name,
    words_files,
    exc,
    suff_sep_char,
    use_default_word_list,
    fn_agg_suff,
):
    """Construit un normalizer de Tokens.

    Args:
        nlp:  le modèle chargé par spacy avec la pipeline.
        name (str):  le nom du pipeline component.
        words_files (list):  une liste de fichiers à charger pour les normes.
        exc (dict):  un dictionnaire mappant des graphie à des normes.
        suff_sep_char (str):  le caractère à utiliser pour séparer le mot des suffixes inclusifs (et, éventuellement, les suffixes entre eux).
        use_default_word_list (bool):  utiliser la liste de mots fournis par défault. (default: True)

    Returns (Normalizer):  un objet pour normaliser les tokens.
    """

    return Normalizer(
        nlp=nlp,
        words_files=words_files,
        exc=exc,
        suff_sep_char=suff_sep_char,
        use_default_word_list=use_default_word_list,
        fn_agg_suff=fn_agg_suff,
    )
