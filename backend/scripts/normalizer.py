import re

from constants import (
    REMOVE_PHRASES,
    DOSAGE_WORDS,
    DEVICE_WORDS,
    STOPWORDS,
    SUFFIX_WORDS,
    ONLY_SYMBOL_REGEX
)

from utils import (
    preprocess,
    smart_title
)

##############################################################################
# REMOVE PHRASES
##############################################################################

def remove_known_phrases(text: str) -> str:

    for phrase in REMOVE_PHRASES:
        text = re.sub(
            rf"\b{re.escape(phrase)}\b",
            " ",
            text,
            flags=re.I
        )

    return text


##############################################################################
# REMOVE DOSAGE WORDS
##############################################################################

def remove_dosage_words(text: str):

    kept = []

    for word in text.split():

        low = word.lower().strip(".,+-")

        if low in DOSAGE_WORDS:
            continue

        kept.append(word)

    return " ".join(kept)

##############################################################################
# REMOVE TOKENS
##############################################################################

REMOVE_TOKENS = {
    "ml",
    "per ml",
    "/ml",
    "w/w",
    "w/v",
    "v/v",
    "ip",
    "bp",
    "usp",
    "tabs",
    "tab",
    "tablet",
    "tablets",
    "capsule",
    "capsules",
    "effervescent",
    "dispersible",
    "oral",
    "spray",
    "roll-on",
    "roll",
    "on",
    "sustained",
    "release",
    "sr",
    "er",
    "xr",
    "cr",
}

##############################################################################
# REMOVE SUFFIXES
##############################################################################

def remove_suffixes(text):

    kept=[]

    for word in text.split():

        low=word.lower().strip(".,")

        if low in SUFFIX_WORDS:
            continue

        kept.append(word)

    return " ".join(kept)


##############################################################################
# REMOVE STOP WORDS
##############################################################################

def remove_stopwords(text):

    kept=[]

    for word in text.split():

        low=word.lower().strip(".,+-")

        if low in STOPWORDS:
            continue

        kept.append(word)

    return " ".join(kept)


##############################################################################
# DEVICE DETECTOR
##############################################################################

def contains_device(text):

    for word in text.split():

        if word.lower().strip(".,+-") in DEVICE_WORDS:
            return True

    return False


##############################################################################
# NORMALIZE +
##############################################################################

def normalize_plus(text):

    text=re.sub(r"\+\s+\+","+",text)

    text=re.sub(r"\s*\+\s*"," + ",text)

    text=re.sub(r"\++","+ ",text)

    text=text.replace("+  +","+")

    text=re.sub(r"\s+"," ",text)

    return text.strip(" +.")


##############################################################################
# BASIC VALIDATION
##############################################################################

def looks_like_garbage(text):

    if len(text)<3:
        return True

    if ONLY_SYMBOL_REGEX.match(text):
        return True

    if text.startswith((".",":","/","%","*")):
        return True

    if len(re.findall(r"[A-Za-z]",text))<3:
        return True

    return False


##############################################################################
# MAIN FUNCTION
##############################################################################

def normalize_medicine(raw_name):

    alias = raw_name.strip()

    text = preprocess(alias)

    text = remove_known_phrases(text)

    text = remove_suffixes(text)

    text = remove_dosage_words(text)

    text = remove_stopwords(text)

    text = normalize_plus(text)

    if contains_device(text):
        return None,None

    if looks_like_garbage(text):
        return None,None

    generic = smart_title(text)

    return generic, alias