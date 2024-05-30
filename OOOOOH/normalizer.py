import re
from spacy.lookups import Table
import OOOOOH.ecriture_inclusive
import OOOOOH.default
import OOOOOH.chars


class Normalizer:
    def __init__(
        self,
        words_files=[],
        exc=[],
        agg_suff="·",
        use_default_word_list=True,
    ):
        """initier un Normalizer.

        Args:
            words_fp (str):  Fichier avec une liste de mot (un par ligne)
            exc (dict):  Les exceptions, par exemple {"ouais": "oui"}
            agg_suff (str, Callable):  Accepte soit une fonction définissant comment agréger les suffixes d'écriture inclusive, soit une chaîne de caractère permettant de définir comment utiliser les méthodes prédéfinies.
            use_default_word_list (bool):  utiliser (en plus des éventuels fichiers de mots en paramètres) la liste de mots integrée au package.

        Returns: None

        Exemple d'utilisation du paramètre `agg_suff`:
            '·': auteur·ricexs (défaut)
            '··': auteur·rice·x·s
            '..': auteur.rice.x.s
            '-': auteur-ricexs (pas recommandé: moins performant)
            '_': auteur_ricexs
            None: autrices
        """

        # une table qui associe, à chaque lettre accentuée, sa version non-accentuée
        self.accents_table = {}
        for letter, accentuated in {
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
        self.index = Table(name="normes", data=d)
        self.index_noacc = Table(
            name="normes_sans_accents", data=d_noacc
        )

        # compile le regex qui trouve des séquences de lettres identiques (3x ou plus la même lettre d'affilé)
        self.re_multi = re.compile(
            rf"(?P<letter>[{OOOOOH.chars.ALPHA}])(?P=letter){{2,}}"
        )

        # certains caractères sont tout simplement enlevés, parenthèses et brackets.
        self.chars_todel = set(
            OOOOOH.chars.PARENTHESES + OOOOOH.chars.BRACKETS
        )

        # d'autres sont uniformisés: tirets et apostrophes.
        hyphens = set(
            OOOOOH.chars.HYPHEN
            + OOOOOH.chars.PERIOD
            + OOOOOH.chars.PERIOD_CENTERED
        ) - set("-")
        apostrophes = set(OOOOOH.chars.APOSTROPHE) - set("'")
        self.chars_toreplace = {i: "-" for i in hyphens}
        self.chars_toreplace.update({i: "'" for i in apostrophes})

        # ajouter les exceptions
        n = self.lookup.get_table("normes")
        for key, value in exc.items():
            n.set(key, value)

    def desaccentuer(self, word):
        """Enlève les accents sur les voyelles d'un mot.

        Args:
            word (str): le mot dont il faut enlever les accents.

        Returns:
            str: le mot
        """

        d = self.accents_table
        chars = [d[c] if c in d else c for c in word]
        word = "".join(chars)
        return word

    def cherche_avec_ou_sans_accents(self, word, norm) -> str:
        """cherche un mot dans les indexes (version accentuée et désaccentuée).

        (met à jour les indexes en même temps.)

        args:
            - word (str): le mot.

        returns (str): la norme trouvée (le mot tel quel, si rien n'a été trouvé).
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

    def normaliser_mot(self, word) -> str:
        """Cherche ou construit la forme normalisée d'un mot.

        Args:
            word (str): Le mot.

        Returns:
            str: La forme normalisée du mot.
        """

        index = self.index

        # cherche si le mot est, tel quel, dans la table lookup.
        if word in index:
            return index[word]

        # les normes sont toujours en minuscules
        word = word.lower()

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
        word = self.re_multi.sub(r"\1", word)

        # cherche si le mot est, après ces transformations de normalisations, dans l'index.
        if word in index:
            return index[word]

        # une copie du mot pour des modifications destinées uniquement à chercher une norme (et non pas, comme dans les opérations précédentes, à la construire).
        s = word

        if "-" in s:
            # word = self.enlever_suffixes(word)  # todo: implémenter
            # si la string contient encore des tirets, il s'agit alors d'un mot composé
            if "-" in s:
                x = s.split("-")
                # enlève les élements vides, produits par exemples dans "-je" ou "peut--être".
                x = [i for i in x if i != ""]
                fn = self.cherche_avec_ou_sans_accents
                a = [fn(sub) for sub in x]
                s = "-".join(a)

        s = fn(s)
        return s

    def __call__(self, doc):
        """normalise les mots.

        Args:
            doc (Doc)

        Returns:
            Doc
        """

        for token in doc:
            if any((c.isalpha() for c in token.text)):
                token.norm_ = self.normaliser_mot(s=token.text)
        return doc
