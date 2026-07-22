import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

TXT_PATH = BASE_DIR / "data" / "raw" / "cdsco.txt"
OUTPUT_PATH = BASE_DIR / "data" / "extracted" / "cdsco.json"

REMOVE_WORDS = [
    "tablet","tablets","capsule","capsules",
    "injection","injectable","inj","inj.",
    "powder","powder for injection",
    "suspension","oral suspension",
    "solution","eye drops","drops",
    "cream","ointment","gel","lotion",
    "bulk","vial","ampoule","syrup",
    "respules","rotacaps",
    "film coated","coated","enteric coated",
    "additional strength","additional indication",
    "finished formulation","finished form",
    "for injection","for oral suspension"
]

medicine_set = set()

with open(TXT_PATH, "r", encoding="utf-8", errors="ignore") as f:
    for line in f:

        line = line.strip()

        if not line:
            continue

        # Skip header
        if line.startswith("Sr.No"):
            continue

        # Remove serial number
        line = re.sub(r"^\d+\s+", "", line)

        # Keep only first column (before strength)
        parts = re.split(r"\t+", line)

        if not parts:
            continue

        drug = parts[0]

        # Remove dosage strengths
        drug = re.sub(
            r"\d+(\.\d+)?\s?(mg|mcg|g|kg|ml|IU|%)",
            "",
            drug,
            flags=re.I,
        )

        # Remove dosage-form words
        for word in REMOVE_WORDS:
            drug = re.sub(
                rf"\b{re.escape(word)}\b",
                "",
                drug,
                flags=re.I,
            )

        # Remove brackets
        drug = re.sub(r"\(.*?\)", "", drug)

        # Normalize separators
        drug = drug.replace("&", "+")
        drug = drug.replace(",", "+")

        # Normalize spaces
        drug = re.sub(r"\s+", " ", drug)

        drug = drug.strip(" +-.")

        if len(drug) < 3:
            continue

        medicine_set.add(drug)

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(sorted(medicine_set), f, indent=2, ensure_ascii=False)

print(f"Extracted {len(medicine_set)} medicines")