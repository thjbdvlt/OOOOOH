def set_suff_sort_key(s):
    """Attribue au suffixe donné en paramètre une valeur pour les ordonner.

    Args:
        s (str): le suffixe.

    Returns (int): 

    Note:
        Cette fonction est uniquement destinée à être utilisée comme `key` dans la fonction `sorted`.
    """

    if s == "s":
        return 2
    elif s == "x":
        return 1
    else:
        return 0


def agrege_un(word, suffixes, char) -> str:
    """Agrège un mot et une liste de suffixes avec un point médian entre le mot d'une part et les suffixes assemblés d'autre part.

    Args:
        suffixes (list): les suffixes.

    Returns (str): les suffixes agregés.

    Exemple:
        - ["x", "s", "rice"] -> "·ricexs"
    """

    suffixes = sorted(suffixes, key=set_suff_sort_key)
    suffixes = "".join(suffixes)
    return f"{word}{char}{suffixes}"


def agrege_plusieurs(word, suffixes, char) -> str:
    """Agrège un mot et une liste de suffixes avec un point médian entre le mot et les suffixes, et entre chaque suffixe.

    Args:
        word (str): le mot.
        suffixes (list): les suffixes.

    Returns (str): le mot et les suffixes agrégés.

    Exemple:
        - "auteur·rice·x·s"
    """

    suffixes = sorted(suffixes, key=set_suff_sort_key)
    suffixes = char.join(suffixes)
    return f"{word}{suffixes}"


def remplace_par_feminin(word, suffixes, char) -> str:
    """Enlève les suffixes d'écriture inclusive et remplace, dans le mot, la terminaison masculine par une terminaison féminine.

    L'usage de cette fonction n'est pas recommandé, en premier lieu car il n'est pas souhaitable de dés-inclusiviser un texte, ensuite car elle modifie les propriétés morphologiques du mot, et enfin car elle est (probablement) assez imprécise. Elle peut toutefois être utile si l'on doit utiliser des modèles incapable d'analyser des textes avec de l'écriture inclusive (et permettra, à défaut d'améliorer ces modèles, de pouvoir analyser ces textes).

    Args:
        word (str): le mot.
        suffixes (list): les suffixes.

    Returns (str): le mot modifié, sans suffixes, au féminin.
    """

    lookup = {
        "trice": "teur",
        "rice": "eur",
        "ice": "eur",
        "euse": "eur",
        "ère": "er",
        "oresse": "eur",
        "esse": "",
        "lle": "l",
        "le": "l",
        "tte": "t",
        "te": "t",
        "ive": "f",
        "ale": "al",
        "se": "s",
        "ne": "n",
        "e": "",
    }
    suffixes = list(suffixes)
    if "x" in suffixes:
        suffixes.remove("x")
    if "s" in suffixes:
        plural = "s"
        suffixes.remove("s")
    else:
        plural = ""
    if len(suffixes) == 0:
        return word + plural
    else:
        fem = suffixes[0]
        mas = lookup.get(fem)
        if word.endswith(mas):
            return word[: -len(mas)] + fem + plural
    return word + plural
