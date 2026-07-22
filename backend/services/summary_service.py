import httpx
import logging
from firebase.firebase_admin import get_firestore_client
from config.settings import get_settings

logger = logging.getLogger(__name__)

class SummaryService:
    def __init__(self):
        self.settings = get_settings()
        self._db = None

    @property
    def db(self):
        if self._db is None:
            self._db = get_firestore_client()
        return self._db

    async def get_or_generate_summary(self, medicine_name: str, strength: str = "", dosage: str = "", instructions: str = "", timing: str = "") -> str:
        """
        Retrieves cached summary from Firestore, or generates a new one using Ollama and caches it.
        """
        if not medicine_name:
            return ""

        normalized_name = medicine_name.strip().lower()
        
        # 1. Check cache in Firestore
        try:
            cache_ref = self.db.collection("summaries_cache").document(normalized_name)
            doc = cache_ref.get()
            if doc.exists:
                logger.info(f"Summary cache hit for: {medicine_name}")
                return doc.to_dict().get("summary", "")
        except Exception as e:
            logger.error(f"Firestore summary cache read error: {e}")

        # 2. Cache miss, generate using Ollama
        logger.info(f"Summary cache miss for: {medicine_name}. Generating with Ollama...")
        
        prompt = (
            f"You are a helpful AI medication assistant. Generate a brief, warm, easy-to-understand medication summary "
            f"for an elderly patient. Summarize the medication: {medicine_name}.\n"
            f"Strength: {strength or 'as prescribed'}\n"
            f"Dosage: {dosage or 'as prescribed'}\n"
            f"Prescription Instructions: {instructions or 'as prescribed'}\n"
            f"Scheduled Timing: {timing or 'as prescribed'}\n\n"
            "Format the summary as a direct, friendly instruction in 3-4 simple lines. Avoid chemical jargon. "
            "Use the exact example structure:\n"
            f"\"This is {medicine_name}.\n"
            "It is used to reduce pain and inflammation.\n"
            "Today's prescription is one tablet after breakfast.\n"
            "Avoid taking it on an empty stomach.\"\n\n"
            "Generate ONLY the summary text, do not include introduction, markdown wrappers, backticks, or explanation."
        )

        url = f"{self.settings.ollama_base_url.rstrip('/')}/api/generate"
        payload = {
            "model": self.settings.ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3
            }
        }

        summary = ""
        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                res_data = response.json()
                summary = res_data.get("response", "").strip()
        except Exception as exc:
            logger.error(f"Error calling Ollama for medication summary: {exc}")
            # Fallback summary in case Ollama is offline
            summary = (
                f"This is {medicine_name} ({strength or 'Prescribed dose'}).\n"
                f"It is used to help manage your health symptoms.\n"
                f"Take it {timing or 'as scheduled'} - {instructions or 'follow instructions'}.\n"
                "Please consult your doctor if you experience any side effects."
            )

        # 3. Store in Firestore Cache
        try:
            from datetime import datetime, timezone
            cache_ref.set({
                "medicineName": medicine_name,
                "summary": summary,
                "generatedAt": datetime.now(timezone.utc)
            }, merge=True)
        except Exception as e:
            logger.error(f"Failed to cache summary in Firestore: {e}")

        return summary
