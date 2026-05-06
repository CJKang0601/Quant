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
        Analyze preprocessed content and generate investment recommendations.
        
        Args:
            preprocessed_content: PreprocessedContent from data pipeline
            source_id: Unique identifier for source
            source_title: Title of source content
            
        Returns:
            AnalysisResult with recommendations, or None if failed
        """
        try:
            logger.info(f"Starting analysis for {source_id}")
            
            # Step 1: Extract entities
            tickers = self.entity_matcher.extract_ticker_mentions(preprocessed_content.normalized_text)
            logger.info(f"Extracted {len(tickers)} tickers")
            
            # Step 2: Overall sentiment analysis
            overall_sentiment = self.sentiment_analyzer.analyze_text_sentiment(
                preprocessed_content.normalized_text
            )
            
            # Step 3: Per-ticker sentiment
            ticker_symbols = [t[0] for t in tickers]
            recommendations = []
            for ticker in ticker_symbols[:10]:  # Limit to top 10 tickers
                sentiment = self.sentiment_analyzer.analyze_ticker_sentiment(
                    preprocessed_content.normalized_text,
                    ticker
                )
                
                # Convert sentiment to action
                action = self._sentiment_to_action(sentiment)
                confidence = self._calculate_confidence(sentiment, ticker)
                
                # Use LLM to generate reason if available
                reason = self._generate_reason(ticker, sentiment, preprocessed_content)
                
                rec = Recommendation(
                    ticker=ticker,
                    action=action,
                    reason=reason,
                    confidence_score=confidence,
                    risk_level=self._assess_risk_level(sentiment),
                )
                recommendations.append(rec)
            
            # Step 4: Industry analysis
            industries = self._extract_industries_from_content(preprocessed_content)
            industry_trends = []
            for industry in industries:
                industry_sentiment = self.sentiment_analyzer.analyze_industry_sentiment(
                    preprocessed_content.normalized_text,
                    industry
                )
                
                trend = IndustryTrend(
                    industry_name=industry,
                    sentiment_score=industry_sentiment,
                    key_trends=self._extract_industry_trends(industry, preprocessed_content),
                )
                industry_trends.append(trend)
            
            # Step 5: Macro view
            macro_view = MacroView(
                overall_sentiment=overall_sentiment,
                key_drivers=self._extract_key_drivers(preprocessed_content),
            )
            
            # Step 6: Risk assessment
            key_risks = self._assess_risks(ticker_symbols, preprocessed_content)
            
            # Create result
            result = AnalysisResult(
                timestamp=datetime.utcnow(),
                sources=[source_title or source_id],
                macro_view=macro_view,
                industry_trends=industry_trends,
                recommendations=recommendations,
                key_risks=key_risks,
                metadata={
                    "source_id": source_id,
                    "entity_count": len(tickers),
                }
            )
            
            logger.info(f"Analysis completed for {source_id}: {len(recommendations)} recommendations")
            return result
        
        except Exception as e:
            logger.error(f"Error in analysis: {e}")
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
