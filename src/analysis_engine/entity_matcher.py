"""Entity matching and RAG retrieval module."""
import re
from typing import List, Dict, Any, Optional, Tuple
from src.utils.logger import get_logger
from src.utils.vector_db import get_vector_store, VectorDBInterface

logger = get_logger(__name__)


class EntityMatcher:
    """Matches entities in text with knowledge base."""
    
    def __init__(self, vector_store: Optional[VectorDBInterface] = None):
        """
        Initialize entity matcher.
        
        Args:
            vector_store: Vector database instance for RAG
        """
        self.vector_store = vector_store
        logger.info("EntityMatcher initialized")
    
    def extract_ticker_mentions(self, text: str) -> List[Tuple[str, int]]:
        """
        Extract ticker mentions from text.
        
        Args:
            text: Input text
            
        Returns:
            List of (ticker, confidence) tuples
        """
        # Pattern for standard tickers
        ticker_pattern = r'\b([A-Z][A-Z0-9]{0,4}(?:\.TW|\.US)?)\b'
        matches = re.findall(ticker_pattern, text)
        
        # Remove duplicates while preserving order
        seen = set()
        tickers = []
        for match in matches:
            if match not in seen:
                tickers.append((match, 0.9))  # High confidence for explicit tickers
                seen.add(match)
        
        logger.info(f"Extracted {len(tickers)} unique tickers")
        return tickers
    
    def extract_company_mentions(self, text: str) -> List[Tuple[str, int]]:
        """
        Extract company name mentions from text.
        
        Args:
            text: Input text
            
        Returns:
            List of (company_name, confidence) tuples
        """
        # Common company patterns in Chinese
        company_pattern = r'([\u4e00-\u9fff]{2,6}(?:科技|電子|股份|公司)?)'
        matches = re.findall(company_pattern, text)
        
        companies = [(m, 0.7) for m in set(matches) if len(m) >= 2]
        logger.info(f"Extracted {len(companies)} company mentions")
        return companies
    
    def match_with_knowledge_base(
        self,
        entities: List[str],
        entity_type: str = "ticker",
        top_k: int = 3,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Match entities with knowledge base using RAG.
        
        Args:
            entities: List of entity names
            entity_type: Type of entity ('ticker' or 'company')
            top_k: Number of results to retrieve
            
        Returns:
            Dict mapping entity to list of matching knowledge
        """
        results = {}
        
        if not self.vector_store:
            logger.warning("Vector store not configured, skipping RAG")
            return results
        
        try:
            for entity in entities:
                query = f"{entity_type}: {entity}"
                matches = self.vector_store.query(
                    query_text=query,
                    collection_name=entity_type,
                    top_k=top_k,
                )
                results[entity] = matches
            
            logger.info(f"Matched {len(results)} entities with knowledge base")
            return results
        
        except Exception as e:
            logger.error(f"Error in knowledge base matching: {e}")
            return results
    
    def enrich_ticker_with_context(
        self,
        ticker: str,
        text: str,
    ) -> Dict[str, Any]:
        """
        Enrich ticker with contextual information from text.
        
        Args:
            ticker: Ticker symbol
            text: Full text content
            
        Returns:
            Dict with enriched ticker information
        """
        # Extract sentences mentioning ticker
        sentences = re.split(r'[。！？\n]+', text)
        context_sentences = [s for s in sentences if ticker.lower() in s.lower()]
        
        enriched = {
            "ticker": ticker,
            "mention_count": len(context_sentences),
            "context": " ".join(context_sentences[:3]),  # First 3 mentions
            "confidence": min(1.0, len(context_sentences) * 0.2),  # Higher confidence for repeated mentions
        }
        
        return enriched
    
    def get_related_tickers(
        self,
        primary_ticker: str,
        text: str,
    ) -> List[str]:
        """
        Find tickers mentioned in relation to primary ticker.
        
        Args:
            primary_ticker: Primary ticker of interest
            text: Text content
            
        Returns:
            List of related ticker symbols
        """
        # Find paragraphs mentioning primary ticker
        sentences = re.split(r'[。！？\n]+', text)
        relevant_paras = [s for s in sentences if primary_ticker.lower() in s.lower()]
        
        related_text = " ".join(relevant_paras)
        all_tickers = self.extract_ticker_mentions(related_text)
        
        # Remove primary ticker
        related = [t[0] for t in all_tickers if t[0] != primary_ticker]
        
        return related


class RAGRetriever:
    """Retrieves relevant documents from vector database for context."""
    
    def __init__(self, vector_store: Optional[VectorDBInterface] = None):
        """
        Initialize RAG retriever.
        
        Args:
            vector_store: Vector database instance
        """
        self.vector_store = vector_store or get_vector_store()
        logger.info("RAGRetriever initialized")
    
    def retrieve_ticker_context(
        self,
        ticker: str,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve context for a specific ticker.
        
        Args:
            ticker: Ticker symbol
            top_k: Number of results
            
        Returns:
            List of relevant documents
        """
        try:
            query = f"Stock ticker: {ticker}. Current situation, fundamentals, and outlook."
            results = self.vector_store.query(
                query_text=query,
                collection_name="tickers",
                top_k=top_k,
            )
            logger.info(f"Retrieved {len(results)} documents for {ticker}")
            return results
        except Exception as e:
            logger.error(f"Error retrieving ticker context: {e}")
            return []
    
    def retrieve_industry_context(
        self,
        industry: str,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve context for a specific industry.
        
        Args:
            industry: Industry name
            top_k: Number of results
            
        Returns:
            List of relevant documents
        """
        try:
            query = f"Industry: {industry}. Trends, growth drivers, and challenges."
            results = self.vector_store.query(
                query_text=query,
                collection_name="industries",
                top_k=top_k,
            )
            logger.info(f"Retrieved {len(results)} documents for {industry}")
            return results
        except Exception as e:
            logger.error(f"Error retrieving industry context: {e}")
            return []
    
    def retrieve_macro_context(self, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieve macro-level context.
        
        Args:
            top_k: Number of results
            
        Returns:
            List of relevant documents
        """
        try:
            query = "Macro economic outlook, interest rates, inflation, global market trends."
            results = self.vector_store.query(
                query_text=query,
                collection_name="macro",
                top_k=top_k,
            )
            logger.info(f"Retrieved {len(results)} macro documents")
            return results
        except Exception as e:
            logger.error(f"Error retrieving macro context: {e}")
            return []
