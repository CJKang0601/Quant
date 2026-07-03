# AI 產業趨勢雷達:財經語音到趨勢洞察系統

## 📋 專案概述

自動追蹤三個財經內容來源(YouTube / Podcast),透過 AI 將非結構化的語音內容,
彙整成**短、中、長期的產業趨勢**。

> 設計目標是理解產業趨勢,**不是短線個股進出**。
> 個股只作為趨勢的佐證(例如台積電 CoWoS 擴產 = AI 供應鏈趨勢的訊號),系統不輸出 BUY/SELL 建議。

### 追蹤來源

| 來源 | 更新節奏 | 內容型態 |
|------|----------|----------|
| 財經皓角 | 每日早上 8:30 直播留檔 | 總經/盤勢日更 |
| 股癌 | 每週三、六 | 散戶視角產業討論 |
| 定錨產業筆記 | 不定期 | 法說會解讀/產業深度 |

### 核心流程

1. **數據攝取**:抓取 YouTube 字幕 / Podcast 音訊(`yt-dlp`, `feedparser`)
2. **語音轉文本**:faster-whisper(無字幕時)
3. **文本預處理**:字幕清理、財經黑話標註(GG→台積電(2330.TW))
4. **趨勢分析**:LLM map-reduce 全文分析 → 產業趨勢 + 時間尺度 + 佐證個股
5. **每日自動化**:GitHub Actions 排程(台灣 13:00),以 manifest 去重,結果發布到 GitHub Pages

---

## 🚀 快速開始

### 1. 環境設置

```bash
git clone https://github.com/CJKang0601/Quant.git
cd Quant

python -m venv venv
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### 2. 配置 API

```bash
cp .env.example .env
# 編輯 .env,填入 OPENAI_API_KEY(或 GOOGLE_API_KEY)
# 本機 ffmpeg 不在 PATH 時,可在 .env 設 FFMPEG_PATH=<ffmpeg bin 目錄>
```

GitHub Actions 使用的 repo secrets:`OPEN_AI_KEY`、`GEMINI_API_KEY`。

### 3. 使用

```bash
# 手動更新所有來源(已處理過的集數會自動跳過)
python update_all_sources.py

# 產生靜態網站(docs/index.html)
python generate_static_site.py

# 本機網頁介面
streamlit run app.py
```

---

## 📁 專案結構

```
Quant/
├── .github/workflows/         # 每日自動化(台灣 13:00)
├── config/
│   ├── settings.py            # 來源清單、模型、路徑設定
│   └── jargon_mapping.yaml    # 財經黑話映射
├── src/
│   ├── data_pipeline/         # 抓取、轉錄、預處理
│   ├── analysis_engine/       # LLM 趨勢分析(map-reduce)
│   └── utils/                 # Pydantic 模型、logger
├── data/
│   ├── processed/             # 分析結果 JSON
│   ├── processed_manifest.json# 已處理集數清單(去重用)
│   └── archive/               # 舊版格式的歷史結果
├── docs/index.html            # GitHub Pages 靜態儀表板
├── app.py                     # Streamlit 本機介面
├── update_all_sources.py      # 自動化更新腳本
└── generate_static_site.py    # 靜態網站產生器
```

---

## 📊 輸出格式

每集分析輸出的 JSON 核心結構:

```json
{
  "source_key": "gooaye",
  "content_date": "2026-07-01",
  "overall_summary": "150-200字本集摘要",
  "macro_view": {
    "overall_sentiment": 7.0,
    "key_drivers": ["AI 資本支出"]
  },
  "industry_trends": [
    {
      "industry_name": "半導體先進封裝",
      "sentiment_score": 8.0,
      "time_horizon": "LONG",
      "thesis": "CoWoS 產能是未來兩三年的結構性瓶頸與機會",
      "supporting_companies": [
        {
          "name": "台積電",
          "ticker": "2330.TW",
          "role_in_trend": "產能供應者",
          "quote": "CoWoS 明年翻倍"
        }
      ]
    }
  ],
  "key_risks": ["地緣政治"]
}
```

`time_horizon`:`SHORT`(0-3 個月)/ `MID`(3-18 個月)/ `LONG`(18 個月以上)。

---

## 🧪 測試

```bash
pytest tests/
```

包含 smoke test(所有進入點模組可 import)、預處理回歸測試(中文標點、CJK 黑話標註、字幕 metadata 清理)。

---

## 🔜 路線圖

- [ ] 趨勢時間軸視覺化:同一產業的情緒/提及次數隨時間變化
- [ ] 跨來源共識指標:三個來源同時提及的趨勢加權
- [ ] 趨勢 vs. 實際股價/產業指數的事後驗證

---

## 📄 許可證

MIT License
