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
        
        Args:
            analysis_result: AnalysisResult instance
            
        Returns:
            JSON string
        """
        try:
            return json.dumps(
                analysis_result.model_dump(),
                ensure_ascii=False,
                indent=2,
                default=str,
            )
        except Exception as e:
            logger.error(f"Error converting AnalysisResult to JSON: {e}")
            return "{}"
    
    @staticmethod
    def format_analysis_to_dict(analysis_result: AnalysisResult) -> Dict[str, Any]:
        """
        Convert AnalysisResult to dictionary.
        
        Args:
            analysis_result: AnalysisResult instance
            
        Returns:
            Dictionary
        """
        return analysis_result.model_dump()
    
    @staticmethod
    def save_analysis_json(analysis_result: AnalysisResult, filepath: str) -> bool:
        """
        Save analysis result to JSON file.
        
        Args:
            analysis_result: AnalysisResult instance
            filepath: Path to save JSON file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            json_str = OutputFormatter.format_analysis_to_json(analysis_result)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(json_str)
            logger.info(f"Saved analysis to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving analysis JSON: {e}")
            return False
    
    @staticmethod
    def format_for_display(analysis_result: AnalysisResult) -> str:
        """
        Format analysis result for human-readable display.
        
        Args:
            analysis_result: AnalysisResult instance
            
        Returns:
            Formatted string
        """
        lines = []
        
        # Header
        lines.append("=" * 80)
        lines.append("AI INVESTMENT ANALYSIS REPORT")
        lines.append("=" * 80)
        lines.append(f"Time: {analysis_result.timestamp.isoformat()}")
        lines.append(f"Sources: {', '.join(analysis_result.sources)}")
        lines.append("")
        
        # Macro View
        if analysis_result.macro_view:
            lines.append("【 MACRO VIEW 】")
            lines.append(f"Overall Sentiment: {analysis_result.macro_view.overall_sentiment:.1f}/10")
            if analysis_result.macro_view.key_drivers:
                lines.append(f"Key Drivers: {', '.join(analysis_result.macro_view.key_drivers)}")
            lines.append("")
        
        # Industry Trends
        if analysis_result.industry_trends:
            lines.append("【 INDUSTRY TRENDS 】")
            for trend in analysis_result.industry_trends:
                lines.append(f"\n{trend.industry_name} (Sentiment: {trend.sentiment_score:.1f}/10)")
                if trend.key_trends:
                    for t in trend.key_trends:
                        lines.append(f"  • {t}")
            lines.append("")
        
        # Recommendations
        if analysis_result.recommendations:
            lines.append("【 STOCK RECOMMENDATIONS 】")
            for rec in analysis_result.recommendations:
                action_color = "🔺" if rec.action == "BUY" else "🔻" if rec.action == "SELL" else "➡️"
                lines.append(f"\n{action_color} {rec.ticker} - {rec.action}")
                lines.append(f"  Confidence: {rec.confidence_score:.0%}")
                lines.append(f"  Reason: {rec.reason}")
                if rec.target_price:
                    lines.append(f"  Target Price: {rec.target_price}")
            lines.append("")
        
        # Key Risks
        if analysis_result.key_risks:
            lines.append("【 KEY RISKS 】")
            for risk in analysis_result.key_risks:
                lines.append(f"  • {risk}")
            lines.append("")
        
        # Risk Management
        if analysis_result.risk_management:
            lines.append("【 RISK MANAGEMENT 】")
            lines.append(f"Portfolio Exposure Limit: {analysis_result.risk_management.overall_exposure_limit}")
            lines.append(f"Suggested Stop-Loss: {analysis_result.risk_management.suggested_stop_loss}")
            if analysis_result.risk_management.suggested_take_profit:
                lines.append(f"Suggested Take-Profit: {analysis_result.risk_management.suggested_take_profit}")
        
        lines.append("")
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    @staticmethod
    def format_csv_recommendations(recommendations: List[Recommendation]) -> str:
        """
        Format recommendations as CSV.
        
        Args:
            recommendations: List of Recommendation objects
            
        Returns:
            CSV-formatted string
        """
        lines = []
        lines.append("Ticker,Action,Confidence,Risk Level,Target Price,Reason")
        
        for rec in recommendations:
            target_price = rec.target_price or ""
            reason = rec.reason.replace(",", ";")  # Escape commas in reason
            lines.append(f"{rec.ticker},{rec.action},{rec.confidence_score:.2f},{rec.risk_level},{target_price},\"{reason}\"")
        
        return "\n".join(lines)
    
    @staticmethod
    def create_summary(analysis_result: AnalysisResult) -> Dict[str, Any]:
        """
        Create a summary of analysis results.
        
        Args:
            analysis_result: AnalysisResult instance
            
        Returns:
            Summary dictionary
        """
        summary = {
            "timestamp": analysis_result.timestamp.isoformat(),
            "sources_count": len(analysis_result.sources),
            "macro_sentiment": round(analysis_result.macro_view.overall_sentiment, 2) if analysis_result.macro_view else None,
            "industry_count": len(analysis_result.industry_trends),
            "recommendations_count": len(analysis_result.recommendations),
            "buy_count": sum(1 for r in analysis_result.recommendations if r.action == "BUY"),
            "sell_count": sum(1 for r in analysis_result.recommendations if r.action == "SELL"),
            "hold_count": sum(1 for r in analysis_result.recommendations if r.action == "HOLD"),
            "avg_confidence": (
                round(sum(r.confidence_score for r in analysis_result.recommendations) / len(analysis_result.recommendations), 2)
                if analysis_result.recommendations else 0
            ),
            "risk_count": len(analysis_result.key_risks),
        }
        
        return summary
