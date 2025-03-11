# import google.generativeai as genai
# import os
# from dotenv import load_dotenv

# load_dotenv()

# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# genai.configure(api_key=GOOGLE_API_KEY)


# models = genai.list_models()
# for model in models:
#     print(model.name)



# from langchain_google_genai import ChatGoogleGenerativeAI
# from dotenv import load_dotenv

# load_dotenv()


# llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-002")
# print(llm.invoke("Write me a ballad about LangChain"))


from src.helper import download_huggingface_embedding

embedding_model=download_huggingface_embedding()