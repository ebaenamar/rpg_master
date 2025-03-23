import os
import json
from typing import List, Dict, Any, Optional

# Import required libraries for RAG
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

class RAGHelper:
    """Helper class for RAG functionality in the RPG game"""
    
    def __init__(self, vector_db_path: str = "./data/vector_db"):
        """Initialize the RAG helper"""
        self.vector_db_path = vector_db_path
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.vector_store = None
        
        # Create data directory if it doesn't exist
        os.makedirs(vector_db_path, exist_ok=True)
    
    def load_historical_data(self, file_path: str) -> List[Dict[str, Any]]:
        """Load historical data from a JSON file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"Error loading historical data: {e}")
            return []
    
    def create_documents(self, historical_data: List[Dict[str, Any]]) -> List[Document]:
        """Convert historical data to Document objects for vectorization"""
        documents = []
        for item in historical_data:
            content = f"{item['title']}: {item['text']}"
            metadata = {
                "source": item.get('source', 'historical_data'),
                "category": item.get('category', 'general'),
                "year": item.get('year', 'unknown'),
                "title": item['title']
            }
            documents.append(Document(page_content=content, metadata=metadata))
        return documents
    
    def initialize_vector_store(self, documents: List[Document]) -> None:
        """Initialize the vector store with documents"""
        self.vector_store = FAISS.from_documents(documents, self.embeddings)
        # Save the vector store
        self.vector_store.save_local(self.vector_db_path)
        print(f"Vector store initialized with {len(documents)} documents and saved to {self.vector_db_path}")
    
    def load_vector_store(self) -> bool:
        """Load the vector store from disk"""
        try:
            self.vector_store = FAISS.load_local(self.vector_db_path, self.embeddings)
            return True
        except Exception as e:
            print(f"Error loading vector store: {e}")
            return False
    
    def setup_rag_system(self, historical_data_path: str) -> bool:
        """Set up the RAG system with historical data"""
        # Try to load existing vector store first
        if self.load_vector_store():
            print("Loaded existing vector store")
            return True
        
        # If loading fails, create a new vector store
        historical_data = self.load_historical_data(historical_data_path)
        if not historical_data:
            print("No historical data found or error loading data")
            return False
        
        documents = self.create_documents(historical_data)
        self.initialize_vector_store(documents)
        return True
    
    def retrieve_context(self, query: str, num_results: int = 3) -> List[Dict[str, Any]]:
        """Retrieve relevant historical context based on a query"""
        if not self.vector_store:
            print("Vector store not initialized")
            return []
        
        results = self.vector_store.similarity_search(query, k=num_results)
        context = []
        
        for doc in results:
            # Split the content back into title and text
            parts = doc.page_content.split(': ', 1)
            title = parts[0] if len(parts) > 1 else doc.metadata.get('title', 'Unknown')
            text = parts[1] if len(parts) > 1 else doc.page_content
            
            context.append({
                "title": title,
                "text": text,
                "source": doc.metadata.get('source', 'historical_data'),
                "category": doc.metadata.get('category', 'general'),
                "year": doc.metadata.get('year', 'unknown')
            })
        
        return context

# Helper function to use in the notebook
def setup_rag_system(historical_data_path: str = "./data/historical_data.json") -> RAGHelper:
    """Set up the RAG system and return the helper object"""
    rag_helper = RAGHelper()
    success = rag_helper.setup_rag_system(historical_data_path)
    
    if success:
        print("RAG system successfully initialized")
    else:
        print("Failed to initialize RAG system")
    
    return rag_helper
