![import OOOOOH as oh](./img/import_as_oh.png)

OOOOOH
======

normalisation de mots français pour [spacy](https://spacy.io/): `OOOOOH` devient `oh`.

|x|y|règle|
|--|--|--|
|chuuuuut!!!!!|chut!|les caractères répétés 3x ou plus sont réduits à un seul (sauf `...`)|
|bateâu|bateau|les mots hors-lexiques sont remplacés par une version accentuée différemment, si une telle version existe|
|HO|ho|les mots sont mis en minuscule|
|PEùùùT-èTRE|peut-être|fonctionne aussi sur les mots composé: chaque mot est normalisé séparément|
|auteur-rice-x-s|auteur·ricexs|uniformise (plusieurs méthodes disponibles) les variantes d'écriture inclusive|
|peut—être|peut-être|toutes les variantes de tirets sont remplacées par des tirets simples|
|autre[ment]|autres|les parenthèses et crochets intra-mot sont enlevées|

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
