"""Smoke tests: 確保核心模組能 import、模型能建構、JSON 解析穩健。

這類 import 級的錯誤過去讓整條 pipeline 掛掉近兩個月而測試沒抓到,
所以這裡直接 import 所有進入點模組。
"""
import json
import pytest


def test_import_entry_points():
    """所有進入點模組必須能 import(擋 ImportError 級災難)。"""
    import main  # noqa: F401
    import update_all_sources  # noqa: F401
    import generate_static_site  # noqa: F401
    from src.analysis_engine.agent import InvestmentAgent  # noqa: F401
    from src.analysis_engine.output_formatter import OutputFormatter  # noqa: F401


def test_analysis_result_roundtrip():
    """AnalysisResult 建構與 JSON 序列化。"""
    from src.utils.data_models import (
        AnalysisResult, MacroView, IndustryTrend, CompanyMention, TimeHorizon,
    )
    from src.analysis_engine.output_formatter import OutputFormatter

    result = AnalysisResult(
        source_key="gooaye",
        source_id="gooaye_abc123",
        source_title="測試集數",
        source_type="podcast",
        content_date="2026-07-01",
        overall_summary="測試摘要",
        macro_view=MacroView(overall_sentiment=6.5, key_drivers=["Fed 政策"]),
        industry_trends=[
            IndustryTrend(
                industry_name="半導體",
                sentiment_score=8.0,
                time_horizon=TimeHorizon.LONG,
                thesis="AI 供應鏈長期擴張",
                supporting_companies=[
                    CompanyMention(name="台積電", ticker="2330.TW", market="TW",
                                   role_in_trend="先進封裝產能供應者"),
                ],
            ),
        ],
    )

    data = json.loads(OutputFormatter.format_analysis_to_json(result))
    assert data["industry_trends"][0]["time_horizon"] == "LONG"
    assert data["industry_trends"][0]["supporting_companies"][0]["ticker"] == "2330.TW"
    assert "recommendations" not in data  # 不再輸出個股操作建議

    summary = OutputFormatter.create_summary(result)
    assert summary["horizon_counts"]["LONG"] == 1

    display = OutputFormatter.format_for_display(result)
    assert "半導體" in display


def test_parse_llm_json_tolerates_fences():
    """LLM 回應常包 markdown 圍欄或夾雜文字,解析必須容忍。"""
    from src.analysis_engine.agent import parse_llm_json

    assert parse_llm_json('{"a": 1}') == {"a": 1}
    assert parse_llm_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert parse_llm_json('好的,以下是結果:\n{"a": 1}\n以上。') == {"a": 1}
    with pytest.raises(json.JSONDecodeError):
        parse_llm_json("這不是 JSON")


def test_horizon_normalization():
    """LLM 可能回傳中文或變體的 time_horizon,需正規化。"""
    from src.analysis_engine.agent import InvestmentAgent

    assert InvestmentAgent._normalize_horizon("SHORT") == "SHORT"
    assert InvestmentAgent._normalize_horizon("短期") == "SHORT"
    assert InvestmentAgent._normalize_horizon("long") == "LONG"
    assert InvestmentAgent._normalize_horizon("看不懂的值") == "MID"
    assert InvestmentAgent._clamp_score(15) == 10.0
    assert InvestmentAgent._clamp_score(None) == 5.5
