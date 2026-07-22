import json
import re
from pathlib import Path

from rapidfuzz import process, fuzz


class MedicineMatcher:

    def __init__(self):

        dataset = Path(__file__).parent.parent / "data" / "medicines.json"

        with open(dataset, "r", encoding="utf-8") as f:
            self.medicines = json.load(f)

        self.lookup = []

        for medicine in self.medicines:

            # Generic name
            generic = medicine.get("generic", "").strip()

            if generic:
                self.lookup.append((generic.lower(), medicine))

            # Brand name
            brand = medicine.get("brand", "").strip()

            if brand:
                self.lookup.append((brand.lower(), medicine))

            # Aliases
            for alias in medicine.get("aliases", []):

                alias = alias.strip()

                if alias:
                    self.lookup.append((alias.lower(), medicine))

    @staticmethod
    def normalize(text: str):

        text = text.lower()

        text = re.sub(r"[^a-z0-9\s\-]", " ", text)

        text = re.sub(r"\s+", " ", text)

        return text.strip()

    def match(self, text: str, threshold=75):

        text = self.normalize(text)

        choices = [item[0] for item in self.lookup]

        results = process.extract(
            text,
            choices,
            scorer=fuzz.WRatio,
            limit=5,
        )

        matches = []

        seen = set()

        for matched_text, score, idx in results:

            if score < threshold:
                continue

            medicine = self.lookup[idx][1]

            key = medicine["generic"]

            if key in seen:
                continue

            seen.add(key)

            matches.append(
                {
                    "generic": medicine["generic"],
                    "brand": medicine["brand"],
                    "confidence": round(score, 2),
                }
            )

        return matches