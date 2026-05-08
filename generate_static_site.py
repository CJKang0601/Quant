import json
import os
from pathlib import Path
from datetime import datetime

class ModernDashboardGenerator:
    """Generates a modern, single-page professional investment dashboard."""
    
    def __init__(self, data_dir: str, output_dir: str):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.sources = {
            "hao": {"name": "財經皓角", "icon": "bi-tv", "color": "#1e88e5"},
            "gooaye": {"name": "股癌", "icon": "bi-mic", "color": "#2c3e50"},
            "market_anchor": {"name": "定錨產業", "icon": "bi-anchor", "color": "#00897b"}
        }

    def load_data(self):
        files = list(self.data_dir.glob("analysis_*.json"))
        all_data = []
        for f in files:
            try:
                with open(f, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    sk = "unknown"
                    if "hao" in f.name: sk = "hao"
                    elif "gooaye" in f.name: sk = "gooaye"
                    elif "market" in f.name: sk = "market_anchor"
                    data["_source_key"] = sk
                    all_data.append(data)
            except: continue
        return sorted(all_data, key=lambda x: x.get("timestamp", ""), reverse=True)

    def generate(self):
        data = self.load_data()
        
        # Split data by source
        data_by_source = {k: [d for d in data if d["_source_key"] == k] for k in self.sources.keys()}
        
        # Stats for Dashboard
        tw_recs = []
        us_recs = []
        for item in data[:15]:
            for r in item.get("recommendations", []):
                r["_source"] = self.sources.get(item["_source_key"], {}).get("name", "未知")
                r["_date"] = item.get("timestamp", "").split("T")[0]
                if r.get("market") == "TW": tw_recs.append(r)
                else: us_recs.append(r)

        html = f"""
        <!DOCTYPE html>
        <html lang="zh-TW">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Quant AI 投資助手</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
            <style>
                body {{ background-color: #f0f2f5; font-family: 'Inter', -apple-system, sans-serif; color: #1a1a1a; }}
                .sidebar {{ background: #ffffff; border-right: 1px solid #e0e0e0; height: 100vh; position: fixed; width: 260px; padding: 2rem 1rem; z-index: 1000; }}
                .main-content {{ margin-left: 260px; padding: 2rem 3rem; }}
                .nav-pills .nav-link {{ color: #4b5563; font-weight: 500; margin-bottom: 0.5rem; border-radius: 10px; padding: 0.8rem 1rem; transition: all 0.2s; }}
                .nav-pills .nav-link:hover {{ background: #f3f4f6; color: #111827; }}
                .nav-pills .nav-link.active {{ background: #2563eb !important; color: #ffffff; box-shadow: 0 4px 12px rgba(37,99,235,0.2); }}
                .card {{ border: none; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); margin-bottom: 2rem; overflow: hidden; }}
                .card-header {{ background: #ffffff; border-bottom: 1px solid #f0f0f0; padding: 1.5rem; }}
                .sentiment-badge {{ padding: 0.5rem 1rem; border-radius: 99px; font-weight: 700; font-size: 0.9rem; }}
                .rec-card {{ border-left: 6px solid #e5e7eb; padding: 1.2rem; background: #fafafa; border-radius: 0 12px 12px 0; margin-bottom: 1rem; }}
                .context-snippet {{ font-size: 0.85rem; color: #6b7280; background: #ffffff; padding: 0.8rem; border-radius: 8px; border: 1px dashed #e5e7eb; margin-top: 0.5rem; }}
                .market-tag {{ font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.05em; padding: 0.2rem 0.5rem; border-radius: 4px; font-weight: 800; }}
                .tag-tw {{ background: #fee2e2; color: #991b1b; }}
                .tag-us {{ background: #dbeafe; color: #1e40af; }}
                .summary-box {{ background: #eff6ff; border-radius: 12px; padding: 1.5rem; border-left: 4px solid #3b82f6; }}
            </style>
        </head>
        <body>
            <div class="sidebar">
                <div class="d-flex align-items-center mb-5 px-2">
                    <i class="bi bi-graph-up-arrow text-primary fs-3 me-3"></i>
                    <h3 class="mb-0 fw-bold">Quant AI</h3>
                </div>
                <div class="nav flex-column nav-pills" id="v-pills-tab" role="tablist" aria-orientation="vertical">
                    <button class="nav-link active" id="tab-home" data-bs-toggle="pill" data-bs-target="#content-home" type="button"><i class="bi bi-grid-1x2-fill me-2"></i> 綜合總覽</button>
                    <button class="nav-link" id="tab-hao" data-bs-toggle="pill" data-bs-target="#content-hao" type="button"><i class="bi bi-tv me-2"></i> 財經皓角</button>
                    <button class="nav-link" id="tab-gooaye" data-bs-toggle="pill" data-bs-target="#content-gooaye" type="button"><i class="bi bi-mic me-2"></i> 股癌專區</button>
                    <button class="nav-link" id="tab-market" data-bs-toggle="pill" data-bs-target="#content-market" type="button"><i class="bi bi-anchor me-2"></i> 定錨產業</button>
                </div>
                <div class="position-absolute bottom-0 start-0 p-4 w-100 text-muted small border-top">
                    最後同步: {datetime.now().strftime('%Y-%m-%d %H:%M')}
                </div>
            </div>

            <div class="main-content">
                <div class="tab-content" id="v-pills-tabContent">
                    <!-- Dashboard Home -->
                    <div class="tab-pane fade show active" id="content-home" role="tabpanel">
                        <h2 class="fw-bold mb-4">🏠 綜合趨勢看板</h2>
                        <div class="row g-4 mb-5">
                            <div class="col-md-6">
                                <div class="card h-100 p-4" style="background: linear-gradient(to right, #ffffff, #fdf2f2);">
                                    <div class="d-flex justify-content-between">
                                        <h4 class="fw-bold">🇹🇼 台股觀點熱點</h4>
                                        <span class="badge bg-danger">{len(tw_recs)} 則建議</span>
                                    </div>
                                    <div class="mt-3">
                                        {"".join([self.render_mini_rec(r) for r in tw_recs[:8]])}
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="card h-100 p-4" style="background: linear-gradient(to right, #ffffff, #eff6ff);">
                                    <div class="d-flex justify-content-between">
                                        <h4 class="fw-bold">🇺🇸 美股觀點熱點</h4>
                                        <span class="badge bg-primary">{len(us_recs)} 則建議</span>
                                    </div>
                                    <div class="mt-3">
                                        {"".join([self.render_mini_rec(r) for r in us_recs[:8]])}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Source Tabs -->
                    {self.render_source_pane("hao", data_by_source["hao"])}
                    {self.render_source_pane("gooaye", data_by_source["gooaye"])}
                    {self.render_source_pane("market_anchor", data_by_source["market_anchor"])}
                </div>
            </div>

            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        </body>
        </html>
        """
        with open(self.output_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("Successfully generated high-performance single-page dashboard!")

    def render_mini_rec(self, r):
        color = "#10b981" if r['action'] == "BUY" else "#ef4444" if r['action'] == "SELL" else "#f59e0b"
        return f"""
        <div class="d-flex align-items-center mb-3 p-2 border-bottom border-light">
            <div class="me-3" style="width: 4px; height: 30px; background: {color}; border-radius: 2px;"></div>
            <div class="flex-grow-1">
                <div class="d-flex justify-content-between align-items-center">
                    <span class="fw-bold">{r['ticker']} {r.get('name', '')}</span>
                    <span class="fw-bold small" style="color: {color};">{r['action']}</span>
                </div>
                <div class="text-muted" style="font-size: 0.8rem;">{r['_source']} | {r['_date']}</div>
            </div>
        </div>
        """

    def render_source_pane(self, key, source_data):
        info = self.sources.get(key, {})
        pane_id = f"content-{key}"
        content_html = f'<div class="tab-pane fade" id="{pane_id}" role="tabpanel">'
        content_html += f'<h2 class="fw-bold mb-4"><i class="bi {info["icon"]} me-2"></i>{info["name"]} 歷史分析</h2>'
        
        if not source_data:
            content_html += '<div class="alert alert-light">目前尚無分析資料。</div>'
        else:
            for item in source_data:
                content_html += self.render_full_card(item)
        
        content_html += '</div>'
        return content_html

    def render_full_card(self, item):
        score = round(item.get("macro_view", {}).get("overall_sentiment", 0), 2)
        color = "#10b981" if score >= 7 else "#f59e0b" if score >= 4 else "#ef4444"
        bg_color = "#ecfdf5" if score >= 7 else "#fffbeb" if score >= 4 else "#fef2f2"
        
        recs_html = ""
        for r in item.get("recommendations", []):
            rec_color = "#10b981" if r['action'] == "BUY" else "#ef4444" if r['action'] == "SELL" else "#f59e0b"
            market_class = "tag-tw" if r.get("market") == "TW" else "tag-us"
            recs_html += f"""
            <div class="rec-card" style="border-left-color: {rec_color};">
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <h5 class="mb-0 fw-bold">
                        <span class="market-tag {market_class} me-2">{r.get('market', 'TW')}</span>
                        {r['ticker']} {r.get('name', '')} 
                        <span class="ms-2 badge" style="background-color: {rec_color}; font-size: 0.75rem;">{r['action']}</span>
                    </h5>
                    <span class="text-muted small">AI 信心度: {int(r.get('confidence_score', 0)*100)}%</span>
                </div>
                <p class="mb-2" style="font-size: 0.95rem;">{r['reason']}</p>
                <div class="context-snippet">
                    <i class="bi bi-chat-left-quote me-2 text-primary"></i>{r.get('context_snippet', '無具體引用內容')}
                </div>
            </div>
            """

        jargon_html = "".join([f'<div class="mb-2 border-bottom pb-1"><span class="fw-bold text-primary">{j["term"]}</span>: <span class="small">{j["explanation"]}</span></div>' for j in item.get("jargon_explained", [])])
        companies_html = "".join([f'<div class="mb-2 border-bottom pb-1"><span class="fw-bold">{c["name"]}</span>: <span class="small text-muted">{c["description"]}</span></div>' for c in item.get("discussed_companies", [])])

        return f"""
        <div class="card mb-5">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h4 class="mb-0 fw-bold">📅 {item.get('timestamp', '').split('T')[0]} - {item.get('source_title', '')[:40]}...</h4>
                <div class="sentiment-badge" style="background: {bg_color}; color: {color}; border: 1px solid {color};">
                    情緒溫度: {score} / 10
                </div>
            </div>
            <div class="card-body">
                <div class="summary-box mb-4">
                    <h6 class="fw-bold mb-2 text-primary"><i class="bi bi-file-text me-2"></i>本集速報 (AI 摘要)</h6>
                    <p class="mb-0 text-dark" style="line-height: 1.6;">{item.get('overall_summary', '無摘要')}</p>
                </div>
                
                <div class="row">
                    <div class="col-lg-8 border-end">
                        <h6 class="fw-bold mb-3"><i class="bi bi-lightbulb me-2 text-warning"></i>核心投資建議</h6>
                        {recs_html or '<p class="text-muted">本集無具體個股建議。</p>'}
                    </div>
                    <div class="col-lg-4">
                        <h6 class="fw-bold mb-3 text-info"><i class="bi bi-building me-2"></i>提到的公司</h6>
                        <div class="mb-4">{companies_html or '<span class="text-muted small">無</span>'}</div>
                        
                        <h6 class="fw-bold mb-3 text-success"><i class="bi bi-book me-2"></i>財經黑話百科</h6>
                        <div class="mb-4">{jargon_html or '<span class="text-muted small">無</span>'}</div>
                        
                        <h6 class="fw-bold mb-3 text-danger"><i class="bi bi-exclamation-triangle me-2"></i>關鍵風險提示</h6>
                        <ul class="small text-danger ps-3">
                            {"".join([f"<li>{r}</li>" for r in item.get('key_risks', [])])}
                        </ul>
                    </div>
                </div>
            </div>
        </div>
        """

if __name__ == "__main__":
    gen = ModernDashboardGenerator("data/processed", "docs")
    gen.generate()
