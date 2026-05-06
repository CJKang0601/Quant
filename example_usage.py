"""Quick start example script."""
from pathlib import Path
from datetime import datetime

# Example: How to use the AI Investment Agent

# ============================================================
# 1. PROCESS LOCAL AUDIO FILE
# ============================================================

from main import MainPipeline

# Initialize pipeline
pipeline = MainPipeline()

# Process a local audio file
# audio_path = "data/raw/example.mp3"
# result = pipeline.process_local_audio(
#     audio_path=audio_path,
#     source_type="youtube",
# )

# ============================================================
# 2. YOUTUBE PROCESSING
# ============================================================

# Uncomment to process YouTube channel
# youtube_url = "https://www.youtube.com/@YourChannel"
# num_processed = pipeline.process_youtube_channel(
#     channel_url=youtube_url,
#     max_videos=3
# )
# print(f"Processed {num_processed} YouTube videos")

# ============================================================
# 3. PODCAST PROCESSING
# ============================================================

# Uncomment to process podcast feed
# podcast_url = "https://example.com/podcast/feed.xml"
# num_processed = pipeline.process_podcast_feed(
#     feed_url=podcast_url,
#     max_episodes=3
# )
# print(f"Processed {num_processed} podcast episodes")

# ============================================================
# 4. MANUAL ANALYSIS (No audio download)
# ============================================================

from src.utils.data_models import TranscriptionResult, PreprocessedContent
from src.data_pipeline.preprocessor import TextPreprocessor
from src.analysis_engine.agent import InvestmentAgent
from src.analysis_engine.output_formatter import OutputFormatter

# Create mock transcription result
transcription = TranscriptionResult(
    source_id="demo_1",
    source_type="youtube",
    source_title="Demo Analysis",
    transcript="""
    台積電今年的 AI Server 訂單量持續成長。
    發哥（聯發科）在手機芯片市場的表現強勢。
    GG（台積電）的 CoWoS 產能持續擴張，這是利多。
    整體來看，半導體產業前景樂觀。
    """,
    duration_seconds=600,
)

# Preprocess
preprocessor = TextPreprocessor()
preprocessed = preprocessor.preprocess(transcription)

print(f"Preprocessed content:")
print(f"  - Chunks: {len(preprocessed.chunks)}")
print(f"  - Entities: {preprocessed.entities_detected}")
print(f"  - Jargon mappings: {preprocessed.jargon_mappings}")

# ============================================================
# 5. ANALYZE WITH AGENT
# ============================================================

agent = InvestmentAgent(llm_provider="openai")
analysis = agent.analyze(preprocessed, "demo_1", "Demo Analysis")

if analysis:
    # Display results
    formatter = OutputFormatter()
    print("\n" + formatter.format_for_display(analysis))
    
    # Save to JSON
    output_path = f"output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    formatter.save_analysis_json(analysis, output_path)
    print(f"\nResults saved to: {output_path}")
    
    # Create summary
    summary = formatter.create_summary(analysis)
    print(f"\nSummary: {summary}")

# ============================================================
# 6. EXPORT RECOMMENDATIONS AS CSV
# ============================================================

if analysis and analysis.recommendations:
    csv_output = formatter.format_csv_recommendations(analysis.recommendations)
    csv_path = f"recommendations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(csv_path, 'w', encoding='utf-8') as f:
        f.write(csv_output)
    print(f"\nRecommendations exported to: {csv_path}")

print("\n✅ Demo completed!")
