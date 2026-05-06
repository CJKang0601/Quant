"""Tests for analysis engine components."""
import pytest
from src.analysis_engine.sentiment_analyzer import SentimentAnalyzer


def test_sentiment_analyzer_positive_text():
    """Test sentiment analysis on positive text."""
    analyzer = SentimentAnalyzer()
    
    text = "台積電看好樂觀推薦買進，成長強勢"
    score = analyzer.analyze_text_sentiment(text, language='zh')
    
    assert score > 6.5  # Should be positive


def test_sentiment_analyzer_negative_text():
    """Test sentiment analysis on negative text."""
    analyzer = SentimentAnalyzer()
    
    text = "看壞衰退弱勢利空警告"
    score = analyzer.analyze_text_sentiment(text, language='zh')
    
    assert score < 4.5  # Should be negative


def test_sentiment_analyzer_neutral_text():
    """Test sentiment analysis on neutral text."""
    analyzer = SentimentAnalyzer()
    
    text = "今天的天氣很好，適合散步"
    score = analyzer.analyze_text_sentiment(text, language='zh')
    
    assert 4.5 <= score <= 6.5  # Should be neutral


def test_sentiment_analyzer_label():
    """Test sentiment label conversion."""
    analyzer = SentimentAnalyzer()
    
    assert analyzer.get_sentiment_label(9.0) == "非常樂觀"
    assert analyzer.get_sentiment_label(7.0) == "樂觀"
    assert analyzer.get_sentiment_label(5.5) == "中立偏樂觀"
    assert analyzer.get_sentiment_label(2.0) == "非常悲觀"
