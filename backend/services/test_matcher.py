from services.medicine_matcher import MedicineMatcher

matcher = MedicineMatcher()

tests = [
    "Paracetmol",
    "Crocin",
    "Abacavir",
    "Allex Px",
    "Mex Sc0",
]

for word in tests:

    print("\nOCR :", word)

    matches = matcher.match(word)

    for m in matches:

        print(m)