import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")

# Set them in os.environ for libraries that use them this way
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY

from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langgraph.checkpoint.memory import MemorySaver
from langchain.schema import Document
from langchain.chains import RetrievalQA
from langchain_community.tools.tavily_search import TavilySearchResults  
from langgraph.graph import END, Graph, START
import pinecone
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from pydantic import BaseModel, Field
import warnings
warnings.filterwarnings("ignore")

print("Environment variables loaded and set.")

def load_pdf(data: str) -> List[Document]:
    """Load PDF documents from a directory."""
    print(f"PDF loading is starting from directory: {data}")
    abs_path = os.path.abspath(data)
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"Directory not found: '{abs_path}'")
    print(f"Loading PDFs from: {abs_path}")
    loader = DirectoryLoader(abs_path, glob="*.pdf", loader_cls=PyPDFLoader)
    documents = loader.load()
    print(f"Found {len(documents)} documents")
    return documents

def process_documents(documents: List[Document]) -> List[Document]:
    """Split documents into smaller chunks."""
    print("PDF loading is done and processing is started.")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(documents)
    return splits

def initialize_vectorstore() -> PineconeVectorStore:
    """Initialize and populate Pinecone vectorstore."""
    print("Initializing Pinecone vectorstore...")
    pc = Pinecone(api_key=PINECONE_API_KEY)
    print("Connecting to existing Pinecone vectorstore...")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    return PineconeVectorStore(index_name="medical-chatbot", embedding=embeddings)

class State(BaseModel):
    """Represents the state of our application."""
    query: str
    context: List[Document] = Field(default_factory=list)
    web_results: List[dict] = Field(default_factory=list)
    response: Optional[str] = None
    vectorstore: Optional[PineconeVectorStore] = None

    class Config:
        arbitrary_types_allowed = True

def retriever_tool(state: State) -> State:
    """Tool for retrieving relevant context from Pinecone."""
    vectorstore = state.vectorstore
    results = vectorstore.similarity_search(state.query, k=3)
    state.context.extend(results)
    print("Retriever tool completed. Results:", results)
    return state

def web_search_tool(state: State) -> State:
    """Tool for performing web searches using Tavily."""
    search = TavilySearchResults()
    results = search.invoke(state.query)
    state.web_results.extend(results)
    print("Web search tool completed.")
    return state

def generate_response(state: State) -> State:
    """Generate final response using Gemini."""
    llm = GoogleGenerativeAI(model="gemini-1.5-flash")
    context_text = "\n".join([doc.page_content for doc in state.context])
    web_text = "\n".join([str(result) for result in state.web_results])

    prompt = f"""You are a medical assistant. Using the following information, provide a clear and comprehensive answer about {state.query}

    Context from medical documents:
    {context_text}

    Additional information from web:
    {web_text}

    Based on this information, please provide a clear, organized explanation about {state.query}. 
    If the context contains relevant information, use it to explain. Focus on providing accurate medical information."""

    try:
        state.response = llm.invoke(prompt)
        print("Response generated successfully.")
    except Exception as e:
        print(f"Error generating response: {e}")
        state.response = "Sorry, I encountered an error generating the response."
    return state

def create_graph() -> Graph:
    """Create the LangGraph workflow."""
    print("Creating graph...")
    workflow = Graph()
    workflow.add_node("retriever", retriever_tool)
    workflow.add_node("web_search", web_search_tool)
    workflow.add_node("generate", generate_response)

    workflow.add_edge(START, "retriever")
    workflow.add_edge("retriever", "web_search")
    workflow.add_edge("web_search", "generate")
    workflow.add_edge("generate", END)

    print("Graph created.")
    return workflow.compile()

class ChatBot:
    def __init__(self):
        self.vectorstore = initialize_vectorstore()
        self.graph = create_graph()

    def ask(self, query: str) -> str:
        initial_state = State(query=query, vectorstore=self.vectorstore)
        config = {'configurable': {'thread_id': '1'}}
        print("Invoking query...")
        final_state = self.graph.invoke(initial_state)
        return final_state.response

def main():
    try:
        chatbot = ChatBot()
        query = "can you tell me any medicine for eye allergy?"
        print(f"\nProcessing query: {query}")
        response = chatbot.ask(query)
        print(f"\nResponse: {response}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    print("Chatbot module loaded successfully.")
    main()
