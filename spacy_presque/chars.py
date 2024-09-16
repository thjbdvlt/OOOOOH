import re

APOSTROPHE = re.escape("'`´’")
SINGLE_QUOTE = re.escape("‘´’")
HYPHEN = re.escape("-–—")
PERIOD = re.escape(".")
PERIOD_CENTERED = re.escape("·")
PARENTHESES = re.escape("()")
BRACKETS = re.escape("[]")
BRACES = re.escape("{}")
COMMA = re.escape(",")
SLASH = re.escape("/")
QUESTION = re.escape("?")
EXCLAM = re.escape("!")
ALPHA_LOWER = "a-zà-ÿ"
ALPHA_UPPER = ALPHA_LOWER.upper()
ALPHA = ALPHA_LOWER + ALPHA_UPPER
