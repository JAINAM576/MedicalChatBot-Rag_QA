import os

import requests
from dotenv import load_dotenv

load_dotenv()

# Fallback list used when API listing is unavailable.
DEFAULT_GROQ_MODELS = [
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
    "mixtral-8x7b-32768",
]


def _is_chat_model(model_id: str) -> bool:
    blocked_keywords = ("whisper", "tts", "transcribe", "vision-preview")
    return not any(word in model_id.lower() for word in blocked_keywords)


def get_rag_models() -> list[str]:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return DEFAULT_GROQ_MODELS

    try:
        response = requests.get(
            "https://api.groq.com/openai/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=12,
        )
        response.raise_for_status()
        data = response.json().get("data", [])
        models = sorted(
            [item.get("id", "") for item in data if item.get("id") and _is_chat_model(item["id"])],
            key=str.lower,
        )
        return models or DEFAULT_GROQ_MODELS
    except Exception:
        return DEFAULT_GROQ_MODELS
