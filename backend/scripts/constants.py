import re

##############################################################################
# REMOVE PHRASES
##############################################################################

REMOVE_PHRASES = {

    "additional indication",
    "additional strength",
    "additional dosage form",
    "same as approved",
    "as approved",
    "finished formulation",
    "finished form",
    "for import",
    "finished formulation import",
    "quality assured biosimilars",
    "quality-assured biosimilars",
    "emlc only",
    "contains",
    "each",
    "not less than",
    "equivalent to",
    "eq to",
    "eq.",
    "colour",
    "color",
    "sterile",

}

##############################################################################
# DOSAGE FORMS
##############################################################################

DOSAGE_WORDS = {

    "tablet","tablets",
    "tab","tabs",

    "capsule","capsules",
    "cap","caps",

    "syrup",
    "suspension",
    "solution",

    "cream",
    "ointment",
    "gel",

    "drop",
    "drops",

    "spray",

    "powder",

    "granules",

    "oral",

    "injectable",

    "injection",

    "inj",

    "respules",

    "rotacaps",

    "chewable",

    "dispersible",

    "film",

    "coated",

    "enteric",

    "release",

    "extended",

    "controlled",

    "modified",

    "prolonged",

    "delayed",

    "sustained",

    "mr",

    "cr",

    "sr",

    "xr",

    "er",

    "xl",

    "od",

    "dt",

    "md",

    "roll-on",

    "roll",

    "on",

    "patch",

    "inhaler",
    
    "lotion",
    
    "mouthwash",
    
    "mouth",
    
    "wash",
    
    "foam",
    
    "shampoo",
    
    "soap",
    
    "paint",
    
    "elixir",
    
    "emulsion",

    "paste",

    "powder",

    "concentrate",

    "nebulizer",

    "nebuliser",

    "sachet",
    
    "sachets",
    
    "liquid",
    
    "lotion",
    
    "spray",
    
    "roll",
    
    "roll-on",
    
    "patch",
    
    "inhaler",
    
    "foam",
    
    "paint"
}

##############################################################################
# DEVICES
##############################################################################

DEVICE_WORDS = {

    "wheelchair",
    "cotton",
    "gauze",
    "belt",
    "bedpan",
    "needle",
    "catheter",
    "bandage",
    "gloves",
    "mask",
    "tube",
    "drain",
    "drainage",
    "velcro",
    "sponge",
    "absorbent",
    "glucometer",
    "lancet",
    "strip",
    "stent",
    "implant",
    "syringe"

}

##############################################################################
# WORDS TO IGNORE
##############################################################################

STOPWORDS = {

    "for",
    "use",
    "during",
    "contains",
    "each",
    "only",
    "less",
    "than",
    "kit",
    "pack",
    "vial",
    "ampoule",
    "ampule",
    "liquid",
    "water",
    "contains",
    "contain",
    "total",
    "less",
    "than",
    "billion",
    "cfu",
    "along",
    "alongwith",
    "along-with",
    "each"

}

##############################################################################
# SALTS
##############################################################################

SALT_NORMALIZATION = {

    "hcl":"Hydrochloride",
    "hydrochlorid":"Hydrochloride",

    "sulphate":"Sulfate",

    "sulph":"Sulfate",

}

##############################################################################
# OCR GARBAGE
##############################################################################

OCR_BAD_CHARS = {

    "Þ",
    "Î",
    "�",
    "≥",
    "≤"

}

##############################################################################
# REGEX
##############################################################################

STRENGTH_REGEX = re.compile(

    r"\b\d+(\.\d+)?\s*(mg|mcg|g|kg|ml|l|iu|units|%|au|meq|mmol)\b",

    re.I

)

BRACKET_REGEX = re.compile(r"\([^)]*\)")

NUMBER_REGEX = re.compile(r"\b\d+(?:/\d+)?(?:\.\d+)?\b")

MULTISPACE_REGEX = re.compile(r"\s+")

ONLY_SYMBOL_REGEX = re.compile(r"^[^A-Za-z]+$")


##############################################################################
# SUFFIX_WORDS
##############################################################################

SUFFIX_WORDS = {
    "ip",
    "bp",
    "usp",
    "ep",
    "ph",
    "i.p",
    "b.p",
    "u.s.p"
}