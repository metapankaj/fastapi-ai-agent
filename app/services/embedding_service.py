from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv
import os

#load environment variables
load_dotenv()

api_key = os.getenv("HUGGINGFACE_API_KEY")
if not api_key:
    raise ValueError("HUGGINGFACE_API_KEY not found in environment variables")
os.environ["HUGGINGFACE_API_KEY"] = api_key

#embedding model
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


def embedding_vectorstore(data):
    """
    Splits text into chunks, embeds it, and stores it in a Chroma vector database.
    
    """
    data = [data]

    # Split the text into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=60)
    chunked_text = text_splitter.create_documents(data)


    print("Chunked Data:", chunked_text)

    # Storing in vector db
    vector_store = Chroma.from_documents(chunked_text, embedding, persist_directory=r"C:\Users\panka\Desktop\document_ai_hub\data\vector_store")
    
    return {"message": "Data successfully added to ChromaDB"}

