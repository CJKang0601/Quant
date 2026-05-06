"""Tests for data pipeline components."""
import pytest
from pathlib import Path
from src.data_pipeline.preprocessor import JargonMapper, TextPreprocessor


def test_jargon_mapper_get_ticker():
    """Test jargon mapping."""
    mapper = JargonMapper()
    
    # Test known mappings
    assert mapper.get_ticker("GG") == "2330.TW"
    assert mapper.get_ticker("發哥") == "2454.TW"


def test_text_preprocessor_clean_text():
    """Test text cleaning."""
    preprocessor = TextPreprocessor()
    
    text = "你好  世界   測試"
    cleaned = preprocessor.clean_text(text)
    
    assert "  " not in cleaned
    assert cleaned == "你好 世界 測試"


def test_text_preprocessor_segment_sentences():
    """Test sentence segmentation."""
    preprocessor = TextPreprocessor()
    
    text = "第一句。第二句！第三句？"
    sentences = preprocessor.segment_sentences(text)
    
    assert len(sentences) == 3


def test_text_preprocessor_create_chunks():
    """Test text chunking."""
    preprocessor = TextPreprocessor()
    
    text = "a" * 500  # 500 character string
    chunks = preprocessor.create_chunks(text, chunk_size=100, overlap=20)
    
    assert len(chunks) > 1
    assert len(chunks[0]) == 100
