from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from store_index import get_retriver
from src.helper import custom_rag
from src.prompt import *
load_dotenv()

def chat_model(model):
    llm = ChatGoogleGenerativeAI(model=model,temperature=0.6,top_k=40,top_p=0.9)
    return llm


def output_generation(query,loaded,selected_model):

 llm=chat_model(model=selected_model)
 retriver=get_retriver(loaded)
 return custom_rag(retriver,prompt,llm,query)