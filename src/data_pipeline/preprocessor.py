"""Text preprocessing and jargon normalization."""
import re
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from src.utils.logger import get_logger
from src.utils.data_models import PreprocessedContent, TranscriptionResult

logger = get_logger(__name__)


class JargonMapper:
    """Maps financial jargon to standardized ticker names."""
    
    def __init__(self, mapping_file: str = "config/jargon_mapping.yaml"):
        """
        Initialize jargon mapper.
        
        Args:
            mapping_file: Path to jargon mapping YAML file
        """
        self.mappings = {}
        self._load_mappings(mapping_file)
    
    def _load_mappings(self, mapping_file: str) -> None:
        """Load mappings from YAML file."""
        try:
            with open(mapping_file, 'r', encoding='utf-8') as f:
                self.mappings = yaml.safe_load(f) or {}
            logger.info(f"Loaded jargon mappings from {mapping_file}")
        except Exception as e:
            logger.warning(f"Error loading jargon mappings: {e}")
            self.mappings = {}
    
    def get_ticker(self, jargon: str) -> Optional[str]:
        """
        Get ticker symbol for jargon term.
        
        Args:
            jargon: Jargon term
            
        Returns:
            Ticker symbol or None
        """
        # Search in Taiwan stocks
        tw_stocks = self.mappings.get('台灣股票', {})
        if jargon in tw_stocks:
            return tw_stocks[jargon].get('ticker')
        
        # Search in US stocks
        us_stocks = self.mappings.get('美股', {})
        if jargon in us_stocks:
            return us_stocks[jargon].get('ticker')
        
        # Search aliases
        for category in [tw_stocks, us_stocks]:
            for key, value in category.items():
                aliases = value.get('aliases', [])
                if jargon in aliases:
                    return value.get('ticker')
        
        return None
    
    def normalize_text(self, text: str) -> Tuple[str, Dict[str, str]]:
        """
        Normalize text by replacing jargon with standard ticker names.
        
        Args:
            text: Input text
            
        Returns:
            Tuple of (normalized_text, applied_mappings)
        """
        normalized_text = text
        applied_mappings = {}
        
        # Get all possible jargon terms
        all_terms = set()
        for category in self.mappings.values():
            if isinstance(category, dict):
                all_terms.update(category.keys())
                for value in category.values():
                    if isinstance(value, dict):
                        all_terms.update(value.get('aliases', []))
        
        # Sort by length (longest first) to avoid partial replacements
        sorted_terms = sorted(all_terms, key=len, reverse=True)
        
        # Replace jargon in text
        for term in sorted_terms:
            ticker = self.get_ticker(term)
            if ticker and term in text:
                pattern = re.compile(r'\b' + re.escape(term) + r'\b', re.IGNORECASE)
                if pattern.search(normalized_text):
                    replacement = f"{term}({ticker})"
                    normalized_text = pattern.sub(replacement, normalized_text)
                    applied_mappings[term] = ticker
        
        return normalized_text, applied_mappings


