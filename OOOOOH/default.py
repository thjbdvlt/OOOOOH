def set_suff_sort_key(s):
    """Attribue au suffixe donné en paramètre une valeur pour les ordonner.

    Args:
        s (str): le suffixe.

    Returns:
        int

    Note:
        Cette fonction est uniquement destinée à être utilisée comme `key` dans la fonction `sorted`.
    """

    if s == "s":
        return 1
    elif s == "x":
        return 0
    else:
        return -1


def agg_suff_one_dot(word, suffixes, char) -> str:
    """Agrège un mot et une liste de suffixes avec un point médian entre le mot d'une part et les suffixes assemblés d'autre part.

    Args:
        word (str): le mot.
        suffixes (list): les suffixes.

    Returns:
        str: le mot et les suffixes, agrégés.

    Exemple:
        - "auteur·ricexs"
    """

    s = "".join(suffixes)
    return f"{word}{char}{s}"


def agg_suff_many_dots(word, suffixes, char) -> str:
    """Agrège un mot et une liste de suffixes avec un point médian entre le mot et les suffixes, et entre chaque suffixe.

    Args:
        word (str): le mot.
        suffixes (list): les suffixes.

    Returns:
        str: le mot et les suffixes agrégés.

    Exemple:
        - "auteur·rice·x·s"
    """

    return char.join([word] + suffixes)


def replace_suff_to_feminine(word, suffixes) -> str:
    """Enlève les suffixes d'écriture inclusive et remplace, dans le mot, la terminaison masculine par une terminaison féminine.

    L'usage de cette fonction n'est pas recommandé, en premier lieu car il n'est pas souhaitable de dés-inclusiviser un texte, ensuite car elle modifie les propriétés morphologiques du mot, et enfin car elle est (probablement) assez imprécise. Elle peut toutefois être utile si l'on doit utiliser des modèles incapable d'analyser des textes avec de l'écriture inclusive (et permettra, à défaut d'améliorer ces modèles, de pouvoir analyser ces textes).

    Args:
        word (str): le mot.
        suffixes (list): les suffixes.

    Returns:
        str
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
