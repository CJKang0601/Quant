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
cd d:\CJK\114-2\sideproject

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

#### 處理本地音訊檔

```python
from main import MainPipeline

pipeline = MainPipeline()
pipeline.process_local_audio("path/to/audio.mp3", source_type="youtube")
```

#### 自動抓取 YouTube 影片

```python
pipeline.process_youtube_channel(
    channel_url="https://www.youtube.com/@YourChannel",
    max_videos=3
)
```

#### 自動抓取 Podcast

```python
pipeline.process_podcast_feed(
    feed_url="https://example.com/podcast/feed.xml",
    max_episodes=3
)
```

---

## 📁 專案結構

```
sideproject/
├── config/                    # 配置文件
│   ├── settings.py           # 全局設置
│   └── jargon_mapping.yaml   # 財經黑話映射
├── src/
│   ├── data_pipeline/        # A. 數據攝取 & 預處理
│   │   ├── youtube_fetcher.py
│   │   ├── podcast_fetcher.py
│   │   ├── transcriber.py
│   │   └── preprocessor.py
│   ├── analysis_engine/      # B. 智能分析層
│   │   ├── agent.py
│   │   ├── sentiment_analyzer.py
│   │   ├── entity_matcher.py
│   │   └── output_formatter.py
│   └── utils/
│       ├── data_models.py    # Pydantic 模型
│       ├── logger.py
│       └── vector_db.py      # RAG 向量數據庫
├── data/
│   ├── raw/                  # 下載的音訊檔
│   └── processed/            # 分析結果 JSON
├── tests/                    # 測試文件
├── notebooks/                # Jupyter 實驗筆記
├── main.py                   # 主進入點
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

**範例：處理音訊文件**
```python
from src.data_pipeline.transcriber import WhisperTranscriber
from src.data_pipeline.preprocessor import TextPreprocessor

# 轉錄
transcriber = WhisperTranscriber(model_size="base")
result = transcriber.transcribe("audio.mp3", language="zh")

# 預處理
preprocessor = TextPreprocessor()
preprocessed = preprocessor.preprocess(transcription)
```

### B. 智能分析 (Analysis Engine)

| 模塊 | 功能 |
|------|------|
| `agent.py` | 主 Agent，協調整個分析流程 |
| `sentiment_analyzer.py` | 情緒分析（1-10 分數）|
| `entity_matcher.py` | 實體識別、RAG 檢索 |
| `output_formatter.py` | JSON 格式化、CSV 導出 |

**範例：運行分析**
```python
from src.analysis_engine.agent import InvestmentAgent

agent = InvestmentAgent(llm_provider="openai")
result = agent.analyze(preprocessed_content, source_id="youtube_1")

# 輸出
from src.analysis_engine.output_formatter import OutputFormatter
formatter = OutputFormatter()
json_output = formatter.format_analysis_to_json(result)
formatter.save_analysis_json(result, "output.json")
```

---

## 📊 輸出格式

Agent 分析輸出的 JSON 結構：

```json
{
  "timestamp": "2026-04-29T20:00:00Z",
  "sources": ["Hao_Ep123"],
  "macro_view": {
    "overall_sentiment": 7.5,
    "key_drivers": ["Fed policy", "Earnings growth"],
    "global_outlook": null
  },
  "industry_trends": [
    {
      "industry_name": "Semiconductors",
      "sentiment_score": 8.2,
      "key_trends": ["AI demand", "CoWoS expansion"],
      "growth_drivers": []
    }
  ],
  "recommendations": [
    {
      "ticker": "2330.TW",
      "action": "BUY",
      "reason": "AI Server 需求超出預期",
      "confidence_score": 0.88,
      "target_price": null,
      "risk_level": "MEDIUM"
    }
  ],
  "key_risks": ["Supply chain disruption", "Geopolitical tensions"],
  "risk_management": {
    "overall_exposure_limit": "60%",
    "suggested_stop_loss": "-8%",
    "suggested_take_profit": null
  },
  "raw_analysis": null,
  "metadata": {"source_id": "youtube_1", "entity_count": 5}
}
```

---

## 🎯 財經黑話映射

系統包含預定義的黑話映射（`config/jargon_mapping.yaml`）：

| 黑話 | 映射 | 類型 |
|------|------|------|
| 發哥 | 聯發科 (2454.TW) | 人物 → 股票 |
| GG | 台積電 (2330.TW) | 暗語 → 股票 |
| 老謝 | 台積電 (2330.TW) | 人物 → 股票 |
| NVDA | NVIDIA | 股票 → 公司 |

**自定義映射**：編輯 `config/jargon_mapping.yaml` 添加新的黑話。

---

## 🧪 測試

```bash
# 運行測試
pytest tests/

# 查看覆蓋率
pytest --cov=src tests/
```

---

## 📝 使用日誌

所有操作都會記錄到控制台和日誌文件（可在 `config/settings.py` 中配置）。

```python
from src.utils.logger import get_logger

logger = get_logger(__name__)
logger.info("Processing started")
logger.error("Error occurred")
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
- [ ] 實時監控儀表板

---

## 📚 依賴說明

### 核心依賴
- `langchain` - LLM 框架
- `openai-whisper` / `faster-whisper` - 語音轉文本
- `yt-dlp` - YouTube 下載
- `feedparser` - Podcast RSS
- `pydantic` - 數據驗證
- `chromadb` / `pinecone` - 向量數據庫

### 可選依賴
- `jupyter` - 分析筆記本
- `pytest` - 測試框架
- `python-logging-loki` - 日誌聚合

---

## 🤝 貢獻

如有改進建議，請提交 PR 或 issue。

---

## 📄 許可證

MIT License

---

## 📞 聯絡方式

如有問題，請參考 `sdd.md` 或聯絡開發團隊。
