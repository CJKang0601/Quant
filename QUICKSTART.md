# 🚀 快速入門指南

## 5 分鐘開始使用 AI Investment Agent

### 步驟 1: 環境準備

```bash
# 進入項目目錄
cd d:\CJK\114-2\sideproject

# 創建虛擬環境
python -m venv venv

# 啟動虛擬環境
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# 安裝依賴
pip install -r requirements.txt
```

### 步驟 2: 配置 API 密鑰

```bash
# 複製環境文件
copy .env.example .env

# 編輯 .env 文件，填入你的 API 密鑰
# OPENAI_API_KEY=sk-...
# GOOGLE_API_KEY=...
```

### 步驟 3: 測試系統

#### 方式 A：分析示例文本（不需要音訊檔）

```python
# 運行示例代碼
python example_usage.py
```

這會輸出：
- 情緒分析結果（1-10 分數）
- 股票建議（BUY/SELL/HOLD）
- 風險評估
- JSON 格式結果

#### 方式 B：處理本地音訊檔

```python
from main import MainPipeline

pipeline = MainPipeline()
pipeline.process_local_audio(
    audio_path="your_audio.mp3",
    source_type="youtube"
)
```

#### 方式 C：自動抓取 YouTube（需要下載工具）

```python
from main import MainPipeline

pipeline = MainPipeline()
pipeline.process_youtube_channel(
    channel_url="https://www.youtube.com/@YourChannel",
    max_videos=3
)
```

---

## 📊 快速範例

### 1. 基本情緒分析

```python
from src.analysis_engine.sentiment_analyzer import SentimentAnalyzer

analyzer = SentimentAnalyzer()

text = "台積電看好強勢，推薦買進"
score = analyzer.analyze_text_sentiment(text, language='zh')

print(f"情緒分數: {score:.1f}/10")  # 輸出: 8.5/10
```

### 2. 黑話映射

```python
from src.data_pipeline.preprocessor import JargonMapper

mapper = JargonMapper()

ticker = mapper.get_ticker("GG")
print(f"GG → {ticker}")  # 輸出: GG → 2330.TW
```

### 3. 實體識別

```python
from src.analysis_engine.entity_matcher import EntityMatcher

matcher = EntityMatcher()

text = "台積電（2330）和聯發科（2454）都表現強勢"
tickers = matcher.extract_ticker_mentions(text)

print(f"發現的股票: {[t[0] for t in tickers]}")
# 輸出: 發現的股票: ['2330', '2454']
```

### 4. 完整分析流程

```python
from src.utils.data_models import TranscriptionResult
from src.data_pipeline.preprocessor import TextPreprocessor
from src.analysis_engine.agent import InvestmentAgent
from src.analysis_engine.output_formatter import OutputFormatter

# 創建轉錄結果
transcription = TranscriptionResult(
    source_id="demo",
    source_type="youtube",
    source_title="Analysis Demo",
    transcript="台積電看好，AI Server 需求超出預期...",
    duration_seconds=600,
)

# 預處理
preprocessor = TextPreprocessor()
preprocessed = preprocessor.preprocess(transcription)

# 分析
agent = InvestmentAgent()
result = agent.analyze(preprocessed, "demo", "Demo")

# 輸出
formatter = OutputFormatter()
print(formatter.format_for_display(result))

# 保存
formatter.save_analysis_json(result, "output.json")
```

---

## 📁 重要文件位置

| 文件 | 用途 |
|------|------|
| `main.py` | 主程序進入點 |
| `example_usage.py` | 使用示例 |
| `config/settings.py` | 全局配置 |
| `config/jargon_mapping.yaml` | 黑話映射表 |
| `.env` | API 密鑰（需自行創建） |
| `data/raw/` | 下載的音訊檔 |
| `data/processed/` | 分析結果 JSON |

---

## 🔧 常見問題

### Q1: 如何修改黑話映射？

編輯 `config/jargon_mapping.yaml`：

```yaml
台灣股票:
  "你的黑話":
    ticker: "2330.TW"
    name: "台積電"
    aliases: ["別名1", "別名2"]
```

### Q2: 如何使用不同的 LLM？

編輯 `src/analysis_engine/agent.py` 的 `_initialize_llm()` 方法，或在初始化時指定：

```python
agent = InvestmentAgent(llm_provider="google")  # 使用 Gemini
```

### Q3: 如何改變情緒分析的敏感度？

編輯 `src/analysis_engine/sentiment_analyzer.py` 的關鍵詞列表。

### Q4: 分析結果保存在哪裡？

所有 JSON 結果保存在 `data/processed/` 目錄。

### Q5: 如何測試沒有 API 密鑰？

運行 `example_usage.py`，它使用示例文本，不需要 API 密鑰。

---

## 🧪 執行測試

```bash
# 安裝測試依賴
pip install pytest pytest-cov

# 運行所有測試
pytest tests/

# 查看覆蓋率
pytest --cov=src tests/
```

---

## 📈 下一步

1. **配置你的 API 密鑰** → 使用真實 LLM
2. **準備音訊內容** → 本地、YouTube 或 Podcast
3. **運行完整分析** → 生成投資建議
4. **定制黑話映射** → 添加你的術語
5. **Phase 2** → 添加量化驗證（稍後）

---

## 💡 提示

- 情緒分數 8-10：非常樂觀，建議 BUY
- 情緒分數 6-8：樂觀，建議 HOLD
- 情緒分數 4-6：中立
- 情緒分數 2-4：悲觀，建議 SELL
- 情緒分數 1-2：非常悲觀，強烈建議 SELL

---

## 📞 需要幫助？

參考以下文件：
- `README.md` - 完整文檔
- `sdd.md` - 系統設計規格
- `example_usage.py` - 詳細代碼範例

祝你使用愉快！ 🚀
