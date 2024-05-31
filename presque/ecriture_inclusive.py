import re

_suffixes_feminins = r"|".join(
    [
        "trice",
        "rice",
        "ice",
        "euse",
        "ère",
        "oresse",
        "esse",
        "lle",
        "le",
        "tte",
        "te",
        "ive",
        "ale",
        "se",
        "ne",
        "e",
    ]
)
_re_issuffix = re.compile(
    r"x?({feminine})?x?s?x?".format(feminine=_suffixes_feminins)
).fullmatch
_re_startswith_feminine = re.compile(_suffixes_feminins).match


def issuffix(s):
    """Évalue si une string est un suffixe d'écriture inclusive.

    Args:
        s (str): la string.

    Returns (bool)
    """

    return True if _re_issuffix(s) and s.count("x") < 2 else False


def match_suff_nonbinary(s):
    """Match (début de str) un suffixe non-binaire 'x'.

    Args:
        s (str): le suffixe dans lequel match 'x'.

    Returns (int, None): la longueur du match (donc 1) si un match est trouvé, sinon None.
    """

    return 1 if s[0] == "x" else None


def match_suff_plural(s):
    """Match (début de str) un suffixe pluriel 's'.

    Args:
        s (str): le suffixe dans lequel match 's'.

    Returns (int, None): la longueur du match (donc 1) si un match est trouvé, sinon None.
    """

    return 1 if s[0] == "s" else None


def match_suff_feminine(s):
    """Match en début de str un suffixe féminin.

    Args:
        s (str): le suffixe dans lequel un suffixe.

    Returns (int, None): la longueur du match si un match est trouvé, sinon None.

    Note:
        l'ordre dans lequel sont placés, ci-dessous, les différents suffixes est important (c'est un ordre de priorité, il faut par exemple absolument éviter de mettre en première position 'e', qui empêcherait de match 'esse' et 'euse'.)
    """

    r = _re_startswith_feminine(s)
    return r.end() if r else None


def split_suffixes(suffix):
    """Décompose un suffixe inclusif aggrégé.

    Args:
        suffix (str): le suffixe à décomposer.

    Returns (list): la liste des suffixes décomposés (qui peut être une liste d'un seul élément).

    Exemples:
        - "eusexs" -> ["euse", "x", "s"]
        - "xeuse" -> ["x", "euse", "s"]

    Si le suffixe ne peut pas être complétement décomposé, le suffixe est retourné tel quel (mais dans une liste).
        - "acteurice" -> ["acteurice"]
        - "riceyyy" -> ["rice"]

    La fonction définit un ordre dans lequel les suffixes peuvent apparaître (le pluriel ne peut pas se trouver avant le féminin), et chaque type de suffixe (féminin, non-binaire, pluriel) ne peut apparaître qu'une seule fois:
        - "euseeuse" -> ["euseeuse"]
        - "srice" -> ["srice"]
    """

    a = []
    s = suffix
    already = set()
    functions = (
        match_suff_nonbinary,
        match_suff_feminine,
        match_suff_nonbinary,
        match_suff_plural,
        match_suff_nonbinary,
    )
    for fn in functions:
        if fn in already:
            continue
        suff_len = fn(s)
        if suff_len:
            suff = s[:suff_len]
            a.append(suff)
            s = s[suff_len:]
            if s == "":
                return a
            already.add(fn)
    return [suffix]
