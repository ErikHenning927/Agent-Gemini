from load_documents import load_docs
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
import os
from dotenv import load_dotenv


load_dotenv()

gemini_key = os.getenv('GEMINI_API_KEY')

chunks = load_docs()
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=gemini_key
)


vectorstore = FAISS.from_documents(chunks, embeddings)
retriever = vectorstore.as_retriever(
                                search_type="similarity_score_threshold", 
                                search_kwargs={"score_threshold": 0.3, "k": 4}
                            )