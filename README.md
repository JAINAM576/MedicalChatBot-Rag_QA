# 🏥 Medical Chatbot using RAG (Retrieval-Augmented Generation)

**Project Demo:** https://jainam576-medicalchatbot-app-oerd0x.streamlit.app/


## 📌 Overview
Welcome to the **Medical Chatbot**, an AI-powered system designed to provide medical-related answers using **Retrieval-Augmented Generation (RAG)**. This chatbot utilizes **LangChain, Pinecone, and Google Gemini AI** to retrieve relevant medical information and generate responses.

🔹 **What makes this chatbot special?**
- Uses the **Gale Encyclopedia of Medicine Vol. 1 (A-B)** as a **knowledge base**.
- Retrieves **relevant medical content** using **vector embeddings**.
- Generates responses with **Google Gemini AI**.
- Provides a **clean & interactive user interface** using **Streamlit**.

## 📂 Project Structure
```
📁 MedicalChatBot-Rag_QA/
├── 📜 README.md             # Project documentation
├── 🏗️ app.py                # Streamlit web application
├── 📜 requirements.txt      # Python dependencies
├── 📁 data/                 # Data source (Medical PDF, gitignored)
├── 📁 models/               # Pretrained embedding model (gitignored)
├── 📁 research/
│   └── 📓 trial.ipynb       # Experimentation notebook
├── 📁 backend/
│   ├── 🚀 main.py           # FastAPI application
│   └── 📁 ui/               # HTML templates & static assets
└── 📁 src/                  # Core package
    ├── 📌 __init__.py
    ├── 🛠️ helper.py          # PDF loading, chunking & embedding utilities
    ├── 🗂️ prompt.py          # System prompt & chat templates
    ├── ⚙️ output_generation.py # LLM response generation
    ├── 📌 models_name.py     # Groq model listing
    └── 📌 store_index.py     # Pinecone vector store & retrieval
```

---

## 🚀 How It Works
### Step 1️⃣: **Building the Knowledge Base**
📖 The chatbot is trained on **"Gale Encyclopedia of Medicine Vol. 1 (A-B).pdf"**, which contains **637 pages** of medical information.
- Extracts text using **LangChain's DirectoryLoader & PyPDFLoader**.
- Splits text into **chunks of 500 words with 30-word overlap**.

### Step 2️⃣: **Embedding & Indexing**
🤖 **Vector Search for Fast Retrieval!**
- Loads **all-MiniLM-L6-v2**, a **sentence transformer model from Hugging Face**.
- Converts text chunks into **numerical embeddings**.
- Stores embeddings in **Pinecone**, a high-performance vector database.
- 📊 **Total embeddings stored:** **5876**

### Step 3️⃣: **Retrieval & LLM Response Generation**
🔍 **How does the chatbot retrieve & respond?**
1. Retrieves **top 5 most relevant chunks** using **cosine similarity**.
2. Formats retrieved chunks into a **system prompt**.
3. Passes the **user query + context** to **Google Gemini AI**.
4. Generates a **human-like medical response**.

### Step 4️⃣: **Modular Implementation**
🛠️ **Code Organization for Reusability**
- `helper.py` → Functions for document processing, embedding & retrieval.
- `prompt.py` → System prompts & chat templates.
- `store_index.py` → Handles **vector storage & retrieval**.
- `output_generation.py` → **LLM invocation with user queries**.
- `models_name.py` → **List of Gemini models**.

### Step 5️⃣: **User Interaction with Streamlit**
🎨 **A Clean & Interactive UI!**
- `app.py` → Web interface built with **Streamlit**.
- Users can **select a Gemini model** from the dropdown.
- Calls `output_generation.py` to process queries & display results.

---

## 📥 Installation & Setup
### 1️⃣ **Create Conda Environment**
```bash
conda create --name medicalchatbot python=3.10.16
conda activate medicalchatbot
```

### 2️⃣ **Install Dependencies**
📦 **Using pip**
```bash
pip install -r requirements.txt
```


### 3️⃣ **Run the Streamlit Chatbot**
🚀 **Launch the Streamlit Interface**
```bash
streamlit run app.py
```

### 4️⃣ **Run the FastAPI Chatbot (New UI)**
🚀 **Launch the FastAPI Interface**
```bash
uvicorn backend.main:app --reload
```

#### FastAPI UI Features
- Minimalistic chat interface with model selector
- Real-time "thinking" status while generating answers
- Response time per answer
- Source cards with PDF name, page number, and evidence snippet
- Clickable source links to open PDF at the source page
- Copy response and clear chat actions

---

---

## 👨‍💻 Developer Information
**Created by:** Jainam Sanghavi  
💡 *Feel free to contribute or improve this project!*
