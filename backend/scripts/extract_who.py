import fitz
import re
import json
from pathlib import Path

# ---------------------------------------------------
# Paths
# ---------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

PDF_PATH = BASE_DIR / "data" / "raw" / "who.pdf"
OUTPUT_DIR = BASE_DIR / "data" / "extracted"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PATH = OUTPUT_DIR / "who_raw.json"

# ---------------------------------------------------
# Dosage keywords
# ---------------------------------------------------

DOSAGE_KEYWORDS = (
    "Tablet",
    "Capsule",
    "Injection",
    "Oral",
    "Powder",
    "Solution",
    "Suspension",
    "Cream",
    "Ointment",
    "Gel",
    "Drops",
    "Patch",
    "Spray",
    "Granules",
    "Implant",
    "Suppository",
    "Lozenge",
    "Dental cartridge",
    "Inhalation",
    "Topical",
    "Solid oral dosage form",
    "Injectable solution",
    "Parenteral solution",
    "Vaginal tablet",
    "Eye drops",
    "Nasal spray",
    "Chewing gum"
)

medicine_names = set()

doc = fitz.open(str(PDF_PATH))

for page in doc:

    lines = [l.strip() for l in page.get_text().split("\n")]

    for i in range(len(lines) - 1):

        current = lines[i]
        nxt = lines[i + 1]

        if not current:
            continue

        current = current.replace("", "").replace("−", "").strip()

        if current.startswith("-"):
            current = current[1:].strip()

        if len(current) < 2:
            continue

        # Skip headings
        if current.isupper():
            continue

        if re.match(r"^\d", current):
            continue

        # Skip explanations
        if len(current.split()) > 8:
            continue

        # Next line must describe dosage form
        if not nxt.startswith(DOSAGE_KEYWORDS):
            continue

        medicine_names.add(current)

# ---------------------------------------------------
# Add therapeutic alternatives
# ---------------------------------------------------

for page in doc:

    text = page.get_text()

    for line in text.split("\n"):

        line = line.strip()

        if not line.startswith("-"):
            continue

        line = line[1:].strip()

        if len(line) < 2:
            continue

        if "ATC" in line:
            continue

        if "for " in line.lower():
            continue

        if len(line.split()) > 6:
            continue

        medicine_names.add(line)

# ---------------------------------------------------
# Final cleaning
# ---------------------------------------------------

REMOVE = {
    "Complementary List",
    "Therapeutic alternatives",
    "WHO Model List of Essential Medicines",
    "page",
}

cleaned = []

for med in sorted(medicine_names):

    med = med.strip()

    if med in REMOVE:
        continue

    med = re.sub(r"\s+", " ", med)

    cleaned.append(med)

# ---------------------------------------------------
# Save
# ---------------------------------------------------

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(cleaned, f, indent=2, ensure_ascii=False)

print(f"Extracted {len(cleaned)} medicine names")