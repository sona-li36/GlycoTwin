import os
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq

# Ensure environment variables are loaded so API keys are present
load_dotenv()

# 1. Setup Models
# We use a local embedding model (free) and Groq for the LLM
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
llm = Groq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))

# Configure global settings so LlamaIndex doesn't try to use OpenAI defaults
Settings.llm = llm
Settings.embed_model = embed_model

# Define where the data lives and where the index will be saved
DATA_DIR = "./Data of GLP"
PERSIST_DIR = "./storage"

def get_clinical_index():
    """
    Loads existing index or creates a new one from the 'Data of GLP' folder.
    Provides detailed logs on how many documents were indexed.
    """
    if not os.path.exists(PERSIST_DIR):
        print(f"🔍 Scanning folder: {DATA_DIR}...")
        
        # Load all PDFs and documents from your folder
        documents = SimpleDirectoryReader(DATA_DIR).load_data()
        
        print(f"📚 RAG has successfully found {len(documents)} document pages from your research.")
        print("Indexing research papers... this may take a minute.")
        
        # Create the vector index
        index = VectorStoreIndex.from_documents(
            documents, 
            embed_model=embed_model
        )
        
        # Save it to the /storage folder so we don't have to re-index every time
        index.storage_context.persist(persist_dir=PERSIST_DIR)
        print("✅ New research index created and saved to /storage.")
    else:
        # Load the existing index from the storage folder
        print("✅ Loading existing research index from /storage...")
        storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
        index = load_index_from_storage(storage_context, embed_model=embed_model)
    
    return index

def query_knowledge_base(query_str: str):
    """
    Searches the research papers and returns a medically grounded answer.
    """
    index = get_clinical_index()
    
    # Configure the engine to act as a Clinical Researcher
    # similarity_top_k=3 means it looks at the 3 most relevant sections of your PDFs
    query_engine = index.as_query_engine(llm=llm, similarity_top_k=3)
    
    response = query_engine.query(query_str)
    return str(response)