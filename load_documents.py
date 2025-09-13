import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain

load_dotenv()


gemini_key = os.getenv('GEMINI_API_KEY')


def load_docs():
    docs = []
    for n in Path("/home/henning/projects/alura-imersion/files").glob("*.pdf"):
        try:
            loader = PyMuPDFLoader(str(n))
            docs.extend(loader.load())
            print(f"Carregado arquivo {n.name}")
        except Exception as e:
            print(f"Erro {n.name}: {e}")


    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)

    chunks = splitter.split_documents(docs)
    return chunks
