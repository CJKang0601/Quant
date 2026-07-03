"""Main LLM Agent for industry-trend analysis.

分析目標:從財經節目逐字稿萃取「短中長期產業趨勢」。
個股只作為趨勢佐證,不輸出 BUY/SELL 操作建議。

長逐字稿採 map-reduce:先分段萃取趨勢筆記,再彙整成結構化 JSON。
"""
import json
import re
from typing import Optional, List, Dict, Any

from src.utils.logger import get_logger
from src.utils.data_models import (
    AnalysisResult,
    MacroView,
    IndustryTrend,
    CompanyMention,
    PreprocessedContent,
)
from src.analysis_engine.output_formatter import OutputFormatter
from config.settings import LLM_MODEL

logger = get_logger(__name__)

SEGMENT_CHAR_LIMIT = 12000  # 單次送進 LLM 的逐字稿字元上限
MAX_SEGMENTS = 10           # 最多分析段數(控制單集成本上限)

HORIZON_ALIASES = {
    "SHORT": "SHORT", "短期": "SHORT", "SHORT_TERM": "SHORT",
    "MID": "MID", "中期": "MID", "MEDIUM": "MID", "MID_TERM": "MID",
    "LONG": "LONG", "長期": "LONG", "LONG_TERM": "LONG",
}


def parse_llm_json(text: str) -> Dict[str, Any]:
    """Parse JSON from LLM output, tolerating markdown fences and surrounding prose."""
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end > start:
            return json.loads(text[start:end + 1])
        raise


MAP_PROMPT_TEMPLATE = """你是財經研究助理。以下是一集財經節目逐字稿的第 {index}/{total} 段。
請從中萃取與「產業趨勢」相關的重點筆記(條列),包括:
- 提到的產業與觀點(看多/看空、理由)
- 時間尺度線索:短期(0-3 個月)/中期(3-18 個月)/長期(18 個月以上)
- 被點名的公司與其在趨勢中的角色,附一句原文關鍵引述
- 總體經濟觀點與風險

只記錄逐字稿中實際講到的內容,不要自行推論補充。
如果本段沒有相關內容,輸出「(本段無產業趨勢相關內容)」。
輸出條列純文字,不要 JSON。

逐字稿段落:
{segment}"""

SYNTHESIS_PROMPT_TEMPLATE = """你是一位專業的產業研究員。以下是財經節目「{source_title}」的{material_label}。
這個系統的目的是追蹤短中長期的「產業趨勢」,不是個股進出建議。
請彙整內容,嚴格只輸出以下格式的 JSON 物件(不要 markdown 圍欄、不要其他文字):

{{
    "overall_summary": "150-200字的本集核心摘要",
    "macro_view": {{
        "overall_sentiment": 1到10的數字(1極悲觀、10極樂觀),
        "key_drivers": ["宏觀驅動因素1", "宏觀驅動因素2"],
        "global_outlook": "簡短全球展望"
    }},
    "industry_trends": [
        {{
            "industry_name": "產業名稱",
            "sentiment_score": 1到10的數字,
            "time_horizon": "SHORT 或 MID 或 LONG (SHORT=0-3個月, MID=3-18個月, LONG=18個月以上)",
            "thesis": "這個趨勢的核心論點,一兩句話",
            "key_trends": ["具體趨勢描述1", "具體趨勢描述2"],
            "growth_drivers": ["驅動因素"],
            "supporting_companies": [
                {{
                    "name": "公司名稱",
                    "ticker": "股票代號(如 2330.TW 或 NVDA),節目沒明講或不確定就填 null",
                    "market": "TW 或 US",
                    "role_in_trend": "該公司在這個趨勢中的角色",
                    "quote": "節目中提到該公司的關鍵原句"
                }}
            ]
        }}
    ],
    "key_risks": ["風險1", "風險2"],
    "discussed_companies": [
        {{"name": "未歸入趨勢但有被討論的公司", "description": "本集對該公司的描述"}}
    ],
    "jargon_explained": [
        {{"term": "黑話/術語", "explanation": "在本集中的含義"}}
    ]
}}

規則:
1. industry_trends 是最重要的輸出,每個趨勢都要判斷 time_horizon。
2. 個股一律放在 supporting_companies 作為趨勢佐證;不要輸出買賣建議。
3. 只根據提供的內容,不要編造節目沒講的資訊。
4. ticker 不確定時填 null,不要猜。
5. 已知黑話對照(輔助理解): {jargon_hint}

{material_label}:
{material}"""


