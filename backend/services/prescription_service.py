import httpx
import json
import logging
from config.settings import get_settings

logger = logging.getLogger(__name__)

class PrescriptionService:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def extract_prescription(self, raw_text: str) -> dict:
        """
        Sends raw text to Ollama and requests structured JSON extraction.
        """
        if not raw_text.strip():
            return {
                "patientName": "",
                "medications": []
            }

        prompt = (
            "Analyze the following raw OCR text extracted from a medical prescription. "
            "Extract the patient's name and all listed medications.\n\n"
            "You must return ONLY a valid JSON object matching the schema below. "
            "Do not include any intro, markdown formatting, backticks, or explanation.\n\n"
            "Required JSON Schema:\n"
            "{\n"
            '  "patientName": "Full name of the patient (string, or empty if not found)",\n'
            '  "medications": [\n'
            "    {\n"
            '      "medicineName": "Official/brand name of the medication (string, required)",\n'
            '      "strength": "Dosage/strength, e.g. 500mg, 10ml (string, or empty if not found)",\n'
            '      "frequency": "Frequency of dosage, e.g. Once daily, Twice daily, Three times a day, 1-0-1, 1-1-1 (string)",\n'
            '      "timings": ["Morning", "Afternoon", "Evening", "Night"],  # Must be a subset array of matching timings (e.g. ["Morning", "Night"] or ["Afternoon"]). Limit to Morning, Afternoon, Evening, Night.\n'
            '      "duration": "Duration of medication course, e.g. 7 days, 1 month (string, or empty if not found)",\n'
            '      "instructions": "Special administration instructions, e.g. Before food, After food (string, or empty if not found)"\n'
            "    }\n"
            "  ]\n"
            "}\n\n"
            f"Raw OCR Text:\n\"\"\"\n{raw_text}\n\"\"\"\n"
        )

        url = f"{self.settings.ollama_base_url.rstrip('/')}/api/generate"
        payload = {
            "model": self.settings.ollama_model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.0
            }
        }

        try:
            async with httpx.AsyncClient(timeout=90.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                res_data = response.json()
                response_content = res_data.get("response", "").strip()
        except Exception as exc:
            logger.error(f"Error calling Ollama API: {exc}")
            raise RuntimeError(f"Ollama integration error: {str(exc)}")

        # Parse the JSON response
        try:
            extracted_data = json.loads(response_content)
        except json.JSONDecodeError as exc:
            logger.error(f"Failed to parse Ollama response as JSON: {response_content}")
            raise ValueError(f"Failed to parse model output as valid JSON: {str(exc)}")

        # Clean and validate against the expected structure
        return self._validate_and_format(extracted_data)

    def _validate_and_format(self, data: dict) -> dict:
        """
        Validates the structure and cleans up fields to match expectations.
        """
        patient_name = str(data.get("patientName") or "").strip()
        meds = data.get("medications")
        if not isinstance(meds, list):
            meds = []

        validated_meds = []
        valid_timings = {"Morning", "Afternoon", "Evening", "Night"}

        for m in meds:
            if not isinstance(m, dict):
                continue

            medicine_name = str(m.get("medicineName") or m.get("name") or "").strip()
            if not medicine_name:
                continue

            # Parse timings
            raw_timings = m.get("timings") or []
            timings = []
            if isinstance(raw_timings, list):
                for t in raw_timings:
                    t_str = str(t).strip().capitalize()
                    if t_str in valid_timings:
                        timings.append(t_str)

            validated_meds.append({
                "medicineName": medicine_name,
                "strength": str(m.get("strength") or "").strip(),
                "frequency": str(m.get("frequency") or "").strip(),
                "timings": timings,
                "duration": str(m.get("duration") or "").strip(),
                "instructions": str(m.get("instructions") or "").strip()
            })

        return {
            "patientName": patient_name,
            "medications": validated_meds
        }
