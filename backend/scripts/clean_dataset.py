"""
Final Medicine Dataset Cleaner

Pipeline:

merged.json
      ↓
normalize_medicine()
      ↓
validate()
      ↓
merge_medicines()
      ↓
cleaned.json
"""

import json
from pathlib import Path

from normalizer import normalize_medicine
from validator import validate
from merger import merge_medicines


# ---------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "processed" / "merged.json"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "cleaned.json"


# ---------------------------------------------------------------------
# LOAD
# ---------------------------------------------------------------------

print("=" * 60)
print("Loading merged dataset...")

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    raw_data = json.load(f)

print(f"Loaded {len(raw_data)} entries.\n")


# ---------------------------------------------------------------------
# PROCESS
# ---------------------------------------------------------------------

processed = []

accepted = 0
rejected = 0

for item in raw_data:

    # ---------------------------------------------------------
    # Get medicine name
    # ---------------------------------------------------------

    if isinstance(item, dict):

        name = (
            item.get("name")
            or item.get("medicine")
            or item.get("generic")
            or item.get("drug")
            or ""
        )

    else:
        name = str(item)

    name = name.strip()

    if not name:
        rejected += 1
        continue

    # ---------------------------------------------------------
    # Normalize
    # ---------------------------------------------------------

    generic, alias = normalize_medicine(name)

    if generic is None:
        rejected += 1
        continue

    # ---------------------------------------------------------
    # Validate
    # ---------------------------------------------------------

    if not validate(generic):
        rejected += 1
        continue

    processed.append((generic, alias))

    accepted += 1


# ---------------------------------------------------------------------
# MERGE
# ---------------------------------------------------------------------

print("Merging aliases...")

database = merge_medicines(processed)


# ---------------------------------------------------------------------
# SORT
# ---------------------------------------------------------------------

database = sorted(
    database,
    key=lambda x: x["generic"].lower()
)


# ---------------------------------------------------------------------
# REASSIGN IDS
# ---------------------------------------------------------------------

for i, med in enumerate(database, start=1):
    med["id"] = i


# ---------------------------------------------------------------------
# SAVE
# ---------------------------------------------------------------------

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(database, f, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------
# STATS
# ---------------------------------------------------------------------

print("\n" + "=" * 60)

print("Cleaning completed successfully!\n")

print(f"Original entries      : {len(raw_data)}")
print(f"Accepted              : {accepted}")
print(f"Rejected              : {rejected}")
print(f"Unique medicines      : {len(database)}")

duplicates = accepted - len(database)

print(f"Merged duplicates     : {duplicates}")

print("\nOutput written to:")
print(OUTPUT_FILE)

print("=" * 60)