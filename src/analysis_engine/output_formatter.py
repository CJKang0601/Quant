"""Output formatting for analysis results."""
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from src.utils.logger import get_logger
from src.utils.data_models import AnalysisResult, Recommendation, MacroView, IndustryTrend, RiskManagement

logger = get_logger(__name__)


class OutputFormatter:
    """Formats analysis results into structured JSON outputs."""
    
    @staticmethod
    def format_analysis_to_json(analysis_result: AnalysisResult) -> str:
        """
        Convert AnalysisResult to JSON string.
        """
        try:
            return analysis_result.model_dump_json(indent=2)
        except Exception as e:
            logger.error(f"Error converting AnalysisResult to JSON: {e}")
            return "{}"
    
    @staticmethod
    def save_analysis_json(analysis_result: AnalysisResult, filepath: str) -> bool:
        """
        Save analysis result to JSON file.
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(OutputFormatter.format_analysis_to_json(analysis_result))
            logger.info(f"Saved analysis to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving analysis JSON: {e}")
            return False

    @staticmethod
    def create_summary(analysis_result: AnalysisResult) -> Dict[str, Any]:
        """
        Create a summary of analysis results for the dashboard.
        """
        summary = {
            "timestamp": analysis_result.timestamp.isoformat(),
            "source_id": analysis_result.source_id,
            "source_title": analysis_result.source_title,
            "macro_sentiment": round(analysis_result.macro_view.overall_sentiment, 2) if analysis_result.macro_view else 0,
            "recommendations_count": len(analysis_result.recommendations),
            "summary_snippet": analysis_result.overall_summary[:100] + "...",
            "tw_count": sum(1 for r in analysis_result.recommendations if r.market == "TW"),
            "us_count": sum(1 for r in analysis_result.recommendations if r.market == "US"),
        }
        return summary
