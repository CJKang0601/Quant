# AI Investment Agent: 從非結構化財經語音到量化決策系統

## 1. 專案願景
本專案旨在建立一套自動化的投資研究流程。系統將抓取特定財經講者（股癌、皓哥、市場錨定）的影音內容，透過大語言模型（LLM）與 Agent 進行語意分析與結構化資訊萃取，最終結合嚴謹的量化回測框架（L0-L10）與風險控管邏輯，產出可執行的台美股投資建議。

---

## 2. 系統架構 (System Architecture)

### A. 數據攝取與預處理 (Data Ingestion & Preprocessing)
* **目標：** 自動化抓取 YouTube (皓哥) 與 Podcast (股癌) 音訊。
* **技術棧：** `yt-dlp`, `feedparser`, `OpenAI Whisper` (or Faster-Whisper)。
* **核心功能：**
    * 定期監測 RSS Feed 與 YouTube 頻道。
    * Speech-to-Text (STT) 轉錄。
    * **財經黑話映射 (Jargon Mapping)：** 處理如「發哥 -> 聯發科 (2454)」、「GG -> 台積電 (2330)」等非標準名稱。

### B. 智能分析層 (Intelligence Layer - Agentic Workflow)
* **目標：** 模擬 NotebookLM 的分析能力，提煉核心觀點。
* **技術棧：** `LangChain` / `LlamaIndex`, `Gemini Pro` / `Claude 3.5 Sonnet`。
* **Agent 任務：**
    * **情緒分析 (Sentiment Analysis)：** 針對不同產業/個股計算樂觀分數 (1-10)。
    * **實體識別與配對 (Entity Matching & RAG)：** 透過 RAG 檢索向量資料庫（含台美股基本面資料），精準匹配講者提到的標的。
    * **觀點結構化：** 輸出 JSON 格式，包含 `Macro_View`, `Industry_Trend`, `Specific_Tickers`, `Key_Risks`。

### C. 量化回測與驗證框架 (Quant Validation - L0-L10)
* **目標：** 證明 AI 提煉的訊號具備統計顯著性，防止過度擬合。
* **實作重點 (參照機構級框架)：**
    * **L0-L1:** 基本回測與滾動測試 (Walk-Forward)。
    * **L4 Bonferroni 校正：** 針對多重因子組合進行假設檢定校正。
    * **L6 市況分層測試 (Regime Analysis)：** 區分牛/熊/盤整市況下的訊號表現。
    * **L7 Combinatorial Purged CV：** 使用組合式淨化交叉驗證，防止數據洩漏。

### D. 資金控管與風險管理 (Risk Management)
* **目標：** 結合 LLM 策略與數學邏輯計算部位。
* **邏輯：**
    * **Input:** 當前資金水位 (Cash Level)、標的波動率 (Volatility)。
    * **Formula:** 使用凱利公式 (Kelly Criterion) 或 固定風險比例 (Fixed Fractional) 計算建議買入股數。
    * **Output:** 具體的停損點 (Stop-loss) 與停利點 (Take-profit)。

---

## 3. 數據架構 (Data Schema Example)

Agent 分析後輸出的結構化 JSON 範例：
```json
{
  "timestamp": "2026-04-29T20:00:00Z",
  "sources": ["Gooaye_Ep450", "Hao_Morning_Live"],
  "market_sentiment": 0.75,
  "recommendations": [
    {
      "ticker": "2330.TW",
      "action": "BUY",
      "reason": "AI Server 需求超出預期，CoWoS 產能持續擴張",
      "confidence_score": 0.88
    }
  ],
  "risk_management": {
    "overall_exposure_limit": "60%",
    "suggested_stop_loss": "-8%"
  }
}
```

---

## 4. 實現階段

### Phase 1: 數據攝取 & 智能分析
- [ ] YouTube fetcher (yt-dlp)
- [ ] Podcast fetcher (feedparser)
- [ ] Whisper 轉錄引擎
- [ ] 財經黑話映射
- [ ] LLM Agent + 情緒分析
- [ ] 實體識別與 RAG
- [ ] JSON 結構化輸出

### Phase 2: 量化驗證
- [ ] 基本回測框架
- [ ] L4-L7 驗證邏輯
- [ ] 信號有效性測試

### Phase 3: 資金控管
- [ ] Kelly 公式實現
- [ ] 風險限額邏輯
- [ ] 部位規模計算

---

## 5. 當前焦點
**Phase 1: 數據攝取到智能分析收集資訊**
