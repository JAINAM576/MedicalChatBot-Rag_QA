from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv
from src.helper import load_extract_pdf, document_to_chunks,download_huggingface_embedding

import os



load_dotenv()

pdf_path="Data/Gale Encyclopedia of Medicine Vol. 1 (A-B).pdf"
dir_path="Data/"

PINECONE_API_KEY=os.environ.get("PINECONE_API_KEY")
os.environ["PINECONE_API_KEY"]=PINECONE_API_KEY

def make_db(index_name,dir_path,run):
    if not run : return 
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index_name = index_name


    pc.create_index(
        name=index_name,
        dimension=384, 
        metric="cosine", 
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        ) 
    )


    extracted_data=load_extract_pdf(dir_path)
    chunks=document_to_chunks(extracted_data)
    embedding_model=download_huggingface_embedding()


    docsearch=PineconeVectorStore.from_documents(
        index_name=index_name,
        documents=chunks,
        embedding=embedding_model
    )
    return {
        "index_name":index_name,
        "embedding_model":embedding_model
    }

index_name="medibotembed"
db_info=make_db(index_name,dir_path,False)


def get_retriver(loaded):

    docretrival=PineconeVectorStore.from_existing_index(
        index_name=index_name,
        embedding=loaded
    )
    reteriver=docretrival.as_retriever(search_type="similarity",search_kwargs={"k":3})
    return reteriver


