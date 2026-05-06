"""Data models for AI Investment Agent using Pydantic."""
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class ActionType(str, Enum):
    """Investment action types."""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class Recommendation(BaseModel):
    """Single investment recommendation."""
    ticker: str = Field(..., description="Stock ticker (e.g., '2330.TW', 'NVDA')")
    action: ActionType = Field(..., description="BUY, SELL, or HOLD")
    reason: str = Field(..., description="Why this recommendation")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence [0-1]")
    target_price: Optional[float] = Field(None, description="Target price if applicable")
    risk_level: Optional[str] = Field("medium", description="LOW, MEDIUM, HIGH")


class MacroView(BaseModel):
    """Macro-level market sentiment."""
    overall_sentiment: float = Field(..., ge=1.0, le=10.0, description="Overall bullish score (1-10)")
    key_drivers: List[str] = Field(default_factory=list, description="Key macro factors")
    global_outlook: Optional[str] = Field(None, description="Global economic outlook")


class IndustryTrend(BaseModel):
    """Industry-level analysis."""
    industry_name: str = Field(..., description="Industry name")
    sentiment_score: float = Field(..., ge=1.0, le=10.0, description="Industry sentiment (1-10)")
    key_trends: List[str] = Field(default_factory=list, description="Key trends in this industry")
    growth_drivers: List[str] = Field(default_factory=list, description="Growth drivers")


class RiskManagement(BaseModel):
    """Risk management details."""
    overall_exposure_limit: str = Field(default="60%", description="Max portfolio exposure")
    suggested_stop_loss: str = Field(default="-8%", description="Suggested stop-loss %")
    suggested_take_profit: Optional[str] = Field(None, description="Suggested take-profit %")


class AnalysisResult(BaseModel):
    """Complete analysis result from Agent."""
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Analysis timestamp")
    sources: List[str] = Field(default_factory=list, description="Source names (e.g., 'Hao_Ep123')")
    macro_view: Optional[MacroView] = Field(None, description="Macro-level sentiment")
    industry_trends: List[IndustryTrend] = Field(default_factory=list, description="Industry analysis")
    recommendations: List[Recommendation] = Field(default_factory=list, description="Stock recommendations")
    key_risks: List[str] = Field(default_factory=list, description="Overall risks")
    risk_management: RiskManagement = Field(default_factory=RiskManagement, description="Risk management guidance")
    raw_analysis: Optional[str] = Field(None, description="Raw LLM analysis output")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TranscriptionResult(BaseModel):
    """Transcription result from audio processing."""
    source_id: str = Field(..., description="Unique source identifier")
    source_type: str = Field(..., description="'youtube' or 'podcast'")
    source_title: str = Field(..., description="Title of the content")
    source_url: Optional[str] = Field(None, description="URL of the source")
    transcript: str = Field(..., description="Full transcript text")
    duration_seconds: int = Field(..., description="Audio duration in seconds")
    language: str = Field(default="zh-TW", description="Language code")
    processed_at: datetime = Field(default_factory=datetime.utcnow, description="Processing timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class PreprocessedContent(BaseModel):
    """Preprocessed content ready for analysis."""
    transcription_id: str = Field(..., description="Reference to transcription")
    normalized_text: str = Field(..., description="Cleaned and normalized text")
    jargon_mappings: Dict[str, str] = Field(default_factory=dict, description="Applied jargon mappings")
    chunks: List[str] = Field(default_factory=list, description="Text chunks for RAG")
    entities_detected: List[str] = Field(default_factory=list, description="Named entities detected")
    preprocessing_timestamp: datetime = Field(default_factory=datetime.utcnow)


class RAGQuery(BaseModel):
    """Query for RAG vector database."""
    query_text: str = Field(..., description="Query text")
    query_type: str = Field(default="general", description="'general', 'sentiment', 'entity'")
    top_k: int = Field(default=5, description="Number of results to retrieve")


class RAGResult(BaseModel):
    """Result from RAG query."""
    query_id: str = Field(..., description="Query identifier")
    matches: List[Dict[str, Any]] = Field(default_factory=list, description="Matched documents")
    total_results: int = Field(default=0, description="Total matching results")
