import re
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from langchain_community.embeddings import HuggingFaceBgeEmbeddings

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
EMBEDDING_MODEL_PATH = PROJECT_ROOT / "models" / "all-MiniLM-L6-v2"
TEMPLATES_DIR = BASE_DIR / "ui" / "templates"
STATIC_DIR = BASE_DIR / "ui" / "static"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env")

from src.models_name import get_rag_models
from src.output_generation import output_generation_small_talk, output_generation_with_sources

app = FastAPI(title="Medical RAG Assistant")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

_embedding_model = None

SMALL_TALK_RULES = {
    "greeting": {
        "patterns": [
            r"^(hi|hello|hey|hii|hola|yo)\b",
            r"\b(good morning|good afternoon|good evening)\b",
        ],
    },
    "thanks": {
        "patterns": [
            r"\b(thanks|thank you|thx|ty)\b",
        ],
    },
    "goodbye": {
        "patterns": [
            r"^(bye|goodbye|see you|cya)\b",
        ],
    },
}

MEDICAL_BOOK_KEYWORDS = {
    "medical",
    "medicine",
    "patient",
    "symptom",
    "symptoms",
    "disease",
    "diseases",
    "treatment",
    "treatments",
    "diagnosis",
    "diagnose",
    "fever",
    "pain",
    "cancer",
    "diabetes",
    "blood",
    "heart",
    "infection",
    "health",
    "book",
    "pdf",
    "gale",
    "encyclopedia",
}


def classify_query_intent(query: str) -> str:
    normalized = query.strip().lower()
    if len(normalized) <= 1:
        return "small_talk"
    for intent_config in SMALL_TALK_RULES.values():
        for pattern in intent_config["patterns"]:
            if re.search(pattern, normalized):
                return "small_talk"
    if any(keyword in normalized for keyword in MEDICAL_BOOK_KEYWORDS):
        return "rag_query"
    return "small_talk"


def get_embedding_model() -> HuggingFaceBgeEmbeddings:
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = HuggingFaceBgeEmbeddings(model_name=str(EMBEDDING_MODEL_PATH))
    return _embedding_model


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    models = get_rag_models()
    return templates.TemplateResponse("index.html", {"request": request, "models": models})


@app.get("/api/models")
async def api_models():
    return {"models": get_rag_models()}


@app.post("/api/chat")
async def api_chat(request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    query = (payload.get("query") or "").strip()
    selected_model = (payload.get("model") or "").strip()

    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    models = get_rag_models()
    if not selected_model:
        selected_model = models[0] if models else "llama-3.1-8b-instant"

    intent = classify_query_intent(query)
    started = time.time()

    try:
        if intent == "rag_query":
            result = output_generation_with_sources(
                query=query,
                loaded=get_embedding_model(),
                selected_model=selected_model,
            )
        else:
            result = output_generation_small_talk(query=query, selected_model=selected_model)

        result["response_time_seconds"] = round(time.time() - started, 2)
        result["intent"] = intent
        return JSONResponse(result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/pdf/{filename:path}")
async def serve_pdf(filename: str):
    file_path = DATA_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="PDF not found.")
    return FileResponse(path=str(file_path), media_type="application/pdf")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
