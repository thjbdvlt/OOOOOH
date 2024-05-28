CHUUUUT
==========

normalisation de mots français pour [spacy](https://spacy.io/): `CHUUUUT` devient `chut`.

|x|y|règle|
|--|--|--|
|chuuuuut!!!!!|chut!|les caractères répétés 3x ou plus sont réduits à un seul|
|CHUT|chut|les mots sont mis en minuscule|
|bateâu|bateau|les mots hors-lexiques sont remplacés par une version accentuée différemment, si une telle version existe|
|autre(s)|autres|les parenthèses intra-mot sont enlevées|
|peut—être|peut-être|toutes les variantes de tirets sont remplacées par des tirets simples|

usage
-----

pour l'utiliser comme composant d'une [_pipeline spacy_](https://spacy.io/usage/processing-pipelines):

```python
import CHUUUUT
import spacy

@spacy.Language.factory("chut_normalizer")
def create_chut_normalizer(nlp, name="chut_normalizer"):
    fp_dic = "/chemin/vers/exemple/fr_xii.dic"
    fp_aff = "/chemin/vers/exemple/fr_xii.aff"
    return CHUUUUT.Normalizer(
        nlp=nlp,
        fp_dic=paths.fp_dic,
        fp_aff=paths.fp_aff
    )

nlp = spacy.load("fr_core_news_lg")
nlp.add_pipe("chut_normalizer", first=True)
```
