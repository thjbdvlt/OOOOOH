presque
======

normalisation de mots français pour [spacy](https://spacy.io/).

|x|y|
|--|--|
|chuuuuut!!!!!|chut!|
|bateâu|bateau|
|HO|ho|
|PEùùùT-èTRE|peut-être|
|auteur-rice-x-s|auteur·ricexs|
|peut—être|peut-être|
|autre[ment]|autrement|
|désœuvrement|désoeuvrement|

- les caractères répétés plus de 3x (2 pour la ponctuation) sont réduits à un seul (sauf "...").
- les mots hors-lexiques sont remplacés par une version accentuée différemment, si une telle version existe.
- les mots sont mis en minuscules.
- les mots composés sont normalisés par l'agrégation de leurs composants, normalisés individuellement.
- les variantes d'écritures inclusives sont uniformisées (caractère de séparation, nombre de caractères, ordre des suffixes).
- les parenthèses et crochets sont enlevés.
- les variantes de tirets (et d'apostrophes) remplacées par des tirets (ou apostrophes) simples (droites).

usage
-----

pour l'utiliser comme composant d'une [_pipeline spacy_](https://spacy.io/usage/processing-pipelines):

```python
import spacy

nlp = spacy.load("fr_core_news_lg")
nlp.add_pipe('presque_normalizer', first=True)

[i.norm_ for i in nlp("QUOOOIIIIII PEUUUUUT---ÉÉÉtréééééé")]
```

```
[quoi, peut-être]
```

it has `to_disk()` and `from_disk()` methods:

```python
nlp.to_disk("./model_output")
```

configuration
-------------

```python
import spacy

def aggregate_suffixes(word: str, suffixes: list, char: str) -> str:
    return word + char + char.join(map(str.upper, suffixes))

config = dict(
    name="normalizer",
    exc={"clef": "clé", "ptetre": "peut-être"},
    words_files=["./exemple/liste/de/mots/specifique.txt"],
    use_default_word_list=False,
    suff_sep_char="-",
    fn_agg_suff=aggregate_suffixes,
)

nlp = spacy.load("fr_core_news_lg")
nlp.add_pipe("presque_normalizer", first=True, config=config)
```

installation
------------

```bash
pip install git+https://github.com/thjbdvlt/spacy-presque
```

dépendances
-----------

- [spacy](https://spacy.io/)
