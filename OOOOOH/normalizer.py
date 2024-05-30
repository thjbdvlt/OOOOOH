import re
from spacy.lookups import Lookups
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

        Returns:
            None

        Exemple d'utilisation du paramètre `agg_suff`:
            '·': auteur·ricexs (défaut)
            '··': auteur·rice·x·s
            '--': auteur-rice-x-s
            '..': auteur.rice.x.s
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
        d_desacc = {}

        lines = []
        if use_default_word_list is True:
            import pkgutil

            lines.extend(
                pkgutil.get_data(__name__, "data/liste_de_mots.txt")
                .decode()
                .split("\n")
            )

        # la valeur du paramètre 'words_files' est utilisée pour ajouter des mots à la liste.
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
            d_desacc[self.desaccentuer(l)] = l

        # utilise l'objet `Lookups` de spaCy, optimisé pour ces tâches.
        self.lookup = Lookups()
        self.lookup.add_table("normes", d)
        self.lookup.add_table("normes_sans_accents", d_desacc)

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

    def reduire_multiple(self, word) -> str:
        """Supprime les caractères répétées plus de trois fois.

        Args:
            word (str): le mot.

        Returns:
            str: le mot, sans les lettres répétées.

        Exemple:
            'haaaa' -> 'ha'
        """

        return self.re_multi.sub(r"\1", word)

    def normaliser_mot(self, word) -> str:
        """Cherche ou construit la forme normalisée d'un mot.

        Args:
            word (str): Le mot.

        Returns:
            str: La forme normalisée du mot.
        """

        index = self.lookup.get_table("normes")
        index_desaccentue = self.lookup.get_table(
            "normes_sans_accents"
        )

        # cherche si le mot est dans la table lookup.
        if word in index:
            return index[word]

        # une copie du mot, qui va être modifiée successivement jusqu'à trouver une norme.
        s = word

        # reconstruit le mot, caractère par caractère. si un caractère est dans le set 'chars_todel', il est ignoré, s'il est dans le dict 'chars_toreplace' il est remplacé (ex. '·' par '-'). dans les autres cas, il est placé tel quel.
        rep = self.chars_toreplace
        s = s.lower()
        s = "".join(
            [
                rep[c] if c in rep else c
                for c in s
                if c not in self.chars_todel
            ]
        )

        # enlève les répétitions de caractères (à partir de trois)
        s = self.reduire_multiple(s)
        if "-" in s:
            # word = self.enlever_suffixes(word)  # todo: implémenter
            if "-" in s:
                x = s.split("-")
                a = []
                for i in x:
                    if i in index:
                        norm = index[i]
                        a.append(norm)
                        continue
                    di = self.desaccentuer(i)
                    if di in index_desaccentue:
                        norm = index_desaccentue[di]
                        a.append(norm)
                        index[i] = norm
                        continue
                    a.append(i)
                    index[i] = i
                s = "-".join(a)

        if s in index:
            return index[s]

        y = index_desaccentue.get(self.desaccentuer(s))
        if y is not None:
            index.set(s, y)
            return y

        # index[word] = word
        index.set(s, s)
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
