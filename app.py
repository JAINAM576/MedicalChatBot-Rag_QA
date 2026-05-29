import re
import time
import datetime

import streamlit as st
from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceBgeEmbeddings

import os
from src.models_name import get_rag_models
from src.output_generation import output_generation_with_sources, output_generation_small_talk
from src.helper import get_pdf_page_text, get_pdf_page_image

load_dotenv()

EMBEDDING_MODEL_PATH = "models/all-MiniLM-L6-v2"

SMALL_TALK_PATTERNS = [
    r"^(hi|hello|hey|hii|hola|yo)\b",
    r"\b(good morning|good afternoon|good evening)\b",
    r"\b(thanks|thank you|thx|ty)\b",
    r"^(bye|goodbye|see you|cya)\b",
]
MEDICAL_KEYWORDS = {
    "medical", "medicine", "patient", "symptom", "symptoms", "disease",
    "diseases", "treatment", "treatments", "diagnosis", "diagnose", "fever",
    "pain", "cancer", "diabetes", "blood", "heart", "infection", "health",
    "book", "pdf", "gale", "encyclopedia",
}


def classify_intent(query: str) -> str:
    normalized = query.strip().lower()
    if len(normalized) <= 1:
        return "small_talk"
    for pattern in SMALL_TALK_PATTERNS:
        if re.search(pattern, normalized):
            return "small_talk"
    if any(kw in normalized for kw in MEDICAL_KEYWORDS):
        return "rag_query"
    return "small_talk"


@st.cache_resource(show_spinner="Loading embedding model...")
def load_embedding_model():
    return HuggingFaceBgeEmbeddings(model_name=EMBEDDING_MODEL_PATH)


def render_sources_section(sources, expanded=False, key_prefix=""):
    with st.expander(f"📚 Sources ({len(sources)} chunks retrieved)", expanded=expanded):
        for idx, src in enumerate(sources):
            # Normalize path separators to handle Windows paths in metadata when running on Linux
            clean_title = src['title'].replace('\\', '/').split('/')[-1]
            page_num = src.get("page")
            page_label = f"Page {page_num}" if page_num else "Page N/A"
            st.markdown(f"##### Chunk {idx + 1}: **{clean_title}** · `{page_label}`")
            
            tab1, tab2, tab3 = st.tabs(["📝 Snippet", "📖 Full Page Text", "🖼️ Original PDF Page"])
            
            # Resolve correct path based on OS case-sensitivity (Data vs data)
            pdf_path = os.path.join("Data", clean_title)
            if not os.path.exists(pdf_path):
                pdf_path = os.path.join("data", clean_title)
            
            with tab1:
                st.caption("Retrieved matching chunk used to answer the question:")
                st.markdown(f"*{src.get('snippet', '')}*")
                
            with tab2:
                if page_num:
                    if os.path.exists(pdf_path):
                        with st.spinner("Extracting page text..."):
                            full_text = get_pdf_page_text(pdf_path, page_num)
                        st.markdown("**Complete Page Text:**")
                        st.text_area(
                            label="Page Text",
                            value=full_text,
                            height=250,
                            disabled=True,
                            label_visibility="collapsed",
                            key=f"{key_prefix}_text_{idx}_{page_num}"
                        )
                    else:
                        st.error(f"PDF file not found at: `{pdf_path}`")
                else:
                    st.warning("No page number metadata available for this source.")
                    
            with tab3:
                if page_num:
                    if os.path.exists(pdf_path):
                        with st.spinner("Rendering PDF page..."):
                            img_bytes = get_pdf_page_image(pdf_path, page_num)
                        if img_bytes:
                            st.image(
                                img_bytes,
                                caption=f"Page {page_num} of {clean_title}",
                                use_container_width=True
                            )
                        else:
                            st.error("Failed to render the PDF page. Ensure the page number is valid.")
                    else:
                        st.error(f"PDF file not found at: `{pdf_path}`")
                else:
                    st.warning("No page number metadata available for this source.")
            st.divider()


st.set_page_config(page_title="Medical RAG Assistant", page_icon="🏥", layout="wide")

st.title("🏥 Medical RAG Assistant")
st.caption("Ask evidence-grounded questions from the Gale Encyclopedia of Medicine.")

with st.sidebar:
    st.header("⚙️ Settings")

    rag_models = get_rag_models()
    selected_model = st.selectbox("Groq Model", options=rag_models)

    st.divider()
    st.markdown("**Knowledge Base**")
    st.markdown("📖 Gale Encyclopedia of Medicine Vol. 1 (A–B)")
    st.markdown("🗂️ ~5876 chunks · 384-dim embeddings · Pinecone")

    st.divider()
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg_idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            render_sources_section(msg["sources"], expanded=False, key_prefix=f"hist_{msg_idx}")
        if msg.get("meta"):
            st.caption(msg["meta"])

query = st.chat_input("Ask a medical question from the PDF...")

if query:
    ts = datetime.datetime.now().strftime("%H:%M")
    st.session_state.messages.append({"role": "user", "content": query})

    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Retrieving context and generating answer..."):
            embedding_model = load_embedding_model()
            intent = classify_intent(query)
            start = time.time()

            try:
                if intent == "rag_query":
                    result = output_generation_with_sources(query, embedding_model, selected_model)
                else:
                    result = output_generation_small_talk(query, selected_model)

                elapsed = round(time.time() - start, 2)
                answer = result["answer"]
                sources = result.get("sources", [])
                meta = f"🤖 {result.get('model', selected_model)}  ·  ⏱️ {elapsed}s  ·  🔍 {intent.replace('_', ' ')}"

                st.markdown(answer)

                if sources:
                    render_sources_section(sources, expanded=True, key_prefix="new_response")

                st.caption(meta)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                    "meta": meta,
                })

            except Exception as e:
                err = f"⚠️ Error: {e}"
                st.error(err)
                st.session_state.messages.append({"role": "assistant", "content": err})
