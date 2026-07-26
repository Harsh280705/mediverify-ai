import json
import re
from pathlib import Path

from rapidfuzz import process, fuzz

CUSTOM_ALIASES = {
    "paracetamol": ["crocin", "calpol", "acetaminophen", "dolo", "pacimol", "pyragesic"],
    "acetaminophen": ["paracetamol", "crocin", "calpol", "dolo"],
    "crocin": ["paracetamol", "calpol", "acetaminophen", "dolo"],
    "calpol": ["paracetamol", "crocin", "acetaminophen", "dolo"],
    "dolo": ["paracetamol", "crocin", "calpol", "acetaminophen"],
    "ibuprofen": ["advil", "motrin", "nurofen"],
    "advil": ["ibuprofen", "motrin", "nurofen"],
    "motrin": ["ibuprofen", "advil", "nurofen"],
    "aspirin": ["ecotrin", "bayer", "acetylsalicylic acid"],
    "acetylsalicylic acid": ["aspirin", "ecotrin", "bayer"],
    "atorvastatin": ["lipitor", "atorva"],
    "lipitor": ["atorvastatin", "atorva"],
    "metformin": ["glucophage", "glycomet"],
    "glucophage": ["metformin", "glycomet"],
    "amoxicillin": ["mox", "amoxil"],
    "amoxil": ["amoxicillin", "mox"],
}

def fix_ocr_numbers(text: str) -> str:
    def replace_lookalikes(match):
        val = match.group(1)
        unit = match.group(2)
        mapped = []
        for char in val:
            if char in ('o', 'O'):
                mapped.append('0')
            elif char in ('l', 'I', 'i'):
                mapped.append('1')
            elif char in ('s', 'S'):
                mapped.append('5')
            elif char in ('b', 'B') and len(val) > 1:
                mapped.append('8')
            elif char in ('z', 'Z'):
                mapped.append('2')
            else:
                mapped.append(char)
        return "".join(mapped) + " " + unit

    # Match digits + lookalikes followed by units or dosage terms
    text = re.sub(
        r'\b([0-9oOliIsSzZbbB]+)\s*(mg|mcg|ml|g|tablets?|capsules?|tabs?|caps?)\b',
        replace_lookalikes,
        text,
        flags=re.IGNORECASE
    )
    return text

def normalize_name(text: str) -> str:
    text = text.lower()
    text = fix_ocr_numbers(text)
    
    # Remove packaging metadata & patterns (batch, expiry, mfg, lic)
    text = re.sub(r'\b(?:batch\s*no\.?|b\.?\s*no\.?|b\s*no|batch)\s*[:.-]?\s*[a-z0-9]+/?[a-z0-9]*\b', ' ', text)
    text = re.sub(r'\b(?:exp\.?\s*(?:date|dt)?\.?|expiry\s*(?:date|dt)?\.?|mfg\.?\s*(?:date|dt)?\.?|mfd\.?)\s*[:.-]?\s*\d{2}[-/]\d{2,4}\b', ' ', text)
    text = re.sub(r'\b(?:lic\.?\s*no\.?|mfg\s*lic\s*no\.?|l\.?\s*no\.?)\s*[:.-]?\s*[a-z0-9/]+\b', ' ', text)
    
    # Remove manufacturer names and pharma suffixes
    manufacturers = [
        "cipla", "gsk", "pfizer", "abbott", "torrent", "lupin", "cadila", "glenmark", "sun pharma", 
        "ranbaxy", "dr reddy", "alkem", "wockhardt", "glaxosmithkline", "novartis", "sanofi", 
        "aurobindo", "intas", "biocon", "limited", "ltd", "pvt", "lab", "laboratories", "pharma", "pharmaceuticals"
    ]
    for m in manufacturers:
        text = re.sub(rf'\b{m}\b', ' ', text)
        
    # Remove standards and symbols
    text = re.sub(r'[®™©]', ' ', text)
    text = re.sub(r'\b(?:ip|bp|usp)\b', ' ', text)
    
    # Remove Rx prefix
    text = re.sub(r'\brx\b', ' ', text)
    
    # Remove strengths (e.g. 500mg, 500 mg, 10ml, etc.)
    text = re.sub(r'\b\d+(?:\.\d+)?\s*(?:mg|mcg|g|ml|iu)\b', ' ', text)
    
    # Remove dosage forms
    dosage_forms = [
        "tablets", "tablet", "capsules", "capsule", "softgels", "softgel", "syrups", "syrup", 
        "suspensions", "suspension", "injections", "injection", "drops", "drop", "ointments", 
        "ointment", "oint", "caps", "cap", "tabs", "tab", "syp", "inj"
    ]
    for df in dosage_forms:
        text = re.sub(rf'\b{df}\b', ' ', text)
        
    # Clean non-alphanumeric (except space)
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    
    # Clean extra spaces
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    # Remove duplicate adjacent words
    words = text.split()
    unique_words = []
    for w in words:
        if not unique_words or unique_words[-1] != w:
            unique_words.append(w)
    text = " ".join(unique_words)
    
    return text

