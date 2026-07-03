"""Quick start example script."""
from datetime import datetime

# Example: How to use the AI Investment Agent

# ============================================================
# 1. PROCESS LOCAL AUDIO FILE
# ============================================================

from main import MainPipeline

# Initialize pipeline
pipeline = MainPipeline()

# Process a local audio file
# pipeline.process_local_audio("data/raw/example.mp3", source_type="youtube")

# ============================================================
# 2. YOUTUBE / PODCAST PROCESSING
# ============================================================

# Uncomment to process YouTube channel
# pipeline.process_youtube_channel("https://www.youtube.com/@YourChannel", max_videos=3)

# Uncomment to process podcast feed
# pipeline.process_podcast_feed("https://example.com/podcast/feed.xml", max_episodes=3)

# ============================================================
# 3. MANUAL ANALYSIS (No audio download)
# ============================================================

from src.utils.data_models import TranscriptionResult
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
    發哥(聯發科)在手機芯片市場的表現強勢。
    GG(台積電)的 CoWoS 產能持續擴張,這是未來兩三年的結構性趨勢。
    整體來看,半導體產業長期前景樂觀。
    """,
    duration_seconds=600,
)

# Preprocess
preprocessor = TextPreprocessor()
preprocessed = preprocessor.preprocess(transcription)

print("Preprocessed content:")
print(f"  - Chunks: {len(preprocessed.chunks)}")
print(f"  - Entities: {preprocessed.entities_detected}")
print(f"  - Jargon mappings: {preprocessed.jargon_mappings}")

# ============================================================
# 4. ANALYZE WITH AGENT (需要 OPENAI_API_KEY)
# ============================================================

agent = InvestmentAgent(llm_provider="openai")
analysis = agent.analyze(
    preprocessed,
    source_id="demo_1",
    source_title="Demo Analysis",
    source_key="demo",
    content_date=datetime.now().strftime("%Y-%m-%d"),
)

if analysis:
    formatter = OutputFormatter()
    print("\n" + formatter.format_for_display(analysis))

    output_path = f"output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    formatter.save_analysis_json(analysis, output_path)
    print(f"\nResults saved to: {output_path}")

    summary = formatter.create_summary(analysis)
    print(f"\nSummary: {summary}")
else:
    print("\n分析未執行(LLM 未配置或分析失敗);核心前處理流程正常。")

print("\nDemo completed!")
