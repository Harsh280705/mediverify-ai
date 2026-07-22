import re
from constants import (
    STRENGTH_REGEX,
    BRACKET_REGEX,
    NUMBER_REGEX,
    MULTISPACE_REGEX,
    OCR_BAD_CHARS,
    SALT_NORMALIZATION,
)

##############################################################################
# BASIC CLEANERS
##############################################################################

def remove_brackets(text: str) -> str:
    """Remove everything inside brackets."""
    return BRACKET_REGEX.sub(" ", text)


def remove_strength(text: str) -> str:
    """
    Removes:
        500 mg
        5 mL
        0.5 %
        150000 AU
        250 IU
    """
    return STRENGTH_REGEX.sub(" ", text)


def remove_numbers(text: str) -> str:
    """
    Removes remaining standalone numbers.
    """
    return NUMBER_REGEX.sub(" ", text)


##############################################################################
# OCR CLEANUP
##############################################################################

def remove_ocr_artifacts(text: str) -> str:
    """
    Removes weird OCR symbols.
    """

    for ch in OCR_BAD_CHARS:
        text = text.replace(ch, " ")

    text = text.replace("\x00", " ")
    text = text.replace("\x05", " ")
    text = text.replace("\ufeff", " ")

    return text


##############################################################################
# BRAND REMOVAL
##############################################################################

def remove_brand_name(text: str) -> str:
    """
    Removes leading quoted brand names.

    "Hyperox" Peracetic Acid
            ↓
    Peracetic Acid
    """

    text = re.sub(r'^"[^"]+"\s*', "", text)

    return text


##############################################################################
# CONNECTORS
##############################################################################

def normalize_connectors(text: str) -> str:
    """
    Converts:
        &
        and
        with

    into

        +
    """

    text = re.sub(r"\band\b", "+", text, flags=re.I)
    text = re.sub(r"\bwith\b", "+", text, flags=re.I)

    text = text.replace("&", "+")

    return text


##############################################################################
# SALTS
##############################################################################

def normalize_salts(text: str) -> str:

    words = []

    for word in text.split():

        key = word.lower().strip("., ")

        if key in SALT_NORMALIZATION:
            words.append(SALT_NORMALIZATION[key])
        else:
            words.append(word)

    return " ".join(words)


##############################################################################
# PUNCTUATION
##############################################################################

def clean_punctuation(text: str) -> str:

    text = text.replace("/", " ")
    text = text.replace("\\", " ")

    text = text.replace(",", " ")

    text = text.replace(":", " ")

    text = text.replace(";", " ")

    text = text.replace("|", " ")

    # Remove w/w notation
    text = re.sub(r"\bw\s*/\s*w\b", " ", text, flags=re.I)

    return text


##############################################################################
# SPACING
##############################################################################

def clean_spacing(text: str) -> str:

    text = MULTISPACE_REGEX.sub(" ", text)

    text = re.sub(r"\+\s+\+", "+", text)

    text = re.sub(r"\s*\+\s*", " + ", text)

    return text.strip(" .+-")


##############################################################################
# TITLE CASE
##############################################################################

def smart_title(text: str) -> str:
    """
    Better than str.title()

    Doesn't change:
        DNA
        HIV
        IV
        pH
    """

    result = []

    for word in text.split():

        if word.isupper() and len(word) <= 4:
            result.append(word)

        else:
            result.append(word.capitalize())

    return " ".join(result)


##############################################################################
# MASTER PREPROCESSOR
##############################################################################

def preprocess(text: str) -> str:
    """
    Runs all lightweight cleanup functions.

    Does NOT remove dosage words.
    Does NOT validate.
    """

    text = remove_brand_name(text)

    text = remove_ocr_artifacts(text)

    text = remove_brackets(text)

    text = remove_strength(text)

    text = remove_numbers(text)

    text = normalize_connectors(text)

    text = normalize_salts(text)

    text = clean_punctuation(text)

    text = clean_spacing(text)

    return text