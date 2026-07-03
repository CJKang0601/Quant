"""Global settings for AI Investment Agent."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
PROCESSED_MANIFEST_PATH = PROJECT_ROOT / "data" / "processed_manifest.json"

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# LLM Provider & Models
# LLM_PROVIDER: "openai" 或 "google";LLM_MODEL 留空時採用該供應商的預設模型
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
LLM_MODEL = os.getenv("LLM_MODEL", "")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

# Data Sources
YOUTUBE_CHANNELS = {
    "hao": "https://www.youtube.com/@yutinghaofinance/videos",  # 游庭皓的財經皓角
    "gooaye": "https://www.youtube.com/@Gooaye/videos",  # 股癌 YouTube
    "market_anchor": "https://www.youtube.com/@%E5%AE%9A%E9%8C%A8%E7%94%A2%E6%A5%AD%E7%AD%86%E8%A8%98/videos",  # 定錨產業筆記
}

PODCAST_FEEDS = {
    "gooaye_podcast": "https://feeds.soundon.fm/podcasts/954689a5-3096-43a4-a80b-7810b219cef3.xml",  # 股癌 Podcast RSS
}

# 各來源的顯示資訊與更新節奏(供介面與排程參考)
SOURCE_INFO = {
    "hao": {"name": "財經皓角", "cadence": "每日早上 8:30 直播留檔"},
    "gooaye": {"name": "股癌", "cadence": "每週三、六更新"},
    "gooaye_podcast": {"name": "股癌 Podcast", "cadence": "每週三、六更新"},
    "market_anchor": {"name": "定錨產業筆記", "cadence": "不定期(法說會/產業深度)"},
}

# Processing Settings
# 本機若 ffmpeg 不在 PATH,可在 .env 設定 FFMPEG_PATH 指向 ffmpeg 的 bin 目錄
FFMPEG_PATH = os.getenv("FFMPEG_PATH", "")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")  # tiny, base, small, medium, large
MAX_AUDIO_DURATION_HOURS = 4
CHUNK_SIZE = 300  # Characters per chunk for RAG

# Sentiment Score Range
SENTIMENT_MIN_SCORE = 1
SENTIMENT_MAX_SCORE = 10

# Vector DB Settings
VECTOR_DB_TYPE = os.getenv("VECTOR_DB_TYPE", "chromadb")  # chromadb or pinecone
CHROMADB_PATH = DATA_PROCESSED_DIR / "chromadb"

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
