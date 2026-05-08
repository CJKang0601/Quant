"""Global settings for AI Investment Agent."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# LLM Models
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4-turbo-preview")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

# Data Sources
YOUTUBE_CHANNELS = {
    "hao": "https://www.youtube.com/@yutinghaofinance/videos",  # 游庭皓的財經皓角
    "gooaye": "https://www.youtube.com/@Gooaye/videos",  # 股癌 YouTube
    "market_anchor": "https://www.youtube.com/@%E5%AE%9A%E9%8C%A8%E7%94%A2%E6%A5%AD%E7%AD%86%E8%A8%98/videos",  # 定錨產業筆記
}

PODCAST_FEEDS = {
    "gooaye_podcast": "https://feeds.soundon.fm/podcasts/954689a5-3096-43a4-a80b-7810b219cef3.xml",  # 股癌 Podcast RSS 正確位址
}

# Processing Settings
FFMPEG_PATH = r"C:\Users\cjkan\Downloads\ffmpeg-2026-05-06-git-f2e5eff3ff-full_build\ffmpeg-2026-05-06-git-f2e5eff3ff-full_build\bin"
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
