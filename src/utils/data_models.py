"""Data models for AI Investment Agent using Pydantic.

設計原則:本系統的目標是追蹤「短中長期產業趨勢」,而非個股操作建議。
個股只作為趨勢的佐證(CompanyMention),不輸出 BUY/SELL 訊號。
"""
from typing import List, Dict, Optional, Any
from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class TimeHorizon(str, Enum):
    """趨勢的時間尺度。"""
    SHORT = "SHORT"  # 0-3 個月
    MID = "MID"      # 3-18 個月
    LONG = "LONG"    # 18 個月以上


class CompanyMention(BaseModel):
    """個股提及 — 作為產業趨勢的佐證,而非操作建議。"""
    name: str = Field(..., description="公司名稱")
    ticker: Optional[str] = Field(None, description="股票代號(如 '2330.TW', 'NVDA'),不確定時留空")
    market: Optional[str] = Field(None, description="市場: TW 或 US")
    role_in_trend: str = Field("", description="該公司在這個趨勢中扮演的角色")
    quote: Optional[str] = Field(None, description="節目中提到該公司的關鍵原句引述")


class MacroView(BaseModel):
    """Macro-level market sentiment."""
    overall_sentiment: float = Field(..., ge=1.0, le=10.0, description="Overall bullish score (1-10)")
    key_drivers: List[str] = Field(default_factory=list, description="Key macro factors")
    global_outlook: Optional[str] = Field(None, description="Global economic outlook")


class IndustryTrend(BaseModel):
    """Industry-level trend analysis — 系統的核心輸出。"""
    industry_name: str = Field(..., description="Industry name")
    sentiment_score: float = Field(..., ge=1.0, le=10.0, description="Industry sentiment (1-10)")
    time_horizon: TimeHorizon = Field(TimeHorizon.MID, description="趨勢的時間尺度")
    thesis: str = Field("", description="這個趨勢的核心論點(一兩句話)")
    key_trends: List[str] = Field(default_factory=list, description="Key trends in this industry")
    growth_drivers: List[str] = Field(default_factory=list, description="Growth drivers")
    supporting_companies: List[CompanyMention] = Field(
        default_factory=list, description="支持這個趨勢判斷的個股佐證"
    )


class AnalysisResult(BaseModel):
    """Complete analysis result from Agent."""
    timestamp: datetime = Field(default_factory=utc_now, description="Analysis timestamp")
    source_key: str = Field("", description="來源代碼: hao / gooaye / market_anchor / gooaye_podcast")
    source_id: str = Field(..., description="Source ID")
    source_title: str = Field(..., description="Source Title")
    source_type: str = Field(..., description="youtube or podcast")
    content_date: Optional[str] = Field(None, description="節目發布日期 YYYY-MM-DD(用於趨勢時間軸)")
    overall_summary: str = Field(..., description="A 150-200 word executive summary of the episode")
    macro_view: Optional[MacroView] = Field(None, description="Macro-level sentiment")
    industry_trends: List[IndustryTrend] = Field(default_factory=list, description="Industry analysis")
    key_risks: List[str] = Field(default_factory=list, description="Overall risks")
    discussed_companies: List[Dict[str, str]] = Field(
        default_factory=list, description="未歸入特定趨勢、但有被討論的公司"
    )
    jargon_explained: List[Dict[str, str]] = Field(default_factory=list, description="Jargon explained")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class TranscriptionResult(BaseModel):
    """Transcription result from audio processing."""
    source_id: str = Field(..., description="Unique source identifier")
    source_type: str = Field(..., description="'youtube' or 'podcast'")
    source_title: str = Field(..., description="Title of the content")
    source_url: Optional[str] = Field(None, description="URL of the source")
    transcript: str = Field(..., description="Full transcript text")
    duration_seconds: int = Field(..., description="Audio duration in seconds")
    language: str = Field(default="zh-TW", description="Language code")
    processed_at: datetime = Field(default_factory=utc_now, description="Processing timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class PreprocessedContent(BaseModel):
    """Preprocessed content ready for analysis."""
    transcription_id: str = Field(..., description="Reference to transcription")
    normalized_text: str = Field(..., description="Cleaned and normalized text")
    jargon_mappings: Dict[str, str] = Field(default_factory=dict, description="Applied jargon mappings")
    chunks: List[str] = Field(default_factory=list, description="Text chunks for RAG")
    entities_detected: List[str] = Field(default_factory=list, description="Named entities detected")
    preprocessing_timestamp: datetime = Field(default_factory=utc_now)
