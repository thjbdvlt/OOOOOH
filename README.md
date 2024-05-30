![import OOOOOH as oh](./img/import_as_oh.png)

OOOOOH
======

normalisation de mots français pour [spacy](https://spacy.io/): `OOOOOH` devient `oh`.

|x|y|
|--|--|
|chuuuuut!!!!!|chut!|
|bateâu|bateau|
|HO|ho|
|PEùùùT-èTRE|peut-être|
|auteur-rice-x-s|auteur·ricexs|
|peut—être|peut-être|
|autre[ment]|autres|

- les caractères répétés plus de 3x (2 pour la ponctuation) sont réduits à un seul (sauf "...").
- les mots hors-lexiques sont remplacés par une version accentuée différemment, si une telle version existe.
- les mots sont mis en minuscules.
- les mots composés sont normalisés séparément.
- les variantes d'écritures inclusives sont uniformisées (caractère de séparation, nombre de caractères, ordre des suffixes).
- les parenthèses et crochets sont enlevés.
- les variantes de tirets (et d'apostrophes) remplacées par des tirets (ou apostrophes) simples (droites).

usage
-----

pour l'utiliser comme composant d'une [_pipeline spacy_](https://spacy.io/usage/processing-pipelines):

```python
import OOOOOH as oh
import spacy

@spacy.Language.factory("oh_normalizer")
def create_chut_normalizer(nlp, name="oh_normalizer"):
    """Construit un normalizer de Tokens."""

    return oh.Normalizer(nlp=nlp)

nlp = spacy.load("fr_core_news_lg")
nlp.add_pipe("oh_normalizer", first=True)
```

configuration
-------------

```python
import OOOOOH as oh
import spacy

def aggregate_suffixes(suffixes: list, char: str) -> str:
    return char + char.join([suffixes])

@spacy.Language.factory("oh_normalizer")
def create_chut_normalizer(nlp, name="oh_normalizer"):
    """Construit un normalizer de Tokens."""

    return oh.Normalizer(
        nlp=nlp,
        exc={"ptetre": "peut-être", "ouais": "oui"},
        words_files=["./exemple/liste/de/mots/spécifique.txt"],
        use_default_word_list=False,
        suff_sep_char="-",
        fn_agg_suff=aggregate_suffixes,
    )

nlp = spacy.load("fr_core_news_lg")
nlp.add_pipe("oh_normalizer", first=True)
```

installation
------------

```bash
git clone https://github.com/thjbdvlt/OOOOOH OOOOOH
cd OOOOOH
pip install .
```

dépendances
-----------

- [spacy](https://spacy.io/)
