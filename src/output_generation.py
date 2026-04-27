import os
from pathlib import Path
from typing import Any

from langchain_groq import ChatGroq
from dotenv import load_dotenv
from src.store_index import get_retriver
from src.helper import custom_rag
from src.prompt import prompt, small_talk_prompt

load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

def chat_model(model):
    if not GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY is missing. Add it to your .env file or set it in your environment before running the app."
        )
    llm = ChatGroq(model=model, temperature=0.6)
    return llm


def output_generation(query,loaded,selected_model):

 llm=chat_model(model=selected_model)
 retriver=get_retriver(loaded)
 return custom_rag(retriver,prompt,llm,query)


def _build_snippet(text: str, max_chars: int = 260) -> str:
    compact = " ".join((text or "").split())
    if len(compact) <= max_chars:
        return compact
    return compact[: max_chars - 3] + "..."


def _extract_page_number(metadata: dict[str, Any]) -> int | None:
    possible_keys = [
        "page",
        "page_number",
        "pageNumber",
        "pagenumber",
        "loc.pageNumber",
    ]

    for key in possible_keys:
        value = metadata.get(key)
        if isinstance(value, int):
            return value + 1 if value >= 0 else None
        if isinstance(value, float):
            if value < 0:
                return None
            return int(value) + 1
        if isinstance(value, str) and value.strip().isdigit():
            num = int(value.strip())
            return num + 1 if num >= 0 else None

    page_label = metadata.get("page_label")
    if isinstance(page_label, str) and page_label.strip().isdigit():
        return int(page_label.strip())

    source_path = str(metadata.get("source", ""))
    page_match = source_path.lower().split("page=")
    if len(page_match) > 1:
        numeric_part = "".join(ch for ch in page_match[-1] if ch.isdigit())
        if numeric_part:
            return int(numeric_part)

    return None


def _extract_sources(retrieved_docs: list[Any]) -> list[dict[str, Any]]:
    sources: list[dict[str, Any]] = []
    for idx, doc in enumerate(retrieved_docs, start=1):
        metadata = getattr(doc, "metadata", {}) or {}
        source_path = metadata.get("source", "")
        file_name = Path(source_path).name if source_path else "Unknown Source"
        page_number = _extract_page_number(metadata)

        sources.append(
            {
                "id": idx,
                "title": file_name,
                "page": page_number,
                "snippet": _build_snippet(getattr(doc, "page_content", "")),
                "source": source_path,
            }
        )
    return sources


def output_generation_with_sources(query, loaded, selected_model):
    llm = chat_model(model=selected_model)
    retriver = get_retriver(loaded)
    retrieved_docs = retriver.invoke(query)
    context_text = "\n".join([doc.page_content for doc in retrieved_docs])
    formatted_prompt = prompt.format(context=context_text, input=query)
    response = llm.invoke(formatted_prompt)

    return {
        "answer": response.content,
        "sources": _extract_sources(retrieved_docs),
        "model": selected_model,
    }


def output_generation_small_talk(query, selected_model):
    llm = chat_model(model=selected_model)
    formatted_prompt = small_talk_prompt.format_messages(input=query)
    response = llm.invoke(formatted_prompt)
    return {
        "answer": response.content,
        "sources": [],
        "model": selected_model,
    }