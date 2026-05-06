# AI Investment Agent: 財經語音到量化決策系統

## 📋 專案概述

這是一個完整的 AI 驅動投資研究系統，將非結構化的財經語音內容轉換為結構化的投資建議。

### 核心功能
- ✅ **數據攝取**：自動抓取 YouTube 和 Podcast 音訊
- ✅ **語音轉文本**：使用 OpenAI Whisper 進行轉錄
- ✅ **文本預處理**：財經黑話映射、實體識別、分塊
- ✅ **智能分析**：情緒分析、實體匹配、結構化輸出
- 🔄 **量化驗證**（Phase 2）：回測框架、風險評估
- 🔄 **資金控管**（Phase 3）：Kelly 公式、部位規模

---

## 🚀 快速開始

### 1. 環境設置

```bash
# Clone 項目
git clone https://github.com/CJKang0601/Quant.git
cd Quant

# 創建虛擬環境
python -m venv venv
venv\Scripts\activate  # Windows

# 安裝依賴
pip install -r requirements.txt
```

### 2. 配置 API

```bash
# 複製環境範本
cp .env.example .env

# 編輯 .env，填入你的 API 密鑰
# OPENAI_API_KEY=your_key_here
# GOOGLE_API_KEY=your_key_here
```

### 3. 使用示例

#### 啟動網站介面

```bash
streamlit run app.py
```

#### 手動更新資料

```python
python update_all_sources.py
```

---

## 📁 專案結構

```
sideproject/
├── .github/workflows/         # GitHub Actions 自動化
├── config/                    # 配置文件
│   ├── settings.py           # 全局設置
│   └── jargon_mapping.yaml   # 財經黑話映射
├── src/
│   ├── data_pipeline/        # A. 數據攝取 & 預處理
│   ├── analysis_engine/      # B. 智能分析層
│   └── utils/                # 工具類
├── app.py                    # Streamlit 網頁主程式
├── main.py                   # 主進入點
├── update_all_sources.py     # 自動化更新腳本
├── sdd.md                    # 系統設計文檔
└── README.md                 # 本文件
```

---

## 🔧 核心模塊說明

### A. 數據攝取 (Data Pipeline)

| 模塊 | 功能 | 技術棧 |
|------|------|--------|
| `youtube_fetcher.py` | 抓取 YouTube 影片 | `yt-dlp` |
| `podcast_fetcher.py` | 抓取 Podcast 集數 | `feedparser`, `requests` |
| `transcriber.py` | 語音轉文本 | `Whisper`, `Faster-Whisper` |
| `preprocessor.py` | 文本清理、黑話映射、分塊 | `regex`, `YAML` |

### B. 智能分析 (Analysis Engine)

| 模塊 | 功能 |
|------|------|
| `agent.py` | 主 Agent，協調整個分析流程 |
| `sentiment_analyzer.py` | 情緒分析（1-10 分數）|
| `entity_matcher.py` | 實體識別、RAG 檢索 |
| `output_formatter.py` | JSON 格式化、CSV 導出 |

---

## 📊 輸出格式

Agent 分析輸出的 JSON 結構：

```json
{
  "timestamp": "2026-04-29T20:00:00Z",
  "sources": ["Hao_Ep123"],
  "macro_view": {
    "overall_sentiment": 7.5,
    "key_drivers": ["Fed policy", "Earnings growth"]
  },
  "recommendations": [
    {
      "ticker": "2330.TW",
      "action": "BUY",
      "reason": "AI Server 需求超出預期",
      "confidence_score": 0.88
    }
  ]
}
```

---

## 🧪 測試

```bash
# 運行測試
pytest tests/
```

---

## 🔜 Phase 2-3 路線圖

### Phase 2: 量化驗證（準備中）
- [ ] 基本回測引擎
- [ ] L4 Bonferroni 多重檢定校正
- [ ] L6 市況分層測試
- [ ] L7 交叉驗證

### Phase 3: 資金控管（準備中）
- [ ] Kelly 公式實現
- [ ] 風險限額邏輯
- [ ] 部位規模計算

---

## 📄 許可證

MIT License
