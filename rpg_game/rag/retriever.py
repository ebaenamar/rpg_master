import os
import json
from typing import List, Dict, Any, Optional

import chromadb
from sentence_transformers import SentenceTransformer
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

from rpg_game.config import VECTOR_DB_PATH, EMBEDDING_MODEL, RAG_TOP_K


class RAGRetriever:
    """Retrieval-Augmented Generation module for historical context"""
    
    def __init__(self, vector_db_path: str = VECTOR_DB_PATH, embedding_model: str = EMBEDDING_MODEL):
        """Initialize the RAG retriever with vector database and embedding model"""
        self.vector_db_path = vector_db_path
        
        # Create directory if it doesn't exist
        os.makedirs(vector_db_path, exist_ok=True)
        
        # Initialize embedding model
        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
        
        # Initialize or load vector database
        self._init_vector_db()
    
    def _init_vector_db(self):
        """Initialize or load the vector database"""
        try:
            self.vectordb = Chroma(
                persist_directory=self.vector_db_path,
                embedding_function=self.embeddings
            )
            print(f"Loaded vector database with {self.vectordb._collection.count()} documents")
        except Exception as e:
            print(f"Creating new vector database: {e}")
            self.vectordb = Chroma(
                embedding_function=self.embeddings,
                persist_directory=self.vector_db_path
            )
    
    def add_documents(self, documents: List[Dict[str, Any]]):
        """Add historical documents to the vector database
        
        Args:
            documents: List of document dictionaries with 'title', 'text', and 'tags' keys
        """
        langchain_docs = []
        
        for doc in documents:
            langchain_docs.append(
                Document(
                    page_content=doc["text"],
                    metadata={
                        "title": doc["title"],
                        "tags": ",".join(doc.get("tags", [])),
                    }
                )
            )
        
        self.vectordb.add_documents(langchain_docs)
        self.vectordb.persist()
        print(f"Added {len(documents)} documents to vector database")
    
    def retrieve(self, query: str, top_k: int = RAG_TOP_K, filter_tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Retrieve relevant historical context based on the query
        
        Args:
            query: The search query related to the current scene
            top_k: Number of relevant passages to retrieve
            filter_tags: Optional list of tags to filter results
            
        Returns:
            List of relevant historical context documents
        """
        # Prepare filter if tags are provided
        filter_dict = None
        if filter_tags:
            # Use $in operator which is supported by ChromaDB
            # We'll search for any document that has at least one of the tags
            filter_dict = {"tags": {"$in": filter_tags}}
        
        # Retrieve documents
        docs = self.vectordb.similarity_search(
            query=query,
            k=top_k,
            filter=filter_dict
        )
        
        # Format results
        results = []
        for doc in docs:
            tags = doc.metadata.get("tags", "").split(",") if doc.metadata.get("tags") else []
            results.append({
                "title": doc.metadata.get("title", "Unknown"),
                "text": doc.page_content,
                "tags": tags
            })
        
        return results


# Helper function to load sample historical data
def load_sample_data(file_path: str) -> List[Dict[str, Any]]:
    """Load sample historical data from a JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading sample data: {e}")
        return []
