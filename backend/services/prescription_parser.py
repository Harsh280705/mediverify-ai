import re
from services.medicine_matcher import MedicineMatcher

class PrescriptionParser:
    MEDICINE_TYPES = {
        "tab":"Tablet","tablet":"Tablet",
        "cap":"Capsule","capsule":"Capsule",
        "syp":"Syrup","syrup":"Syrup",
        "inj":"Injection","injection":"Injection",
        "drop":"Drops","drops":"Drops",
        "ointment":"Ointment","oint":"Ointment",
    }

    def __init__(self):
        self.matcher = MedicineMatcher()

    def _ignore_line(self, line):
        l=line.lower()
        junk=["(tot","total","qty","address","phone","timing","timning","reg:","mmc","closed:"]
        return any(j in l for j in junk)

    def _extract_medicine_type(self,line):
        l=line.lower()
        for k,v in self.MEDICINE_TYPES.items():
            if re.search(rf"\b{re.escape(k)}\b",l):
                return v
        return None

    def _extract_strength(self,text):
        m=re.search(r"(\d+(?:\.\d+)?)\s*(mg|mcg|g|ml|iu)",text,re.I)
        return m.group(0) if m else None

    def _extract_duration(self,text):
        m=re.search(r"(\d+)\s*(day|days|week|weeks|month|months)",text,re.I)
        return int(m.group(1)) if m else None

    def _extract_schedule(self,text):
        l=text.lower()
        return {
            "morning":"morning" in l,
            "afternoon":"afternoon" in l,
            "evening":"evening" in l,
            "night":"night" in l
        }

    def _extract_meal(self,text):
        l=text.lower()
        if "before food" in l: return "Before Food"
        if "after food" in l: return "After Food"
        if "empty stomach" in l: return "Empty Stomach"
        return None

    def _clean_name(self,line):
        line=re.sub(r"^\d+\)\s*","",line)
        line=re.sub(r"^(tab|tablet|cap|capsule|syp|syrup|inj|injection|drops?|ointment)[\s\.:,-]*","",line,flags=re.I)
        return line.strip()

    def parse(self,text):
        prescription={
            "doctor":None,
            "hospital":None,
            "patient_name":None,
            "age":None,
            "gender":None,
            "date":None,
            "diagnosis":None,
            "follow_up":None,
            "advice":[],
            "medicines":[]
        }

        current=None
        advice=False
        lines=[l.strip() for l in text.splitlines() if l.strip()]

        for i,line in enumerate(lines):
            lower=line.lower()

            if lower.startswith("dr"):
                prescription["doctor"]=line
                continue

            if prescription["hospital"] is None and "hospital" in lower:
                prescription["hospital"]=line

            d=re.search(r"\d{1,2}[-/][A-Za-z]+[-/]\d{2,4}",line)
            if d:
                if prescription["date"] is None:
                    prescription["date"]=d.group()
                else:
                    prescription["follow_up"]=d.group()

            if "diagnosis" in lower and i+1<len(lines):
                prescription["diagnosis"]=lines[i+1]

            if lower.startswith("advice"):
                advice=True
                continue

            if advice:
                if lower.startswith("follow up"):
                    advice=False
                else:
                    prescription["advice"].append(line)
                    continue

            if self._ignore_line(line):
                continue

            if re.match(r"^\d+\)",line) or any(k in lower for k in self.MEDICINE_TYPES):
                med=self._clean_name(line)
                current={
                    "ocr_name":med,
                    "matched":self.matcher.match(med),
                    "type":self._extract_medicine_type(line),
                    "strength":self._extract_strength(line),
                    "schedule":{"morning":False,"afternoon":False,"evening":False,"night":False},
                    "meal":None,
                    "duration_days":None
                }
                prescription["medicines"].append(current)
                continue

            if current:
                s=self._extract_schedule(line)
                if any(s.values()):
                    current["schedule"]=s
                meal=self._extract_meal(line)
                if meal:
                    current["meal"]=meal
                dur=self._extract_duration(line)
                if dur:
                    current["duration_days"]=dur
                st=self._extract_strength(line)
                if st and current["strength"] is None:
                    current["strength"]=st

        return prescription
