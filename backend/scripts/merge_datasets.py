import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

FILES = [
    BASE_DIR / "data/extracted/who_raw.json",
    BASE_DIR / "data/extracted/jan.json",
    BASE_DIR / "data/extracted/cdsco.json",
]

merged = []

for file in FILES:
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)

        if isinstance(data, list):
            merged.extend(data)

OUTPUT = BASE_DIR / "data/processed/merged.json"
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(merged, f, indent=2, ensure_ascii=False)

print("Merged:", len(merged))