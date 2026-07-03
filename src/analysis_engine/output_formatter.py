"""Output formatting for analysis results."""
import json
from typing import Dict, Any
from src.utils.logger import get_logger
from src.utils.data_models import AnalysisResult, TimeHorizon

logger = get_logger(__name__)

HORIZON_LABELS = {
    TimeHorizon.SHORT: "短期(0-3月)",
    TimeHorizon.MID: "中期(3-18月)",
    TimeHorizon.LONG: "長期(18月+)",
}


class OutputFormatter:
    """Formats analysis results into structured JSON outputs."""

    @staticmethod
    def format_analysis_to_json(analysis_result: AnalysisResult) -> str:
        """Convert AnalysisResult to JSON string."""
        try:
            return analysis_result.model_dump_json(indent=2)
        except Exception as e:
            logger.error(f"Error converting AnalysisResult to JSON: {e}")
            return "{}"

    @staticmethod
    def save_analysis_json(analysis_result: AnalysisResult, filepath: str) -> bool:
        """Save analysis result to JSON file."""
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
        """Create a summary of analysis results for the dashboard."""
        horizon_counts = {"SHORT": 0, "MID": 0, "LONG": 0}
        for trend in analysis_result.industry_trends:
            horizon_counts[trend.time_horizon.value] += 1

        return {
            "timestamp": analysis_result.timestamp.isoformat(),
            "source_key": analysis_result.source_key,
            "source_id": analysis_result.source_id,
            "source_title": analysis_result.source_title,
            "content_date": analysis_result.content_date,
            "macro_sentiment": round(analysis_result.macro_view.overall_sentiment, 2) if analysis_result.macro_view else 0,
            "industry_trend_count": len(analysis_result.industry_trends),
            "horizon_counts": horizon_counts,
            "summary_snippet": analysis_result.overall_summary[:100] + "...",
        }

    @staticmethod
    def format_for_display(analysis_result: AnalysisResult) -> str:
        """Format analysis result as human-readable console text."""
        lines = [
            "=" * 70,
            f"來源: {analysis_result.source_title} ({analysis_result.source_key or analysis_result.source_type})",
            f"節目日期: {analysis_result.content_date or '未知'}",
            "-" * 70,
            f"摘要: {analysis_result.overall_summary}",
        ]

        if analysis_result.macro_view:
            lines.append(f"宏觀情緒: {analysis_result.macro_view.overall_sentiment:.1f}/10")
            for driver in analysis_result.macro_view.key_drivers:
                lines.append(f"  驅動因素: {driver}")

        if analysis_result.industry_trends:
            lines.append("-" * 70)
            lines.append("產業趨勢:")
            for trend in analysis_result.industry_trends:
                horizon = HORIZON_LABELS.get(trend.time_horizon, trend.time_horizon.value)
                lines.append(f"  [{horizon}] {trend.industry_name} ({trend.sentiment_score:.1f}/10)")
                if trend.thesis:
                    lines.append(f"    論點: {trend.thesis}")
                for company in trend.supporting_companies:
                    ticker = f" ({company.ticker})" if company.ticker else ""
                    lines.append(f"    佐證個股: {company.name}{ticker} — {company.role_in_trend}")

        if analysis_result.key_risks:
            lines.append("-" * 70)
            lines.append("關鍵風險: " + "; ".join(analysis_result.key_risks))

        lines.append("=" * 70)
        return "\n".join(lines)
