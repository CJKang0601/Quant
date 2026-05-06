"""Sentiment analysis module."""
import re
from typing import Dict, List, Tuple, Optional
from src.utils.logger import get_logger

logger = get_logger(__name__)


class SentimentAnalyzer:
    """Analyzes sentiment in financial content."""
    
    # Positive/Negative keywords for different languages
    POSITIVE_KEYWORDS = {
        'zh': [
            '看好', '樂觀', '上升', '買進', '買入', '推薦',
            '成長', '強勢', '突破', '利多', '優勢', '領先',
            '增長', '利好', '看漲', '牛市', '暴漲',
        ],
        'en': [
            'bullish', 'positive', 'growth', 'upside', 'buy', 'strong',
            'outperform', 'surge', 'boom', 'rally', 'uptrend',
        ],
    }
    
    NEGATIVE_KEYWORDS = {
        'zh': [
            '看壞', '悲觀', '下跌', '賣出', '風險', '警告',
            '衰退', '弱勢', '崩潰', '利空', '劣勢', '落後',
            '下降', '利空', '看跌', '熊市', '暴跌',
        ],
        'en': [
            'bearish', 'negative', 'decline', 'downside', 'sell', 'weak',
            'underperform', 'crash', 'slump', 'downtrend',
        ],
    }
    
    def __init__(self):
        """Initialize sentiment analyzer."""
        logger.info("SentimentAnalyzer initialized")
    
    def analyze_text_sentiment(
        self,
        text: str,
        language: str = 'zh',
    ) -> float:
        """
        Analyze sentiment of text and return score (1-10).
        
        Args:
            text: Text to analyze
            language: Language code ('zh' or 'en')
            
        Returns:
            Sentiment score (1-10, 5.5 is neutral)
        """
        text_lower = text.lower()
        
        positive_count = sum(1 for kw in self.POSITIVE_KEYWORDS.get(language, []) if kw in text_lower)
        negative_count = sum(1 for kw in self.NEGATIVE_KEYWORDS.get(language, []) if kw in text_lower)
        
        total_keywords = positive_count + negative_count
        if total_keywords == 0:
            return 5.5  # Neutral
        
        # Calculate score (1-10 scale)
        net_sentiment = (positive_count - negative_count) / total_keywords
        score = 5.5 + (net_sentiment * 4.5)  # Range: 1-10
        
        return max(1.0, min(10.0, score))
    
    def analyze_paragraph_sentiments(
        self,
        paragraphs: List[str],
        language: str = 'zh',
    ) -> Dict[int, float]:
        """
        Analyze sentiment for multiple paragraphs.
        
        Args:
            paragraphs: List of text paragraphs
            language: Language code
            
        Returns:
            Dict mapping paragraph index to sentiment score
        """
        sentiments = {}
        for idx, paragraph in enumerate(paragraphs):
            sentiments[idx] = self.analyze_text_sentiment(paragraph, language)
        
        return sentiments
    
    def analyze_ticker_sentiment(
        self,
        text: str,
        ticker: str,
        language: str = 'zh',
    ) -> float:
        """
        Analyze sentiment for a specific ticker in text.
        
        Args:
            text: Text containing ticker mentions
            ticker: Ticker symbol to analyze
            language: Language code
            
        Returns:
            Sentiment score (1-10)
        """
        # Find sentences/paragraphs mentioning the ticker
        sentences = re.split(r'[。！？\n]+', text)
        relevant_sentences = [s for s in sentences if ticker.lower() in s.lower()]
        
        if not relevant_sentences:
            return 5.5  # Neutral if not mentioned
        
        # Combine relevant sentences
        combined_text = ' '.join(relevant_sentences)
        return self.analyze_text_sentiment(combined_text, language)
    
    def analyze_industry_sentiment(
        self,
        text: str,
        industry_name: str,
        language: str = 'zh',
    ) -> float:
        """
        Analyze sentiment for a specific industry.
        
        Args:
            text: Text containing industry mentions
            industry_name: Industry name
            language: Language code
            
        Returns:
            Sentiment score (1-10)
        """
        # Simple industry mention detection
        sentences = re.split(r'[。！？\n]+', text)
        relevant_sentences = [s for s in sentences if industry_name.lower() in s.lower()]
        
        if not relevant_sentences:
            return 5.5
        
        combined_text = ' '.join(relevant_sentences)
        return self.analyze_text_sentiment(combined_text, language)
    
    def get_sentiment_label(self, score: float) -> str:
        """
        Convert sentiment score to label.
        
        Args:
            score: Sentiment score (1-10)
            
        Returns:
            Sentiment label
        """
        if score >= 8:
            return "非常樂觀"
        elif score >= 6.5:
            return "樂觀"
        elif score >= 5.5:
            return "中立偏樂觀"
        elif score >= 4.5:
            return "中立偏悲觀"
        elif score >= 3:
            return "悲觀"
        else:
            return "非常悲觀"
