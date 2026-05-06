"""Vector database interface for RAG functionality."""
import os
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from src.utils.logger import get_logger

logger = get_logger(__name__)


class VectorDBInterface(ABC):
    """Abstract interface for vector database operations."""
    
    @abstractmethod
    def add_documents(self, documents: List[Dict[str, Any]], collection_name: str) -> bool:
        """Add documents to vector database."""
        pass
    
    @abstractmethod
    def query(self, query_text: str, collection_name: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Query vector database."""
        pass
    
    @abstractmethod
    def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection."""
        pass


class ChromaDBVectorStore(VectorDBInterface):
    """ChromaDB implementation of vector store."""
    
    def __init__(self, persist_directory: str):
        """Initialize ChromaDB client."""
        try:
            import chromadb
            self.client = chromadb.PersistentClient(path=persist_directory)
            logger.info(f"ChromaDB initialized with path: {persist_directory}")
        except ImportError:
            logger.error("chromadb not installed. Install with: pip install chromadb")
            raise
    
    def add_documents(self, documents: List[Dict[str, Any]], collection_name: str) -> bool:
        """Add documents to ChromaDB collection."""
        try:
            collection = self.client.get_or_create_collection(name=collection_name)
            
            # Extract documents and metadata
            docs = [doc.get("content", "") for doc in documents]
            metadatas = [doc.get("metadata", {}) for doc in documents]
            ids = [doc.get("id", str(i)) for i, doc in enumerate(documents)]
            
            collection.add(
                documents=docs,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(documents)} documents to {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error adding documents to {collection_name}: {e}")
            return False
    
    def query(self, query_text: str, collection_name: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Query ChromaDB collection."""
        try:
            collection = self.client.get_collection(name=collection_name)
            results = collection.query(
                query_texts=[query_text],
                n_results=top_k
            )
            
            # Format results
            formatted_results = []
            if results and results['documents']:
                for doc, meta, distance in zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                ):
                    formatted_results.append({
                        "content": doc,
                        "metadata": meta,
                        "distance": distance
                    })
            
            logger.info(f"Query returned {len(formatted_results)} results from {collection_name}")
            return formatted_results
        except Exception as e:
            logger.error(f"Error querying {collection_name}: {e}")
            return []
    
    def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection from ChromaDB."""
        try:
            self.client.delete_collection(name=collection_name)
            logger.info(f"Deleted collection: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting collection {collection_name}: {e}")
            return False


class PineconeVectorStore(VectorDBInterface):
    """Pinecone implementation of vector store."""
    
    def __init__(self, api_key: str, index_name: str):
        """Initialize Pinecone client."""
        try:
            from pinecone import Pinecone
            self.client = Pinecone(api_key=api_key)
            self.index = self.client.Index(index_name)
            logger.info(f"Pinecone initialized with index: {index_name}")
        except ImportError:
            logger.error("pinecone not installed. Install with: pip install pinecone-client")
            raise
    
    def add_documents(self, documents: List[Dict[str, Any]], collection_name: str) -> bool:
        """Add documents to Pinecone."""
        logger.warning("Pinecone add_documents not yet implemented")
        return False
    
    def query(self, query_text: str, collection_name: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Query Pinecone."""
        logger.warning("Pinecone query not yet implemented")
        return []
    
    def delete_collection(self, collection_name: str) -> bool:
        """Delete collection from Pinecone."""
        logger.warning("Pinecone delete_collection not yet implemented")
        return False


def get_vector_store(vector_db_type: str = "chromadb", **kwargs) -> VectorDBInterface:
    """Factory function to get vector store instance."""
    if vector_db_type == "chromadb":
        from config.settings import CHROMADB_PATH
        return ChromaDBVectorStore(persist_directory=str(CHROMADB_PATH))
    elif vector_db_type == "pinecone":
        from config.settings import PINECONE_API_KEY
        return PineconeVectorStore(api_key=PINECONE_API_KEY, index_name=kwargs.get("index_name", "default"))
    else:
        raise ValueError(f"Unknown vector DB type: {vector_db_type}")
