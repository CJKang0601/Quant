import streamlit as st
import json
import os
import pandas as pd
from pathlib import Path
from datetime import datetime

# 設置頁面配置
st.set_page_config(
    page_title="AI 投資研究助理 - 財經資訊彙整",
    page_icon="📈",
    layout="wide"
)

# 常數定義
DATA_DIR = Path("data/processed")
SOURCES = {
    "hao": "財經皓角",
    "gooaye": "股癌",
    "market_anchor": "市場錨定"
}

def load_analysis_files():
    """載入所有已處理的 JSON 分析檔案"""
    files = list(DATA_DIR.glob("*.json"))
    data = []
    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as file:
                content = json.load(file)
                # 簡單識別來源
                source_key = "unknown"
                for key in SOURCES.keys():
                    if key in f.name.lower():
                        source_key = key
                        break
                
                content["_source_key"] = source_key
                content["_filename"] = f.name
                data.append(content)
        except Exception as e:
            st.error(f"讀取檔案 {f.name} 時發生錯誤: {e}")
    
    # 按時間排序
    return sorted(data, key=lambda x: x.get("timestamp", ""), reverse=True)

def render_recommendations(recs):
    """渲染投資建議表格"""
    if not recs:
        st.info("本次分析無具體個股建議。")
        return
    
    df = pd.DataFrame(recs)
    # 格式化顯示
    display_df = df.copy()
    if "confidence_score" in display_df.columns:
        display_df["confidence_score"] = display_df["confidence_score"].apply(lambda x: f"{x:.0%}")
    
    st.table(display_df)

def render_analysis_card(analysis):
    """渲染單一分析報告的內容"""
    with st.expander(f"📅 {analysis.get('timestamp', '未知時間')} - {', '.join(analysis.get('sources', []))}", expanded=True):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("📊 宏觀情緒")
            macro = analysis.get("macro_view", {})
            if macro:
                score = macro.get("overall_sentiment", 5)
                st.metric("樂觀分數", f"{score}/10")
                st.write("**關鍵驅動因素:**")
                for driver in macro.get("key_drivers", []):
                    st.write(f"- {driver}")
            else:
                st.write("無宏觀數據")

        with col2:
            st.subheader("💡 核心觀點與建議")
            render_recommendations(analysis.get("recommendations", []))
            
        st.divider()
        
        col3, col4 = st.columns(2)
        with col3:
            st.subheader("🏭 產業趨勢")
            for trend in analysis.get("industry_trends", []):
                st.write(f"**{trend.get('industry_name')}** (得分: {trend.get('sentiment_score')}/10)")
                for t in trend.get("key_trends", []):
                    st.write(f"  • {t}")
        
        with col4:
            st.subheader("⚠️ 風險提示")
            for risk in analysis.get("key_risks", []):
                st.write(f"- {risk}")

# Sidebar 導航
st.sidebar.title("🚀 投資 AI 助理")
page = st.sidebar.radio("請選擇頁面", ["🏠 總覽首頁", "📺 財經皓角", "🎙️ 股癌", "⚓ 市場錨定"])

# 載入數據
all_data = load_analysis_files()

if page == "🏠 總覽首頁":
    st.title("📊 財經資訊智能彙整總覽")
    st.write("本系統自動追蹤 YouTube 與 Podcast 內容，並透過 AI 提煉結構化投資觀點。")
    
    if not all_data:
        st.warning("目前尚無分析數據，請先運行資料抓取腳本。")
        st.code("python example_usage.py")
    else:
        # 顯示最新三條
        st.header("✨ 最新分析動態")
        for i in range(min(3, len(all_data))):
            render_analysis_card(all_data[i])

elif page == "📺 財經皓角":
    st.title("📺 財經皓角 - 分析歷史")
    source_data = [d for d in all_data if d["_source_key"] == "hao"]
    if not source_data:
        st.info("尚無財經皓角的分析資料。")
    else:
        for d in source_data:
            render_analysis_card(d)

elif page == "🎙️ 股癌":
    st.title("🎙️ 股癌 - 分析歷史")
    source_data = [d for d in all_data if d["_source_key"] == "gooaye"]
    if not source_data:
        st.info("尚無股癌的分析資料。")
    else:
        for d in source_data:
            render_analysis_card(d)

elif page == "⚓ 市場錨定":
    st.title("⚓ 市場錨定 - 分析歷史")
    source_data = [d for d in all_data if d["_source_key"] == "market_anchor"]
    if not source_data:
        st.info("尚無市場錨定的分析資料。")
    else:
        for d in source_data:
            render_analysis_card(d)

# 頁腳
st.sidebar.divider()
st.sidebar.info(f"最後更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
