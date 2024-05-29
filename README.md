CHUUUUT
==========

normalisation de mots français pour [spacy](https://spacy.io/): `OOOOOH` devient `oh`.

|x|y|règle|
|--|--|--|
|chuuuuut!!!!!|chut!|les caractères répétés 3x ou plus sont réduits à un seul|
|bateâu|bateau|les mots hors-lexiques sont remplacés par une version accentuée différemment, si une telle version existe|
|peut—être|peut-être|toutes les variantes de tirets sont remplacées par des tirets simples|
|autre(s)|autres|les parenthèses intra-mot sont enlevées|
|HO|ho|les mots sont mis en minuscule|
|PEUUUUT-èTRE|peut-être|fonctionne aussi sur les mots composé: chaque mot est normalisé séparément|
|auteur-ricexs|auteur·rice·x·s|uniformise (plusieurs méthodes disponibles) les variantes d'écriture inclusive|

usage
-----

pour l'utiliser comme composant d'une [_pipeline spacy_](https://spacy.io/usage/processing-pipelines):

```python
import CHUUUUT
import spacy

@spacy.Language.factory("chut_normalizer")
def create_chut_normalizer(nlp, name="chut_normalizer"):
    """Construit un normalizer de Tokens."""

    # le lexique est une liste de mots (un par ligne).
    lexique_fp = "/chemin/vers/exemple/words.txt"

    # un `dict` pour des exceptions spécifiques
    exc = {"ouais": "oui", "ptetre": "peut-être"}

    return CHUUUUT.Normalizer(
        nlp=nlp,
        fp_dic=paths.fp_dic,
        fp_aff=paths.fp_aff,
        exc=exc,
    )

nlp = spacy.load("fr_core_news_lg")
nlp.add_pipe("chut_normalizer", first=True)
```
