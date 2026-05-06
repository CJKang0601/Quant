"""Example notebook for AI Investment Agent analysis."""
# %%
# # AI Investment Agent - Analysis Demo

# %%
# ## Setup and Imports

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path.cwd()))

from src.data_pipeline.preprocessor import TextPreprocessor, JargonMapper
from src.analysis_engine.sentiment_analyzer import SentimentAnalyzer
from src.analysis_engine.entity_matcher import EntityMatcher
from src.analysis_engine.output_formatter import OutputFormatter

# %%
# ## Example Text Analysis

# Sample financial commentary (mock data)
sample_text = """
皓哥今天分享了他對台積電的最新看法。
發哥在半導體領域表現強勢，AI Server 需求超出預期。
GG（台積電）的 CoWoS 產能持續擴張，這對整個供應鏈都是利多。
聯發科在手機芯片市場也有不錯的成長機會。
整體來看，半導體產業前景樂觀，建議持續關注。
"""

# %%
# ## Text Preprocessing

preprocessor = TextPreprocessor()

# Clean text
cleaned_text = preprocessor.clean_text(sample_text)
print("Cleaned text:", cleaned_text[:100], "...")

# %%
# Normalize jargon
normalized_text, mappings = preprocessor.jargon_mapper.normalize_text(cleaned_text)
print("\nJargon mappings applied:")
for jargon, ticker in mappings.items():
    print(f"  {jargon} → {ticker}")

# %%
# Extract entities
entities = preprocessor.extract_entities(normalized_text)
print("\nDetected entities:", entities)

# %%
# Create chunks for RAG
chunks = preprocessor.create_chunks(normalized_text, chunk_size=200)
print(f"\nCreated {len(chunks)} text chunks")
for i, chunk in enumerate(chunks[:2]):
    print(f"Chunk {i+1}: {chunk[:80]}...")

# %%
# ## Sentiment Analysis

analyzer = SentimentAnalyzer()

# Overall sentiment
overall_sentiment = analyzer.analyze_text_sentiment(normalized_text, language='zh')
print(f"\nOverall sentiment: {overall_sentiment:.1f}/10")
print(f"Label: {analyzer.get_sentiment_label(overall_sentiment)}")

# %%
# Per-ticker sentiment
tickers = ['2330.TW', '2454.TW', 'NVDA']

print("\nPer-ticker sentiment:")
for ticker in tickers:
    sentiment = analyzer.analyze_ticker_sentiment(normalized_text, ticker, language='zh')
    print(f"  {ticker}: {sentiment:.1f}/10 ({analyzer.get_sentiment_label(sentiment)})")

# %%
# ## Entity Matching

matcher = EntityMatcher()

# Extract ticker mentions
ticker_mentions = matcher.extract_ticker_mentions(normalized_text)
print("\nExtracted tickers:")
for ticker, confidence in ticker_mentions:
    print(f"  {ticker} (confidence: {confidence:.0%})")

# %%
# ## Output Formatting

# Example: Create a sample AnalysisResult
from src.utils.data_models import AnalysisResult, MacroView, Recommendation, ActionType
from datetime import datetime

result = AnalysisResult(
    timestamp=datetime.utcnow(),
    sources=["Hao_Demo"],
    macro_view=MacroView(
        overall_sentiment=7.5,
        key_drivers=["AI demand growth", "Semiconductor strength"],
    ),
    recommendations=[
        Recommendation(
            ticker="2330.TW",
            action=ActionType.BUY,
            reason="AI Server 需求超出預期",
            confidence_score=0.88,
            risk_level="MEDIUM",
        ),
        Recommendation(
            ticker="2454.TW",
            action=ActionType.HOLD,
            reason="穩定增長，值得持續關注",
            confidence_score=0.72,
            risk_level="LOW",
        ),
    ],
    key_risks=["Supply chain disruption", "Geopolitical tensions"],
)

# %%
# Display formatted output
formatter = OutputFormatter()
display_text = formatter.format_for_display(result)
print(display_text)

# %%
# Save to JSON
import json
json_output = formatter.format_analysis_to_json(result)
print("\nJSON output:")
print(json_output[:500], "...")
