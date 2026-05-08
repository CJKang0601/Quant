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
    name: Optional[str] = Field(None, description="Company name")
    market: str = Field("TW", description="Market category: TW or US")
    action: ActionType = Field(..., description="BUY, SELL, or HOLD")
    reason: str = Field(..., description="Why this recommendation")
    context_snippet: str = Field(..., description="Specific text snippet or approx timestamp where this was mentioned")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence [0-1]")
    risk_level: Optional[str] = Field("MEDIUM", description="LOW, MEDIUM, HIGH")


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


class AnalysisResult(BaseModel):
    """Complete analysis result from Agent."""
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Analysis timestamp")
    source_id: str = Field(..., description="Source ID")
    source_title: str = Field(..., description="Source Title")
    source_type: str = Field(..., description="youtube or podcast")
    overall_summary: str = Field(..., description="A 150-200 word executive summary of the episode")
    macro_view: Optional[MacroView] = Field(None, description="Macro-level sentiment")
    industry_trends: List[IndustryTrend] = Field(default_factory=list, description="Industry analysis")
    recommendations: List[Recommendation] = Field(default_factory=list, description="Stock recommendations")
    key_risks: List[str] = Field(default_factory=list, description="Overall risks")
    discussed_companies: List[Dict[str, str]] = Field(default_factory=list, description="Companies mentioned with brief descriptions")
    jargon_explained: List[Dict[str, str]] = Field(default_factory=list, description="Jargon explained")
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
