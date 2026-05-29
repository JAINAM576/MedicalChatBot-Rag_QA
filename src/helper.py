#importing libraries



from langchain_community.document_loaders import PyPDFLoader,DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from  langchain_community.embeddings import HuggingFaceBgeEmbeddings
import pandas as pd
import os



# load and extract document(tex) from pdf

def load_extract_pdf(path):
    loader=DirectoryLoader(path,glob="*.pdf",loader_cls=PyPDFLoader)
    document=loader.load()
    return document


# anaylse each page of pdf
def analyse_pages(extracted_data):
    data={"character_count":[],"words_len":[],"sentances_len":[],"token_count":[]}
    for i in extracted_data:
        page_data=i.page_content
    
        data["character_count"].append(len(page_data))
        data["words_len"].append(len(page_data.split(" ")))
        data["sentances_len"].append(len(page_data.split(".")))
        data["token_count"].append(len(page_data)/4)

    return data
        
        


# convert documents into chunks ! chunk_size=500 and chunk_overlay=30

def document_to_chunks(extracted_data):
    text_splitter=RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=30)
    chunks=text_splitter.split_documents(extracted_data)
    return chunks


# download hugging face embedding 
def download_huggingface_embedding(local_path="models/all-MiniLM-L6-v2"):
    
    if not os.path.exists(local_path):
        print("🔄 Model not found locally. Downloading...")
        embeddings = HuggingFaceBgeEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        embeddings.client.save_pretrained(local_path)  
        print("✅ Model downloaded and saved at:", local_path)
    else:
        print("✅ Loading model from local storage:", local_path)
        embeddings = HuggingFaceBgeEmbeddings(model_name=local_path) 

    return embeddings




def custom_rag(reteriver,prompt,llm,query):
    retrived_document=reteriver.invoke(query)
    # print(f"retrived similiar documents : {retrived_document}")
    context_text = "\n".join([doc.page_content for doc in retrived_document])
    formatted_prompt=prompt.format(context=context_text,input=query)
    response=llm.invoke(formatted_prompt)
    return response.content


def get_pdf_page_text(pdf_path: str, page_num_1based: int) -> str:
    """Extract full text of a specific page from a PDF file."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(pdf_path)
        if page_num_1based < 1 or page_num_1based > len(reader.pages):
            return f"Invalid page number {page_num_1based}. The document has {len(reader.pages)} pages."
        page = reader.pages[page_num_1based - 1]
        return page.extract_text() or "No text could be extracted from this page."
    except Exception as e:
        return f"Error extracting page: {e}"


def get_pdf_page_image(pdf_path: str, page_num_1based: int) -> bytes | None:
    try:
        import fitz  
        doc = fitz.open(pdf_path)
        if page_num_1based < 1 or page_num_1based > len(doc):
            print(f"⚠️ Page {page_num_1based} is out of range for {pdf_path} (length {len(doc)}).")
            return None
        page = doc.load_page(page_num_1based - 1)
        pix = page.get_pixmap(dpi=150)
        return pix.tobytes("png")
    except Exception as e:
        import traceback
        print(f"⚠️ Error rendering PDF page image: {e}")
        traceback.print_exc()
        return None

