from OOOOOH.ecriture_inclusive import issuffix, split_suffixes
from OOOOOH.default import agrege_un, agrege_plusieurs

for s in (
    "rice",
    "scrice",
    "tricexs",
    "tricex",
    "xrice",
    "xrices",
    "euses",
    "rose",
    "eurice",
    "ricexxsxss",
):
    if issuffix(s):
        print(agrege_un("auteur", split_suffixes(s)))
        print(agrege_plusieurs("auteur", split_suffixes(s)))
    else:
        print(s, False)
