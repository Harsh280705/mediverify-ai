import json
import re
from pathlib import Path

import pandas as pd

# ----------------------------------------------------
# Paths
# ----------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

CSV_PATH = BASE_DIR / "data" / "raw" / "jan_aushadhi.csv"
OUTPUT_PATH = BASE_DIR / "data" / "extracted" / "jan.json"

# ----------------------------------------------------
# Load CSV
# ----------------------------------------------------

df = pd.read_csv(CSV_PATH)

medicine_names = set()

# ----------------------------------------------------
# Words to remove
# ----------------------------------------------------

REMOVE_WORDS = [
    "Tablets",
    "Tablet",
    "Capsules",
    "Capsule",
    "Injection",
    "Injections",
    "Syrup",
    "Suspension",
    "Cream",
    "Gel",
    "Ointment",
    "Drops",
    "Lotion",
    "Powder",
    "Solution",
    "Respules",
    "Rotacaps",
    "Inhaler",
    "Nasal Spray",
    "Eye Drops",
    "Ear Drops",
    "IP",
    "USP",
    "BP",
]

# ----------------------------------------------------
# Extract medicines
# ----------------------------------------------------

for item in df["Generic Name"].dropna():

    med = str(item).strip()

    # remove dosage forms
    for word in REMOVE_WORDS:
        med = re.sub(rf"\b{re.escape(word)}\b", "", med, flags=re.IGNORECASE)

    # remove strengths
    med = re.sub(r"\d+(\.\d+)?\s?(mg|mcg|g|kg|ml|IU|%)", "", med, flags=re.IGNORECASE)

    # remove brackets
    med = re.sub(r"\(.*?\)", "", med)

    # normalize "and" to +
    med = med.replace(" and ", " + ")

    # remove commas
    med = med.replace(",", " + ")

    # normalize spaces
    med = re.sub(r"\s+", " ", med)

    med = med.strip(" +-")

    if len(med) < 3:
        continue

    medicine_names.add(med)

# ----------------------------------------------------
# Save
# ----------------------------------------------------

medicine_list = sorted(medicine_names)

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(medicine_list, f, indent=2, ensure_ascii=False)

print(f"Extracted {len(medicine_list)} Jan Aushadhi medicines")