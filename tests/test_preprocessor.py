"""Regression tests for preprocessor bugs:
1. clean_text 不可清掉中文標點(句子切分依賴 。！？)
2. 中文黑話必須能在句中被標註(\\b 對 CJK 無效的舊 bug)
3. VTT 字幕的 metadata 行必須清除(舊資料曾把 'Kind: captions' 當內容分析)
4. ticker 抽取不可把 OK/TW/AI 等常見縮寫當股票
"""
from src.data_pipeline.preprocessor import TextPreprocessor, JargonMapper


def test_clean_text_preserves_chinese_punctuation():
    p = TextPreprocessor()
    cleaned = p.clean_text("台積電很強。但是要小心！你說對嗎？")
    assert "。" in cleaned
    assert "！" in cleaned
    sentences = p.segment_sentences(cleaned)
    assert len(sentences) == 3


def test_clean_text_preserves_ticker_dots():
    p = TextPreprocessor()
    cleaned = p.clean_text("2330.TW 目標價上調 3.5%。")
    assert "2330.TW" in cleaned
    assert "3.5%" in cleaned


def test_clean_text_strips_vtt_metadata():
    p = TextPreprocessor()
    vtt = "WEBVTT\nKind: captions\nLanguage: zh-TW\n00:00:00.000 --> 00:00:05.000\n大家好\n"
    cleaned = p.clean_text(vtt)
    assert "captions" not in cleaned
    assert "zh-TW" not in cleaned
    assert "大家好" in cleaned


def test_jargon_annotation_works_in_chinese_sentences():
    mapper = JargonMapper()
    # 中文詞夾在句中(前後都是 CJK 字元)也要能標註
    normalized, applied = mapper.normalize_text("我覺得台積電第四季會很強")
    assert "台積電(2330.TW)" in normalized
    assert applied.get("台積電") == "2330.TW"

    # ASCII 黑話仍要求邊界,不可誤中英文單字的一部分
    normalized2, applied2 = mapper.normalize_text("EGGS are not GG")
    assert "EGGS(2330.TW)" not in normalized2
    assert applied2.get("GG") == "2330.TW"


def test_jargon_annotation_no_double_replacement():
    mapper = JargonMapper()
    # 「台積電」標註後,別名「台積」不可在結果上二次標註
    normalized, _ = mapper.normalize_text("台積電")
    assert normalized == "台積電(2330.TW)"


def test_extract_entities_filters_common_acronyms():
    p = TextPreprocessor()
    entities = p.extract_entities("OK 這個 AI 趨勢下 2330.TW 和 NVDA 都受惠")
    assert "2330.TW" in entities
    assert "NVDA" in entities
    assert "OK" not in entities
    assert "AI" not in entities
