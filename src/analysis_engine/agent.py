"""Main LLM Agent for financial analysis."""
from typing import Optional, List, Dict, Any
from datetime import datetime
import json

from src.utils.logger import get_logger
from src.utils.data_models import AnalysisResult, Recommendation, MacroView, IndustryTrend, PreprocessedContent
from src.analysis_engine.sentiment_analyzer import SentimentAnalyzer
from src.analysis_engine.entity_matcher import EntityMatcher, RAGRetriever
from src.analysis_engine.output_formatter import OutputFormatter

logger = get_logger(__name__)


class InvestmentAgent:
    """Main Agent for AI-driven investment analysis."""
    
    def __init__(self, llm_provider: str = "openai"):
        """
        Initialize Investment Agent.
        
        Args:
            llm_provider: LLM provider ('openai', 'google', 'anthropic')
        """
        self.llm_provider = llm_provider
        self.sentiment_analyzer = SentimentAnalyzer()
        self.entity_matcher = EntityMatcher()
        try:
            self.rag_retriever = RAGRetriever()
        except Exception as e:
            logger.warning(f"RAG retriever not available: {e}")
            self.rag_retriever = None
        self.formatter = OutputFormatter()
        
        # Initialize LLM
        self._initialize_llm()
        
        logger.info(f"InvestmentAgent initialized with {llm_provider}")
    
    def _initialize_llm(self) -> None:
        """Initialize LLM client based on provider."""
        try:
            if self.llm_provider == "openai":
                from langchain_openai import ChatOpenAI
                self.llm = ChatOpenAI(
                    model_name="gpt-4-turbo-preview",
                    temperature=0.3,
                )
            elif self.llm_provider == "google":
                from langchain_google_genai import ChatGoogleGenerativeAI
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-pro",
                    temperature=0.3,
                )
            else:
                logger.warning(f"Unknown LLM provider: {self.llm_provider}")
                self.llm = None
        except ImportError:
            logger.warning(f"Could not import LLM client for {self.llm_provider}")
            self.llm = None
    
    def analyze(
        self,
        preprocessed_content: PreprocessedContent,
        source_id: str,
        source_title: str = "",
    ) -> Optional[AnalysisResult]:
        """
        Full analysis using LLM for structured insights.
        """
        try:
            logger.info(f"Starting deep analysis for {source_id}")
            
            # Prepare context
            full_text = preprocessed_content.normalized_text
            jargon_hint = json.dumps(preprocessed_content.jargon_mappings, ensure_ascii=False)
            
            prompt = f"""
            你是一位專業的投資研究員。請針對以下財經內容進行深度分析並輸出 JSON 格式。
            
            來源標題: {source_title}
            
            內容全文:
            {full_text[:6000]} # 限制長度
            
            已知黑話映射: {jargon_hint}
            
            請嚴格遵守以下格式輸出 JSON:
            {{
                "overall_summary": "150-200字的本集核心摘要...",
                "macro_view": {{
                    "overall_sentiment": 1-10的分數,
                    "key_drivers": ["原因1", "原因2"],
                    "global_outlook": "簡短全球展望"
                }},
                "industry_trends": [
                    {{
                        "industry_name": "產業名稱",
                        "sentiment_score": 1-10的分數,
                        "key_trends": ["趨勢1", "趨勢2"],
                        "growth_drivers": ["驅動因素"]
                    }}
                ],
                "recommendations": [
                    {{
                        "ticker": "代號",
                        "name": "公司名稱",
                        "market": "TW 或 US",
                        "action": "BUY/SELL/HOLD",
                        "reason": "具體的推薦理由",
                        "context_snippet": "在哪個時間點或段落提到了什麼(具體引述內容)",
                        "confidence_score": 0.0-1.0,
                        "risk_level": "LOW/MEDIUM/HIGH"
                    }}
                ],
                "key_risks": ["風險1", "風險2"],
                "discussed_companies": [
                    {{"name": "公司名", "description": "本集對該公司的描述"}}
                ],
                "jargon_explained": [
                    {{"term": "黑話/術語", "explanation": "在本集中的含義"}}
                ]
            }}
            """
            
            if not self.llm:
                return None
                
            response = self.llm.invoke(prompt)
            data = json.loads(response.content)
            
            # Create models from response data
            macro = MacroView(**data["macro_view"])
            industries = [IndustryTrend(**it) for item in data.get("industry_trends", [])] # This line had a minor naming fix needed
            industries = [IndustryTrend(**it) for it in data.get("industry_trends", [])]
            recs = [Recommendation(**r) for r in data.get("recommendations", [])]
            
            result = AnalysisResult(
                timestamp=datetime.utcnow(),
                source_id=source_id,
                source_title=source_title or source_id,
                source_type="youtube" if "hao" in source_id or "market" in source_id else "podcast",
                overall_summary=data.get("overall_summary", ""),
                macro_view=macro,
                industry_trends=industries,
                recommendations=recs,
                key_risks=data.get("key_risks", []),
                discussed_companies=data.get("discussed_companies", []),
                jargon_explained=data.get("jargon_explained", []),
                metadata={"source_id": source_id}
            )
            
            logger.info(f"Analysis completed for {source_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error in deep analysis: {e}")
            return None
    
    def _sentiment_to_action(self, sentiment_score: float) -> str:
        """Convert sentiment score to action."""
        if sentiment_score >= 7:
            return "BUY"
        elif sentiment_score <= 4:
            return "SELL"
        else:
            return "HOLD"
    
    def _calculate_confidence(self, sentiment_score: float, ticker: str) -> float:
        """Calculate confidence score for recommendation."""
        # Base confidence from sentiment extremity
        base_confidence = abs(sentiment_score - 5.5) / 4.5
        
        # Adjust based on ticker specificity
        # (In real implementation, would check frequency, context strength, etc.)
        adjusted = min(0.95, base_confidence * 0.9)
        
        return max(0.5, adjusted)
    
    def _generate_reason(self, ticker: str, sentiment: float, content: PreprocessedContent) -> str:
        """Generate explanation for recommendation."""
        label = self.sentiment_analyzer.get_sentiment_label(sentiment)
        
        # Extract key sentences about ticker
        import re
        sentences = re.split(r'[。！？\n]+', content.normalized_text)
        relevant = [s for s in sentences if ticker.lower() in s.lower()]
        
        if relevant:
            return f"{label}: {relevant[0][:100]}"
        else:
            return f"Market sentiment toward {ticker} is {label}"
    
    def _assess_risk_level(self, sentiment_score: float) -> str:
        """Assess risk level based on sentiment."""
        if 4 <= sentiment_score <= 7:
            return "LOW"
        elif sentiment_score > 7 or sentiment_score < 4:
            return "MEDIUM"
        else:
            return "HIGH"
    
    def _extract_industries_from_content(self, content: PreprocessedContent) -> List[str]:
        """Extract industry mentions from content."""
        industries = []
        
        # Common Taiwan industries
        industry_keywords = {
            "半導體": "Semiconductors",
            "電子製造": "Electronics Manufacturing",
            "AI": "Artificial Intelligence",
            "軟體": "Software",
            "銀行": "Banking",
            "金融": "Finance",
            "電信": "Telecommunications",
            "能源": "Energy",
        }
        
        for keyword in industry_keywords.keys():
            if keyword in content.normalized_text:
                industries.append(industry_keywords[keyword])
        
        return industries if industries else ["Technology"]
    
    def _extract_industry_trends(self, industry: str, content: PreprocessedContent) -> List[str]:
        """Extract key trends for an industry."""
        trends = []
        
        # Simple keyword matching for trends
        trend_keywords = {
            "成長": "Growth opportunity",
            "投資": "Investment increase",
            "新產品": "New product launch",
            "競爭": "Increased competition",
            "政策": "Policy changes",
            "技術": "Technology advancement",
        }
        
        for keyword, trend in trend_keywords.items():
            if keyword in content.normalized_text:
                trends.append(trend)
        
        return trends[:3]  # Top 3 trends
    
    def _extract_key_drivers(self, content: PreprocessedContent) -> List[str]:
        """Extract key macro drivers from content."""
        drivers = []
        
        driver_keywords = {
            "利率": "Interest rate movements",
            "通膨": "Inflation dynamics",
            "聯準會": "Fed policy",
            "GDP": "Economic growth",
            "貿易": "Trade tensions",
            "匯率": "Currency movements",
        }
        
        for keyword, driver in driver_keywords.items():
            if keyword in content.normalized_text:
                drivers.append(driver)
        
        return drivers[:3] if drivers else ["Market volatility"]
    
    def _assess_risks(self, tickers: List[str], content: PreprocessedContent) -> List[str]:
        """Assess key risks mentioned in content."""
        risks = []
        
        risk_keywords = {
            "風險": "Market risk",
            "虧損": "Potential losses",
            "衰退": "Economic recession",
            "利率上升": "Rising interest rates",
            "監管": "Regulatory risks",
            "競爭": "Competitive pressure",
        }
        
        for keyword, risk in risk_keywords.items():
            if keyword in content.normalized_text:
                risks.append(risk)
        
        return risks[:5] if risks else ["General market uncertainty"]
