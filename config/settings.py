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
    "market_anchor": "https://www.youtube.com/@marketanchors/videos",  # 市場錨定
}

PODCAST_FEEDS = {
    "gooaye": "https://feeds.soundon.fm/podcasts/7f70ff38-ac90-449e-8c7c-487770830720.xml",  # 股癌 RSS
}

# Processing Settings
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
