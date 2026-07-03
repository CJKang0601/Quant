import streamlit as st
import json
from pathlib import Path
from datetime import datetime

from config.settings import SOURCE_INFO

# 設置頁面配置
st.set_page_config(
    page_title="AI 產業趨勢雷達 - 財經資訊彙整",
    page_icon="📡",
    layout="wide"
)

DATA_DIR = Path("data/processed")

HORIZON_LABELS = {
    "SHORT": "🟡 短期 (0-3月)",
    "MID": "🔵 中期 (3-18月)",
    "LONG": "🟢 長期 (18月+)",
}

# 顯示分區(股癌 YouTube 與 Podcast 合併)
PAGES = {
    "hao": "📺 財經皓角",
    "gooaye": "🎙️ 股癌",
    "market_anchor": "⚓ 定錨產業",
}


def load_analysis_files():
    """載入所有已處理的 JSON 分析檔案"""
    files = list(DATA_DIR.glob("analysis_*.json"))
    data = []
    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as file:
                content = json.load(file)
                source_key = content.get("source_key")
                if not source_key:
                    for key in ("hao", "gooaye", "market"):
                        if key in f.name.lower():
                            source_key = "market_anchor" if key == "market" else key
                            break
                if source_key == "gooaye_podcast":
                    source_key = "gooaye"
                content["_source_key"] = source_key or "unknown"
                content["_filename"] = f.name
                content["_display_date"] = content.get("content_date") or content.get("timestamp", "").split("T")[0]
                data.append(content)
        except Exception as e:
            st.error(f"讀取檔案 {f.name} 時發生錯誤: {e}")

    return sorted(data, key=lambda x: x.get("content_date") or x.get("timestamp", ""), reverse=True)


def render_trend(trend):
    """渲染單一產業趨勢"""
    horizon = HORIZON_LABELS.get(trend.get("time_horizon", "MID"), trend.get("time_horizon", ""))
    score = trend.get("sentiment_score", 5.5)
    st.markdown(f"**{trend.get('industry_name', '')}** {horizon} | 情緒 {round(score, 1)}/10")
    if trend.get("thesis"):
        st.write(trend["thesis"])
    for t in trend.get("key_trends", []):
        st.write(f"  • {t}")
    for c in trend.get("supporting_companies", []):
        ticker = f" ({c['ticker']})" if c.get("ticker") else ""
        st.caption(f"佐證個股: {c.get('name', '')}{ticker} — {c.get('role_in_trend', '')}")
        if c.get("quote"):
            st.caption(f"> {c['quote']}")
    st.divider()


def render_analysis_card(analysis):
    """渲染單一分析報告的內容"""
    title = analysis.get("source_title", "")[:50]
    with st.expander(f"📅 {analysis.get('_display_date', '未知日期')} - {title}", expanded=True):
        if analysis.get("overall_summary"):
            st.info(analysis["overall_summary"])

        col1, col2 = st.columns([1, 2])

        with col1:
            st.subheader("📊 宏觀情緒")
            macro = analysis.get("macro_view") or {}
            if macro:
                score = macro.get("overall_sentiment", 5)
                st.metric("樂觀分數", f"{round(score, 1)}/10")
                st.write("**關鍵驅動因素:**")
                for driver in macro.get("key_drivers", []):
                    st.write(f"- {driver}")
                if macro.get("global_outlook"):
                    st.caption(macro["global_outlook"])
            else:
                st.write("無宏觀數據")

            st.subheader("⚠️ 風險提示")
            for risk in analysis.get("key_risks", []):
                st.write(f"- {risk}")

        with col2:
            st.subheader("📡 產業趨勢")
            trends = analysis.get("industry_trends", [])
            if trends:
                for trend in trends:
                    render_trend(trend)
            else:
                st.write("本集無明確產業趨勢內容。")

        col3, col4 = st.columns(2)
        with col3:
            companies = analysis.get("discussed_companies", [])
            if companies:
                st.subheader("🏢 其他討論公司")
                for c in companies:
                    st.write(f"**{c.get('name', '')}**: {c.get('description', '')}")
        with col4:
            jargon = analysis.get("jargon_explained", [])
            if jargon:
                st.subheader("📖 黑話百科")
                for j in jargon:
                    st.write(f"**{j.get('term', '')}**: {j.get('explanation', '')}")


# Sidebar 導航
st.sidebar.title("📡 產業趨勢雷達")
page = st.sidebar.radio("請選擇頁面", ["🏠 總覽首頁"] + list(PAGES.values()))

# 載入數據
all_data = load_analysis_files()

if page == "🏠 總覽首頁":
    st.title("📡 財經資訊產業趨勢總覽")
    st.write("自動追蹤三個來源的 YouTube/Podcast 內容,透過 AI 提煉短中長期產業趨勢。個股僅作為趨勢佐證,非投資建議。")
    for key, info in SOURCE_INFO.items():
        if key != "gooaye_podcast":
            st.caption(f"• {info['name']}: {info['cadence']}")

    if not all_data:
        st.warning("目前尚無分析數據,請先運行資料抓取腳本。")
        st.code("python update_all_sources.py")
    else:
        st.header("✨ 最新分析動態")
        for i in range(min(3, len(all_data))):
            render_analysis_card(all_data[i])
else:
    source_key = next(k for k, v in PAGES.items() if v == page)
    st.title(f"{page} - 分析歷史")
    source_data = [d for d in all_data if d["_source_key"] == source_key]
    if not source_data:
        st.info("尚無此來源的分析資料。")
    else:
        for d in source_data:
            render_analysis_card(d)

# 頁腳
st.sidebar.divider()
st.sidebar.info(f"最後更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