def extract_strength_and_form(text: str) -> tuple:
    text = text.lower()
    text = fix_ocr_numbers(text)
    
    # 1. Extract strength
    strength_match = re.search(r'\b(\d+(?:\.\d+)?\s*(?:mg|mcg|g|ml|iu))\b', text)
    strength = strength_match.group(1).replace(" ", "") if strength_match else None
    
    # 2. Extract dosage form
    form = None
    dosage_forms_map = {
        "tablet": ["tablets", "tablet", "tabs", "tab"],
        "capsule": ["capsules", "capsule", "softgels", "softgel", "caps", "cap"],
        "syrup": ["syrups", "syrup", "suspensions", "suspension", "syp"],
        "injection": ["injections", "injection", "inj"],
        "drops": ["drops", "drop"],
        "ointment": ["ointments", "ointment", "oint"]
    }
    for canonical_form, aliases in dosage_forms_map.items():
        for alias in aliases:
            if re.search(rf'\b{alias}\b', text):
                form = canonical_form
                break
        if form:
            break
            
    return strength, form


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
        return normalize_name(text)

    def match(self, text: str, threshold=75):
        norm_text = normalize_name(text)
        if not norm_text:
            return []

        # 1. Check CUSTOM_ALIASES
        custom_synonyms = []
        for alias_key, syns in CUSTOM_ALIASES.items():
            if norm_text == alias_key or norm_text in syns:
                custom_synonyms.append(alias_key)
                custom_synonyms.extend(syns)
                break

        matches = []
        seen = set()

        # If we have custom synonyms, retrieve database entries for them first
        if custom_synonyms:
            for syn in custom_synonyms:
                for name, med in self.lookup:
                    if name == syn:
                        key = med["generic"]
                        if key not in seen:
                            seen.add(key)
                            matches.append({
                                "generic": med["generic"],
                                "brand": med["brand"],
                                "confidence": 100.0
                            })

        # Standard fuzzy search
        choices = [item[0] for item in self.lookup]
        results = process.extract(
            norm_text,
            choices,
            scorer=fuzz.WRatio,
            limit=5,
        )

        for matched_text, score, idx in results:
            if score < threshold:
                continue

            medicine = self.lookup[idx][1]
            key = medicine["generic"]
            if key in seen:
                continue

            seen.add(key)
            matches.append({
                "generic": medicine["generic"],
                "brand": medicine["brand"],
                "confidence": round(score, 2),
            })

        return matches

    def calculate_match_confidence(self, ocr_lines: list[str], expected_name: str, expected_strength: str | None = None, expected_dosage: str | None = None) -> float:
        expected_name_norm = normalize_name(expected_name)
        expected_strength_norm = expected_strength.lower().replace(" ", "") if expected_strength else None
        
        _, expected_form = extract_strength_and_form(f"{expected_name} {expected_dosage or ''}")
        
        # 1. Resolve candidates for expected_name
        candidates = set()
        if expected_name_norm:
            candidates.add(expected_name_norm)
            
        custom_synonyms = []
        for alias_key, syns in CUSTOM_ALIASES.items():
            if expected_name_norm == alias_key or expected_name_norm in syns:
                custom_synonyms.append(alias_key)
                custom_synonyms.extend(syns)
                break
                
        if custom_synonyms:
            candidates.update(custom_synonyms)
            for syn in custom_synonyms:
                for name, med in self.lookup:
                    if name == syn:
                        candidates.add(normalize_name(med.get("generic", "")))
                        candidates.add(normalize_name(med.get("brand", "")))
                        for alias in med.get("aliases", []):
                            candidates.add(normalize_name(alias))
        else:
            db_matches = self.match(expected_name, threshold=70)
            for m in db_matches:
                for med in self.medicines:
                    if med.get("generic") == m.get("generic"):
                        candidates.add(normalize_name(med.get("generic", "")))
                        candidates.add(normalize_name(med.get("brand", "")))
                        for alias in med.get("aliases", []):
                            candidates.add(normalize_name(alias))
                        break
                        
        candidates = {c for c in candidates if c}
        if not candidates:
            return 0.0
            
        best_overall_confidence = 0.0
        
        for line in ocr_lines:
            line_name_norm = normalize_name(line)
            if not line_name_norm:
                continue
                
            line_strength, line_form = extract_strength_and_form(line)
            
            for candidate in candidates:
                # Stage 1: Exact match
                if line_name_norm == candidate:
                    name_score = 100.0
                # Stage 3: Substring matches
                elif len(line_name_norm) > 4 and len(candidate) > 4 and (line_name_norm in candidate or candidate in line_name_norm):
                    name_score = 90.0
                # Stage 4: RapidFuzz similarity
                else:
                    name_score = fuzz.WRatio(line_name_norm, candidate)
                    
                if name_score < 70.0:
                    continue
                    
                if candidate == expected_name_norm:
                    type_multiplier = 1.0
                elif expected_name_norm in CUSTOM_ALIASES and candidate in CUSTOM_ALIASES[expected_name_norm]:
                    type_multiplier = 0.95
                else:
                    type_multiplier = 0.90
                    
                base_confidence = name_score * type_multiplier
                
                # Strength comparison (Stage 7)
                strength_score = 1.0
                strength_bonus = 0.0
                
                if expected_strength_norm:
                    if line_strength:
                        if line_strength == expected_strength_norm:
                            strength_bonus = 5.0
                        else:
                            strength_score = 0.1  # Mismatch penalty
                    else:
                        strength_score = 0.9  # Missing strength slight penalty
                        
                # Dosage form comparison (Stage 7)
                form_score = 1.0
                if expected_form:
                    if line_form:
                        if line_form == expected_form:
                            strength_bonus += 2.0
                        else:
                            form_score = 0.8
                            
                total_conf = (base_confidence * strength_score * form_score) + strength_bonus
                total_conf = min(100.0, max(0.0, total_conf))
                
                if total_conf > best_overall_confidence:
                    best_overall_confidence = total_conf
                    
        # Apply Ollama interpretation confidence
        is_in_db = False
        if expected_name_norm:
            for name, _ in self.lookup:
                if name == expected_name_norm:
                    is_in_db = True
                    break
        ollama_factor = 1.0 if is_in_db else 0.8
        
        final_conf = best_overall_confidence * ollama_factor
        return round(final_conf, 2)