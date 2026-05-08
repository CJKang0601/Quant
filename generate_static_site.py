import json
import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class DashboardGenerator:
    """Generates a professional multi-page static dashboard."""
    
    def __init__(self, data_dir: str, output_dir: str):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.sources = {
            "hao": {"name": "財經皓角", "icon": "📺", "color": "#1e88e5"},
            "gooaye": {"name": "股癌", "icon": "🎙️", "color": "#37474f"},
            "market_anchor": {"name": "定錨產業", "icon": "⚓", "color": "#00897b"}
        }

    def load_data(self):
        files = list(self.data_dir.glob("analysis_*.json"))
        all_data = []
        for f in files:
            try:
                with open(f, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    # Sync source key
                    sk = "unknown"
                    if "hao" in f.name: sk = "hao"
                    elif "gooaye" in f.name: sk = "gooaye"
                    elif "market" in f.name: sk = "market_anchor"
                    data["_source_key"] = sk
                    all_data.append(data)
            except: continue
        return sorted(all_data, key=lambda x: x.get("timestamp", ""), reverse=True)

    def get_header(self, title):
        return f"""
        <!DOCTYPE html>
        <html lang="zh-TW">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title} - AI 投資助手</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
            <style>
                :root {{ --sidebar-width: 250px; }}
                body {{ background-color: #f4f7f6; font-family: 'Inter', sans-serif; }}
                #sidebar {{ width: var(--sidebar-width); position: fixed; height: 100vh; background: #2c3e50; color: white; transition: all 0.3s; }}
                #content {{ margin-left: var(--sidebar-width); padding: 30px; }}
                .nav-link {{ color: #adb5bd; margin-bottom: 10px; border-radius: 8px; }}
                .nav-link:hover, .nav-link.active {{ background: #34495e; color: white; }}
                .stat-card {{ border: none; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); transition: transform 0.2s; }}
                .stat-card:hover {{ transform: translateY(-5px); }}
                .ticker-badge {{ font-family: monospace; background: #e9ecef; padding: 2px 8px; border-radius: 4px; }}
                .recommendation-row {{ border-left: 5px solid #ccc; margin-bottom: 15px; padding: 15px; background: white; border-radius: 0 10px 10px 0; box-shadow: 0 2px 5px rgba(0,0,0,0.02); }}
                .context-box {{ font-style: italic; color: #6c757d; font-size: 0.9rem; margin-top: 8px; padding: 10px; background: #f8f9fa; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div id="sidebar" class="p-3">
                <h4 class="mb-4 text-center">📈 Quant AI</h4>
                <ul class="nav flex-column">
                    <li class="nav-item"><a href="index.html" class="nav-link {'active' if title=='Dashboard' else ''}"><i class="bi bi-house-door me-2"></i> 綜合總覽</a></li>
                    <li class="nav-item"><a href="hao.html" class="nav-link {'active' if title=='財經皓角' else ''}"><i class="bi bi-tv me-2"></i> 財經皓角</a></li>
                    <li class="nav-item"><a href="gooaye.html" class="nav-link {'active' if title=='股癌' else ''}"><i class="bi bi-mic me-2"></i> 股癌</a></li>
                    <li class="nav-item"><a href="market.html" class="nav-link {'active' if title=='定錨產業' else ''}"><i class="bi bi-anchor me-2"></i> 定錨產業</a></li>
                </ul>
                <div class="mt-auto small text-muted text-center pt-5">
                    最後更新: {datetime.now().strftime('%Y-%m-%d')}
                </div>
            </div>
            <div id="content">
        """

    def generate_dashboard(self, data):
        html = self.get_header("Dashboard")
        
        # 統計最新台美股建議
        tw_recs = []
        us_recs = []
        for item in data[:10]: # 只取最近 10 份報告
            for r in item.get("recommendations", []):
                r["_source"] = self.sources.get(item["_source_key"], {}).get("name", "未知")
                r["_date"] = item.get("timestamp", "").split("T")[0]
                if r.get("market") == "TW": tw_recs.append(r)
                else: us_recs.append(r)

        html += f"""
                <h2 class="mb-4">🏠 綜合分析總覽</h2>
                <div class="row mb-4">
                    <div class="col-md-6">
                        <div class="card stat-card p-4 text-white" style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);">
                            <h3>🇹🇼 台股觀點匯整</h3>
                            <p>共有 {len(tw_recs)} 則最新建議</p>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card stat-card p-4 text-white" style="background: linear-gradient(135deg, #2c3e50 0%, #4ca1af 100%);">
                            <h3>🇺🇸 美股觀點匯整</h3>
                            <p>共有 {len(us_recs)} 則最新建議</p>
                        </div>
                    </div>
                </div>

                <div class="row">
                    <div class="col-md-6">
                        <h4>最新台股信號</h4>
                        {"".join([self.render_rec_mini(r) for r in tw_recs[:10]])}
                    </div>
                    <div class="col-md-6">
                        <h4>最新美股信號</h4>
                        {"".join([self.render_rec_mini(r) for r in us_recs[:10]])}
                    </div>
                </div>
        """
        html += "</div></body></html>"
        with open(self.output_dir / "index.html", "w", encoding="utf-8") as f: f.write(html)

    def render_rec_mini(self, r):
        color = "#28a745" if r['action'] == "BUY" else "#dc3545" if r['action'] == "SELL" else "#ffc107"
        return f"""
        <div class="recommendation-row" style="border-left-color: {color};">
            <div class="d-flex justify-content-between align-items-start">
                <div>
                    <span class="ticker-badge">{r['ticker']}</span> <strong>{r.get('name', '')}</strong>
                    <span class="badge" style="background-color: {color};">{r['action']}</span>
                </div>
                <small class="text-muted">{r['_source']} | {r['_date']}</small>
            </div>
            <div class="small mt-2">{r['reason']}</div>
        </div>
        """

    def generate_source_page(self, key, data):
        source_info = self.sources.get(key, {"name": "未知", "icon": "❓", "color": "#666"})
        html = self.get_header(source_info["name"])
        source_data = [d for d in data if d["_source_key"] == key]

        html += f"<h2>{source_info['icon']} {source_info['name']} - 歷史分析</h2>"
        
        if not source_data:
            html += "<p class='mt-4'>目前尚無此來源的分析資料。</p>"
        else:
            for item in source_data:
                html += self.render_full_analysis(item)

        html += "</div></body></html>"
        filename = f"{key if key != 'market_anchor' else 'market'}.html"
        with open(self.output_dir / filename, "w", encoding="utf-8") as f: f.write(html)

    def render_full_analysis(self, item):
        macro = item.get("macro_view", {})
        score = round(macro.get("overall_sentiment", 0), 2)
        score_color = "#28a745" if score >= 7 else "#ffc107" if score >= 4 else "#dc3545"
        
        recs_html = ""
        for r in item.get("recommendations", []):
            color = "#28a745" if r['action'] == "BUY" else "#dc3545" if r['action'] == "SELL" else "#ffc107"
            recs_html += f"""
            <div class="recommendation-row" style="border-left-color: {color};">
                <div class="d-flex justify-content-between">
                    <h5>{r['ticker']} {r.get('name', '')} <span class="badge" style="background-color: {color};">{r['action']}</span></h5>
                    <span class="text-muted">信心度: {int(r.get('confidence_score', 0)*100)}%</span>
                </div>
                <p class="mb-1"><strong>分析理由:</strong> {r['reason']}</p>
                <div class="context-box"><i class="bi bi-quote me-1"></i> {r.get('context_snippet', '無具體引用內容')}</div>
            </div>
            """

        jargon_html = "".join([f"<li><strong>{j['term']}:</strong> {j['explanation']}</li>" for j in item.get("jargon_explained", [])])
        companies_html = "".join([f"<li><strong>{c['name']}:</strong> {c['description']}</li>" for c in item.get("discussed_companies", [])])

        return f"""
        <div class="card stat-card mb-5">
            <div class="card-header bg-white py-3">
                <div class="d-flex justify-content-between align-items-center">
                    <h4 class="mb-0">📅 {item.get('timestamp', '').split('T')[0]} - {item.get('source_title', '')}</h4>
                    <div class="h4 mb-0" style="color: {score_color};">情緒: {score}/10</div>
                </div>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-12 mb-4">
                        <h5>📝 本集速報 (AI 摘要)</h5>
                        <p class="lead" style="font-size: 1.1rem;">{item.get('overall_summary', '無摘要')}</p>
                    </div>
                </div>
                <hr>
                <div class="row">
                    <div class="col-md-8 border-end">
                        <h5 class="mb-3">💡 投資建議詳情</h5>
                        {recs_html or "<p>本集無具體個股建議。</p>"}
                    </div>
                    <div class="col-md-4">
                        <h5 class="mb-3">🔍 提到的公司</h5>
                        <ul class="small">{companies_html or "無"}</ul>
                        <h5 class="mt-4 mb-3">📚 財經黑話/術語</h5>
                        <ul class="small">{jargon_html or "無"}</ul>
                        <h5 class="mt-4 mb-3">⚠️ 關鍵風險</h5>
                        <ul class="small">{"".join([f"<li>{r}</li>" for r in item.get('key_risks', [])])}</ul>
                    </div>
                </div>
            </div>
        </div>
        """

    def generate_all(self):
        data = self.load_data()
        self.generate_dashboard(data)
        self.generate_source_page("hao", data)
        self.generate_source_page("gooaye", data)
        self.generate_source_page("market_anchor", data)
        print("Successfully generated all dashboard pages!")

if __name__ == "__main__":
    gen = DashboardGenerator("data/processed", "docs")
    gen.generate_all()
