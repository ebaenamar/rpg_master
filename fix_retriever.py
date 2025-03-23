import os
import sys
from typing import List, Dict, Any, Optional

# This function will be used to monkey patch the RAGRetriever.retrieve method
def fixed_retrieve(self, query: str, top_k: int = 3, filter_tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Retrieve relevant historical context based on the query
    
    Args:
        query: The search query related to the current scene
        top_k: Number of relevant passages to retrieve
        filter_tags: Optional list of tags to filter results
        
    Returns:
        List of relevant historical context documents
    """
    try:
        # Prepare filter if tags are provided
        filter_dict = None
        
        # Only use filter if we have tags
        if filter_tags and len(filter_tags) > 0:
            # Convert all tags to strings to avoid type issues
            string_tags = [str(tag).strip() for tag in filter_tags if tag]
            
            if string_tags:
                # Use $in operator which is supported by ChromaDB
                filter_dict = {"tags": {"$in": string_tags}}
        
        # Retrieve documents - without filter if filter_dict is None
        if filter_dict:
            print(f"Searching with filter: {filter_dict}")
            docs = self.vectordb.similarity_search(
                query=query,
                k=top_k,
                filter=filter_dict
            )
        else:
            # If no valid filter, search without filter
            print("Searching without filter")
            docs = self.vectordb.similarity_search(
                query=query,
                k=top_k
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
        
    except Exception as e:
        print(f"Error in RAG retrieval: {e}")
        return []

print("Add this code to your Jupyter notebook:")
print("\n" + "=" * 80 + "\n")
print("# Fix the RAGRetriever.retrieve method to use $in instead of $contains")
print("from rpg_game.rag.retriever import RAGRetriever")
print("from fix_retriever import fixed_retrieve")
print("# Monkey patch the retrieve method")
print("RAGRetriever.retrieve = fixed_retrieve")
print("print('✅ RAGRetriever.retrieve method has been fixed')")
print("\n" + "=" * 80 + "\n")
print("Run this cell before starting the game.")
