import streamlit as st
import time
import datetime
from output_generation import output_generation
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from models_name import rag_models


st.set_page_config(page_title="Chatbot - PDF Q&A", page_icon="💬", layout="wide")


st.markdown("""
<style>
    /* Dark theme base styling */
    .stApp {
        background-color: #121212;
        color: #e0e0e0;
    }
    
    /* Container styles */
    .chat-container {
        border-radius: 10px;
        margin-bottom: 16px;
        padding: 12px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.3);
    }
    
    /* User message styling */
    .user-container {
        background-color: #2d3748;
        border-left: 4px solid #6366f1;
           
            justify-content:flex-end;
                width: 50%;
    float: right;
    height: auto;
    min-height: 100px;
    }
    
    /* Assistant message styling */
    .assistant-container {
        background-color: #1a202c;
        border-left: 4px solid #38b2ac;
          
            justify-content:flex-start;
                width: 50%;
    float: left;
    height: auto;
    min-height: 100px;
    }
    
    /* Header for chat messages */
    .chat-header {
       
        justify-content: space-between;
        margin-bottom: 8px;
        font-size: 0.85em;
        color: #a0aec0;
        font-weight: 500;
    }
    
    /* Time display */
    .chat-time {
        text-align: right;
    }
    
    /* Message content */
    .chat-content {
        padding: 5px;
        color: #e2e8f0;
        line-height: 1.5;
    }
    
    /* Response time indicator */
    .response-time {
        font-size: 0.75em;
        color: #718096;
        text-align: right;
        font-style: italic;
        margin-top: 6px;
    }
    
    /* Title styling */
    h1 {
        color: #e2e8f0;
        text-align: center;
        margin-bottom: 32px;
        padding-top: 16px;
    }
    
    /* Sidebar styling */
    .css-6qob1r {
        background-color: #1a202c;
    }
    
    /* Adjust input field for dark mode */
    .stTextInput>div>div>input {
        background-color: #2d3748;
        color: #e2e8f0;
    }
    
    /* Style for links in dark mode */
    a {
        color: #63b3ed !important;
    }
    
    /* Streamlit elements overrides for dark mode */
    .stButton>button {
        background-color: #4a5568;
        color: #e2e8f0;
    }
    
    .stSelectbox>div>div {
        background-color: #2d3748;
        color: #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)


st.markdown("<h1>📄 PDF Q&A Chatbot</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## About")
    st.markdown("Ask questions about your uploaded PDF documents.")
    st.markdown("---")
    st.markdown("## Settings")
    
    
    # Model selection dropdown with default value
    if 'selected_model' not in st.session_state:
        st.session_state.selected_model = "gemini-2.0-pro-exp" 

    selected_model = st.selectbox(
        "Select Model:",
        options=rag_models,
        index=rag_models.index(st.session_state.selected_model)
    )
    
    
    if selected_model != st.session_state.selected_model:
        st.session_state.selected_model = selected_model



if "messages" not in st.session_state:
    st.session_state.messages = []


chat_container = st.container()


def get_loading_html(timestamp):
    return f"""
    <div class="chat-container assistant-container">
        <div class="chat-header">
            <div><strong>Assistant</strong></div>
            <div class="chat-time">{timestamp}</div>
        </div>
        <div class="chat-content">Generating response...</div>
    </div>
    """

# Display chat history with enhanced styling and fixed markdown for better rendering
with chat_container:
    for msg in st.session_state.messages:
        container_class = "user-container" if msg["role"] == "user" else "assistant-container"
        response_time_html = f'<div class="response-time">Response time: {msg.get("response_time", "N/A")}</div>' if msg["role"] == "assistant" and "response_time" in msg else ""
        
        st.markdown(f"""
        <div class="chat-container {container_class}">
            <div class="chat-header">
                <div><strong>{"You" if msg["role"] == "user" else "Assistant"}</strong></div>
                <div class="chat-time">{msg.get("time", "")}</div>
            </div>
            <div class="chat-content">{msg["content"]}</div>
            {response_time_html}
        </div>
        """, unsafe_allow_html=True)


query = st.chat_input("Ask a question about your PDF...")

if query:
 
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    
 
    st.session_state.messages.append({
        "role": "user", 
        "content": query,
        "time": current_time
    })
    
    with chat_container:
        st.markdown(f"""
        <div class="chat-container user-container">
            <div class="chat-header">
                <div><strong>You</strong></div>
                <div class="chat-time">{current_time}</div>
            </div>
            <div class="chat-content">{query}</div>
        </div>
        """, unsafe_allow_html=True)
    

    if "embedding_model" not in st.session_state:
        with st.spinner("Loading embedding model..."):
            st.session_state.embedding_model = HuggingFaceBgeEmbeddings(model_name="models/all-MiniLM-L6-v2")
    
    
    with chat_container:
        assistant_container = st.empty()
        response_timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
       
        assistant_container.markdown(get_loading_html(response_timestamp), unsafe_allow_html=True)
        
  
        start_time = time.time()
        
      
        try:
            response_text = output_generation(query, st.session_state.embedding_model,st.session_state.selected_model)
            
            # Calculate response time
            end_time = time.time()
            response_time = f"{(end_time - start_time):.2f}s"
            
            # Update assistant message with the actual response
            assistant_container.markdown(f"""
            <div class="chat-container assistant-container">
                <div class="chat-header">
                    <div><strong>Assistant</strong></div>
                    <div class="chat-time">{response_timestamp}</div>
                </div>
                <div class="chat-content">{response_text}</div>
                <div class="response-time">Response time: {response_time}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Save assistant response to chat history
            st.session_state.messages.append({
                "role": "assistant", 
                "content": response_text,
                "time": response_timestamp,
                "response_time": response_time
            })
            
        except Exception as e:
            # Handle errors gracefully
            error_message = f"Sorry, an error occurred: {str(e)}"
            
            assistant_container.markdown(f"""
            <div class="chat-container assistant-container">
                <div class="chat-header">
                    <div><strong>Assistant</strong></div>
                    <div class="chat-time">{response_timestamp}</div>
                </div>
                <div class="chat-content">{error_message}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.session_state.messages.append({
                "role": "assistant", 
                "content": error_message,
                "time": response_timestamp
            })