class TextPreprocessor:
    """Preprocesses transcribed text for analysis."""
    
    def __init__(self, jargon_mapper: Optional[JargonMapper] = None):
        """
        Initialize preprocessor.
        
        Args:
            jargon_mapper: JargonMapper instance for normalization
        """
        self.jargon_mapper = jargon_mapper or JargonMapper()
    
    def clean_text(self, text: str) -> str:
        """
        Clean text (remove extra spaces, fix encoding issues, etc.).
        
        Args:
            text: Input text
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove common OCR artifacts
        text = re.sub(r'[^\w\s\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff()-]', '', text)
        
        return text
    
    def segment_sentences(self, text: str) -> List[str]:
        """
        Segment text into sentences.
        
        Args:
            text: Input text
            
        Returns:
            List of sentences
        """
        # Simple sentence segmentation for Chinese/English mix
        sentences = re.split(r'[。！？\n]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def create_chunks(self, text: str, chunk_size: int = 300, overlap: int = 50) -> List[str]:
        """
        Create overlapping text chunks for RAG.
        
        Args:
            text: Input text
            chunk_size: Characters per chunk
            overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
        
        return chunks
    
    def extract_entities(self, text: str) -> List[str]:
        """
        Extract named entities (simple regex-based).
        
        Args:
            text: Input text
            
        Returns:
            List of detected entities (tickers, company names, etc.)
        """
        entities = set()
        
        # Look for ticker patterns (e.g., 2330.TW, NVDA)
        ticker_pattern = r'\b[A-Z][A-Z0-9]{0,4}(?:\.TW|\.US)?\b'
        entities.update(re.findall(ticker_pattern, text))
        
        # Look for jargon terms
        all_terms = set()
        for category in self.jargon_mapper.mappings.values():
            if isinstance(category, dict):
                all_terms.update(category.keys())
        
        for term in all_terms:
            if term in text:
                entities.add(term)
        
        return list(entities)
    
    def preprocess(
        self,
        transcription: TranscriptionResult,
        chunk_size: int = 300,
    ) -> PreprocessedContent:
        """
        Full preprocessing pipeline.
        
        Args:
            transcription: TranscriptionResult from transcriber
            chunk_size: Size of text chunks
            
        Returns:
            PreprocessedContent
        """
        try:
            # Step 1: Clean text
            cleaned_text = self.clean_text(transcription.transcript)
            
            # Step 2: Normalize jargon
            normalized_text, jargon_mappings = self.jargon_mapper.normalize_text(cleaned_text)
            
            # Step 3: Create chunks
            chunks = self.create_chunks(normalized_text, chunk_size=chunk_size)
            
            # Step 4: Extract entities
            entities = self.extract_entities(normalized_text)
            
            result = PreprocessedContent(
                transcription_id=transcription.source_id,
                normalized_text=normalized_text,
                jargon_mappings=jargon_mappings,
                chunks=chunks,
                entities_detected=entities,
            )
            
            logger.info(f"Preprocessed content for {transcription.source_id}: "
                       f"{len(chunks)} chunks, {len(entities)} entities")
            return result
        
        except Exception as e:
            logger.error(f"Error preprocessing transcription: {e}")
            raise


class DataPipeline:
    """Complete data pipeline from audio to preprocessed content."""
    
    def __init__(
        self,
        youtube_fetcher=None,
        podcast_fetcher=None,
        transcriber=None,
        preprocessor=None,
    ):
        """Initialize data pipeline with components."""
        self.youtube_fetcher = youtube_fetcher
        self.podcast_fetcher = podcast_fetcher
        self.transcriber = transcriber
        self.preprocessor = preprocessor or TextPreprocessor()
    
    def process_audio_file(
        self,
        audio_path: str,
        source_id: str,
        source_type: str = "youtube",
        source_title: str = "",
        source_url: Optional[str] = None,
    ) -> Optional[PreprocessedContent]:
        """
        Process a single audio file through the full pipeline.
        
        Args:
            audio_path: Path to audio file
            source_id: Unique source identifier
            source_type: Type of source
            source_title: Title of source
            source_url: URL of source
            
        Returns:
            PreprocessedContent or None if failed
        """
        try:
            if not self.transcriber:
                logger.error("Transcriber not configured")
                return None
            
            # Transcribe
            transcription = self.transcriber.transcribe_to_result(
                audio_path=audio_path,
                source_id=source_id,
                source_type=source_type,
                source_title=source_title,
                source_url=source_url,
            )
            
            if not transcription:
                return None
            
            # Preprocess
            preprocessed = self.preprocessor.preprocess(transcription)
            
            logger.info(f"Successfully processed {source_id} through full pipeline")
            return preprocessed
        
        except Exception as e:
            logger.error(f"Error in data pipeline: {e}")
            return None