class InvestmentAgent:
    """Agent for AI-driven industry-trend analysis."""

    def __init__(self, llm_provider: str = "openai"):
        """
        Initialize Investment Agent.

        Args:
            llm_provider: LLM provider ('openai' or 'google')
        """
        self.llm_provider = llm_provider
        self.formatter = OutputFormatter()
        self._initialize_llm()
        logger.info(f"InvestmentAgent initialized with {llm_provider} ({LLM_MODEL})")

    def _initialize_llm(self) -> None:
        """Initialize LLM client based on provider."""
        try:
            if self.llm_provider == "openai":
                from langchain_openai import ChatOpenAI
                self.llm = ChatOpenAI(model=LLM_MODEL, temperature=0.2)
            elif self.llm_provider == "google":
                from langchain_google_genai import ChatGoogleGenerativeAI
                self.llm = ChatGoogleGenerativeAI(model=LLM_MODEL, temperature=0.2)
            else:
                logger.warning(f"Unknown LLM provider: {self.llm_provider}")
                self.llm = None
        except ImportError:
            logger.warning(f"Could not import LLM client for {self.llm_provider}")
            self.llm = None

    def _invoke_text(self, prompt: str) -> str:
        """Invoke LLM and return plain-text content."""
        response = self.llm.invoke(prompt)
        content = response.content
        if isinstance(content, list):
            content = "".join(str(part) for part in content)
        return content

    def _extract_segment_notes(self, segments: List[str]) -> str:
        """Map stage: 逐段萃取產業趨勢筆記。"""
        notes = []
        for i, segment in enumerate(segments, start=1):
            prompt = MAP_PROMPT_TEMPLATE.format(index=i, total=len(segments), segment=segment)
            try:
                note = self._invoke_text(prompt)
                notes.append(f"【第 {i}/{len(segments)} 段筆記】\n{note}")
            except Exception as e:
                logger.error(f"Error extracting notes from segment {i}: {e}")
        return "\n\n".join(notes)

    @staticmethod
    def _normalize_horizon(raw: Any) -> str:
        return HORIZON_ALIASES.get(str(raw).strip().upper(), "MID")

    @staticmethod
    def _clamp_score(raw: Any, default: float = 5.5) -> float:
        try:
            return max(1.0, min(10.0, float(raw)))
        except (TypeError, ValueError):
            return default

    def _build_industry_trends(self, raw_trends: List[Dict[str, Any]]) -> List[IndustryTrend]:
        trends = []
        for item in raw_trends:
            if not isinstance(item, dict) or not item.get("industry_name"):
                continue
            companies = []
            for c in item.get("supporting_companies", []) or []:
                if isinstance(c, dict) and c.get("name"):
                    companies.append(CompanyMention(
                        name=str(c["name"]),
                        ticker=c.get("ticker") or None,
                        market=c.get("market") or None,
                        role_in_trend=str(c.get("role_in_trend", "")),
                        quote=c.get("quote") or None,
                    ))
            trends.append(IndustryTrend(
                industry_name=str(item["industry_name"]),
                sentiment_score=self._clamp_score(item.get("sentiment_score")),
                time_horizon=self._normalize_horizon(item.get("time_horizon")),
                thesis=str(item.get("thesis", "")),
                key_trends=[str(t) for t in item.get("key_trends", []) or []],
                growth_drivers=[str(d) for d in item.get("growth_drivers", []) or []],
                supporting_companies=companies,
            ))
        return trends

    @staticmethod
    def _clean_str_dicts(items: Any) -> List[Dict[str, str]]:
        cleaned = []
        for item in items or []:
            if isinstance(item, dict):
                cleaned.append({str(k): str(v) for k, v in item.items() if v is not None})
        return cleaned

    def analyze(
        self,
        preprocessed_content: PreprocessedContent,
        source_id: str,
        source_title: str = "",
        source_key: str = "",
        source_type: str = "youtube",
        content_date: Optional[str] = None,
    ) -> Optional[AnalysisResult]:
        """Full analysis: map-reduce over the transcript, output industry-trend JSON."""
        if not self.llm:
            logger.error("LLM not configured; cannot analyze. Check API keys and provider.")
            return None

        try:
            logger.info(f"Starting trend analysis for {source_id}")
            full_text = preprocessed_content.normalized_text
            jargon_hint = json.dumps(preprocessed_content.jargon_mappings, ensure_ascii=False)

            # Map stage: 長逐字稿分段萃取,短的直接進彙整
            segments = [
                full_text[i:i + SEGMENT_CHAR_LIMIT]
                for i in range(0, len(full_text), SEGMENT_CHAR_LIMIT)
            ][:MAX_SEGMENTS]

            if len(segments) <= 1:
                material_label = "逐字稿全文"
                material = full_text[:SEGMENT_CHAR_LIMIT]
            else:
                material_label = "分段趨勢筆記"
                material = self._extract_segment_notes(segments)
                if not material.strip():
                    logger.error(f"All segment extractions failed for {source_id}")
                    return None

            # Reduce stage: 彙整為結構化 JSON
            prompt = SYNTHESIS_PROMPT_TEMPLATE.format(
                source_title=source_title or source_id,
                material_label=material_label,
                jargon_hint=jargon_hint,
                material=material,
            )
            data = parse_llm_json(self._invoke_text(prompt))

            macro_raw = data.get("macro_view") or {}
            macro = MacroView(
                overall_sentiment=self._clamp_score(macro_raw.get("overall_sentiment")),
                key_drivers=[str(d) for d in macro_raw.get("key_drivers", []) or []],
                global_outlook=macro_raw.get("global_outlook"),
            )

            result = AnalysisResult(
                source_key=source_key,
                source_id=source_id,
                source_title=source_title or source_id,
                source_type=source_type,
                content_date=content_date,
                overall_summary=str(data.get("overall_summary", "")),
                macro_view=macro,
                industry_trends=self._build_industry_trends(data.get("industry_trends", []) or []),
                key_risks=[str(r) for r in data.get("key_risks", []) or []],
                discussed_companies=self._clean_str_dicts(data.get("discussed_companies")),
                jargon_explained=self._clean_str_dicts(data.get("jargon_explained")),
                metadata={
                    "source_id": source_id,
                    "transcript_chars": len(full_text),
                    "segments_analyzed": len(segments),
                },
            )

            logger.info(f"Analysis completed for {source_id}: {len(result.industry_trends)} trends")
            return result

        except Exception as e:
            logger.error(f"Error in trend analysis for {source_id}: {e}")
            return None
