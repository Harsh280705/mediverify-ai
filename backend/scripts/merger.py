from collections import defaultdict
import re

##############################################################################
# NORMALIZATION KEY
##############################################################################

def create_key(name: str) -> str:
    """
    Generates a comparison key.

    Example

    Abacavir Sulfate
    Abacavir sulfate
    ABACAVIR SULFATE

    ↓

    abacavir sulfate
    """

    key = name.lower()

    key = key.replace("-", " ")

    key = re.sub(r"\s+", " ", key)

    key = key.strip()

    return key


##############################################################################
# BEST GENERIC
##############################################################################

def choose_generic(names):

    """
    Choose the cleanest canonical name.

    Preference:
        1. Proper Title Case
        2. Shortest
        3. Alphabetical
    """

    names = sorted(set(names))

    title_case = [
        n for n in names
        if n == " ".join(w.capitalize() for w in n.split())
    ]

    if title_case:
        return min(title_case, key=len)

    return min(names, key=len)


##############################################################################
# CLEAN ALIASES
##############################################################################

def clean_aliases(aliases):

    cleaned = set()

    for alias in aliases:

        alias = alias.strip()

        alias = re.sub(r"\s+", " ", alias)

        alias = alias.strip()

        if len(alias) < 3:
            continue

        cleaned.add(alias)

    return sorted(cleaned)


##############################################################################
# MERGE
##############################################################################

def merge_medicines(records):

    """
    records =

    [
        (generic, alias),
        (generic, alias)
    ]
    """

    groups = defaultdict(list)

    alias_map = defaultdict(set)

    for generic, alias in records:

        key = create_key(generic)

        groups[key].append(generic)

        alias_map[key].add(alias)

        alias_map[key].add(generic)

    database = []

    idx = 1

    for key in sorted(groups):

        generic = choose_generic(groups[key])

        aliases = clean_aliases(alias_map[key])

        database.append({

            "id": idx,

            "generic": generic,

            "brand": "",

            "aliases": aliases

        })

        idx += 1

    return database