import re

from constants import (
    DEVICE_WORDS,
    STOPWORDS,
    DOSAGE_WORDS,
    OCR_BAD_CHARS
)

##############################################################################
# BAD WORDS
##############################################################################

BAD_PHRASES = {

    "not less than",
    "each contains",
    "contains",
    "additional strength",
    "additional indication",
    "finished formulation",
    "same as approved",
    "for import",
    "quality assured biosimilars",
    "quality-assured biosimilars",
    "emlc only",

}

##############################################################################
# REGEX
##############################################################################

ONLY_SYMBOLS = re.compile(r"^[^A-Za-z]+$")

ONLY_NUMBERS = re.compile(r"^[0-9 .+\-/]+$")

TOO_MANY_SYMBOLS = re.compile(r"[^\w\s+]{3,}")

##############################################################################
# BASIC CHECKS
##############################################################################

def has_bad_phrase(text):

    low = text.lower()

    for phrase in BAD_PHRASES:

        if phrase in low:
            return True

    return False


##############################################################################

def has_ocr_artifacts(text):

    for ch in OCR_BAD_CHARS:

        if ch in text:
            return True

    return False


##############################################################################

def starts_with_symbol(text):

    if len(text) == 0:
        return True

    return text[0] in ".:/%*[]{}"


##############################################################################

def too_short(text):

    letters = re.findall(r"[A-Za-z]", text)

    return len(letters) < 3


##############################################################################

def only_symbols(text):

    return ONLY_SYMBOLS.match(text) is not None


##############################################################################

def only_numbers(text):

    return ONLY_NUMBERS.match(text) is not None


##############################################################################

def too_many_symbols(text):

    return TOO_MANY_SYMBOLS.search(text) is not None


##############################################################################
# DEVICE CHECK
##############################################################################

def looks_like_device(text):

    for word in text.split():

        if word.lower().strip(".,+-") in DEVICE_WORDS:

            return True

    return False


##############################################################################
# DOSAGE ONLY
##############################################################################

def only_dosage_words(text):

    words = text.split()

    if not words:
        return True

    valid = 0

    for word in words:

        low = word.lower().strip(".,+-")

        if low not in DOSAGE_WORDS and low not in STOPWORDS:

            valid += 1

    return valid == 0


##############################################################################
# DUPLICATE ALIASES
##############################################################################

def clean_aliases(alias_list):

    cleaned = []

    seen = set()

    for alias in alias_list:

        alias = re.sub(r"\s+", " ", alias).strip()

        if len(alias) < 3:
            continue

        key = alias.lower()

        if key in seen:
            continue

        seen.add(key)

        cleaned.append(alias)

    return sorted(cleaned)


##############################################################################
# MASTER VALIDATOR
##############################################################################

def validate(generic):

    if generic is None:
        return False

    generic = generic.strip()

    if len(generic) == 0:
        return False

    if too_short(generic):
        return False

    if starts_with_symbol(generic):
        return False

    if only_symbols(generic):
        return False

    if only_numbers(generic):
        return False

    if has_bad_phrase(generic):
        return False

    if has_ocr_artifacts(generic):
        return False

    if too_many_symbols(generic):
        return False

    if looks_like_device(generic):
        return False

    if only_dosage_words(generic):
        return False

    return True