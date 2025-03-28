from langchain.chat_models import init_chat_model
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os

# Load and validate environment variables
load_dotenv()

#llm api key
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("GROQ_API_KEY not found in environment variables")

#embedding model api key
hf_api_key = os.getenv("HUGGINGFACE_API_KEY")
if not hf_api_key:
    raise ValueError("HUGGINGFACE_API_KEY not found in environment variables")

#LLM
model = init_chat_model("llama-3.3-70b-versatile", model_provider="groq",temperature = 0.7)

#embedding model
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Load vector store
persist_directory = r"C:\Users\panka\Desktop\document_ai_hub\data\vector_store"
if not os.path.exists(persist_directory):
    raise FileNotFoundError(f"Vector store directory not found: {persist_directory}")
vector_store = Chroma(persist_directory=persist_directory, embedding_function=embedding)
 

def query_retriever(query):
    
    """
    Retrieves top k relevant documents from the vector store based on the query.
    
    """
    retriever = vector_store.as_retriever(search_type = "similarity",search_kwargs={"k": 3})
    
    return retriever.invoke(query)



def role_based_response(query,role):
    """
    Generates a role-specific response to a query using retrieved context and an LLM.
    
    """
    retrieved_docs = query_retriever(query) 
    retrieved_text = "\n".join([doc.page_content for doc in retrieved_docs])
    
    role_based_promt = {
        "lawyer": (
            "You are an expert lawyer. Based only on the provided reference material and your legal expertise, "
            "extract key legal clauses, summarize contract terms, and provide a concise legal analysis relevant to the query. "
            "Do not provide advice or information outside the legal domain (e.g., banking or business management). "
            "If the query or reference material is unrelated to law, state that you cannot assist.\n\n"
            f"Reference:\n{retrieved_text}\n\n"
            f"Query: {query}\n\n"
            "Ensure your response is only  relevant to provided context and role-based ,if it is not available in context,just say i don't know,please ask query only related to law."
        ),
        "banker": (
            "You are a knowledgeable banker. Based exclusively on the provided reference material and your banking expertise, "
            "answer the query related to bank policies, loans, credit cards, or financial services. Provide practical advice or explanations. "
            "Do not provide advice or information outside the banking domain (e.g., legal clauses,enterprises and academic summaries). "
            "If the query or reference material is unrelated to banking, state that you cannot assist.\n\n"
            f"Reference:\n{retrieved_text}\n\n"
            f"Query: {query}\n\n"
            "Ensure your response is only  relevant to provided context and role-based,if it is not available in context,just say i don't know.Please ask query related to banking only."
        ),
        "student": (
            "You are a  student assistant. Based solely on the provided reference material and your academic skills, "
            "summarize it as if it were a research paper, highlight key points, and generate appropriate citations if applicable. "
            "Tailor the summary to the query and avoid non-academic content (e.g., legal,banking,enterprises). "
            "If the query or reference material is unrelated to academic summarization, state that you cannot assist.\n\n"
            f"Reference:\n{retrieved_text}\n\n"
            f"Query: {query}\n\n"
            "Ensure your response is only  relevant to provided context and role-based,if it is not available in context,just say i don't know.please ask query related to academics and research only."
        ),
        "enterprise": (
            "You are an expert enterprise assistant. Base  on the provided reference material and your business expertise, "
            "transcribe or interpret it as if it were meeting notes, extract actionable items or key decisions, and address the query with a business focus. "
            "Tailor the summary to the query and avoid non-bussiness content (e.g., legal,banking,academics). "
            f"Reference:\n{retrieved_text}\n\n"
            f"Query: {query}\n\n"
            "Ensure your response is only  relevant to provided context and role-based,if it is not available in context,just say i don't know the answer,please ask query related to bussiness."
        )
 }
    
    
    
    promt = role_based_promt[role]
    response = model.invoke(promt)
    return response.content
