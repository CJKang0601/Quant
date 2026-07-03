"""Static site generator: 產業趨勢儀表板 (GitHub Pages)."""
import json
from pathlib import Path
from datetime import datetime

# time_horizon → (顯示文字, 前景色, 背景色)
HORIZONS = {
    "SHORT": ("短期 0-3月", "#b45309", "#fef3c7"),
    "MID": ("中期 3-18月", "#1d4ed8", "#dbeafe"),
    "LONG": ("長期 18月+", "#047857", "#d1fae5"),
}


def horizon_badge(horizon: str) -> str:
    label, fg, bg = HORIZONS.get(horizon, HORIZONS["MID"])
    return f'<span class="horizon-tag" style="color: {fg}; background: {bg};">{label}</span>'


def sentiment_colors(score: float):
    if score >= 7:
        return "#10b981", "#ecfdf5"
    if score >= 4:
        return "#f59e0b", "#fffbeb"
    return "#ef4444", "#fef2f2"


class TrendDashboardGenerator:
    """Generates a single-page industry-trend dashboard."""

    def __init__(self, data_dir: str, output_dir: str):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.sources = {
            "hao": {"name": "財經皓角", "icon": "bi-tv", "cadence": "每日 8:30 直播"},
            "gooaye": {"name": "股癌", "icon": "bi-mic", "cadence": "每週三、六"},
            "market_anchor": {"name": "定錨產業", "icon": "bi-anchor", "cadence": "不定期深度"},
        }

    def load_data(self):
        files = list(self.data_dir.glob("analysis_*.json"))
        all_data = []
        for f in files:
            try:
                with open(f, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    sk = data.get("_source_key") or data.get("source_key")
                    if not sk:
                        if "hao" in f.name:
                            sk = "hao"
                        elif "gooaye" in f.name:
                            sk = "gooaye"
                        elif "market" in f.name:
                            sk = "market_anchor"
                        else:
                            sk = "unknown"
                    # podcast 與 YouTube 的股癌歸為同一個顯示分區
                    if sk == "gooaye_podcast":
                        sk = "gooaye"
                    data["_source_key"] = sk
                    data["_display_date"] = data.get("content_date") or data.get("timestamp", "").split("T")[0]
                    all_data.append(data)
            except Exception:
                continue
        return sorted(all_data, key=lambda x: x.get("content_date") or x.get("timestamp", ""), reverse=True)

    def aggregate_trends(self, data, recent_n=20):
        """跨集數彙整產業趨勢:同產業被多來源、多集數重複提及 = 趨勢強度訊號。"""
        industries = {}
        for item in data[:recent_n]:
            source_name = self.sources.get(item["_source_key"], {}).get("name", "未知")
            for trend in item.get("industry_trends", []):
                name = trend.get("industry_name", "").strip()
                if not name:
                    continue
                entry = industries.setdefault(name, {
                    "mentions": [], "horizons": {}, "sources": set(),
                })
                entry["mentions"].append({
                    "source": source_name,
                    "date": item["_display_date"],
                    "score": trend.get("sentiment_score", 5.5),
                    "thesis": trend.get("thesis", ""),
                    "horizon": trend.get("time_horizon", "MID"),
                })
                entry["horizons"][trend.get("time_horizon", "MID")] = \
                    entry["horizons"].get(trend.get("time_horizon", "MID"), 0) + 1
                entry["sources"].add(source_name)
        # 依提及次數排序(次數相同看來源數)
        return sorted(
            industries.items(),
            key=lambda kv: (len(kv[1]["mentions"]), len(kv[1]["sources"])),
            reverse=True,
        )

    def render_trend_radar(self, aggregated):
        if not aggregated:
            return '<div class="alert alert-light">尚無趨勢資料,等待第一次自動分析。</div>'
        rows = ""
        for name, info in aggregated[:12]:
            latest = info["mentions"][0]
            score = latest["score"]
            fg, bg = sentiment_colors(score)
            horizon_html = "".join(
                horizon_badge(h) + f'<span class="text-muted small me-2">×{c}</span>'
                for h, c in sorted(info["horizons"].items())
            )
            sources_html = "、".join(sorted(info["sources"]))
            thesis = next((m["thesis"] for m in info["mentions"] if m["thesis"]), "")
            rows += f"""
            <div class="d-flex align-items-start mb-3 p-3 border-bottom border-light">
                <div class="me-3 mt-1" style="width: 4px; height: 42px; background: {fg}; border-radius: 2px;"></div>
                <div class="flex-grow-1">
                    <div class="d-flex justify-content-between align-items-center flex-wrap">
                        <span class="fw-bold">{name}</span>
                        <span class="fw-bold small" style="color: {fg};">情緒 {round(score, 1)}/10</span>
                    </div>
                    <div class="mt-1">{horizon_html}</div>
                    <div class="text-muted mt-1" style="font-size: 0.85rem;">{thesis}</div>
                    <div class="text-muted" style="font-size: 0.75rem;">提及 {len(info["mentions"])} 次 | 來源: {sources_html} | 最近: {latest["date"]}</div>
                </div>
            </div>
            """
        return rows

    def render_trend_card(self, trend):
        score = trend.get("sentiment_score", 5.5)
        fg, _ = sentiment_colors(score)
        companies_html = ""
        for c in trend.get("supporting_companies", []):
            ticker = f" ({c['ticker']})" if c.get("ticker") else ""
            quote = f'<div class="context-snippet"><i class="bi bi-chat-left-quote me-2 text-primary"></i>{c["quote"]}</div>' if c.get("quote") else ""
            companies_html += f"""
            <div class="mt-2 ps-3 border-start border-2">
                <span class="fw-bold small">{c.get('name', '')}{ticker}</span>
                <span class="text-muted small"> — {c.get('role_in_trend', '')}</span>
                {quote}
            </div>
            """
        key_trends_html = "".join(f'<li class="small">{t}</li>' for t in trend.get("key_trends", []))
        return f"""
        <div class="rec-card" style="border-left-color: {fg};">
            <div class="d-flex justify-content-between align-items-center mb-1 flex-wrap">
                <h5 class="mb-0 fw-bold">{trend.get('industry_name', '')} {horizon_badge(trend.get('time_horizon', 'MID'))}</h5>
                <span class="fw-bold small" style="color: {fg};">情緒 {round(score, 1)}/10</span>
            </div>
            <p class="mb-1" style="font-size: 0.95rem;">{trend.get('thesis', '')}</p>
            <ul class="mb-1 ps-4">{key_trends_html}</ul>
            {companies_html}
        </div>
        """

    def render_full_card(self, item):
        score = round(item.get("macro_view", {}).get("overall_sentiment", 0) or 0, 2)
        fg, bg = sentiment_colors(score)

        trends_html = "".join(self.render_trend_card(t) for t in item.get("industry_trends", []))
        jargon_html = "".join(
            f'<div class="mb-2 border-bottom pb-1"><span class="fw-bold text-primary">{j.get("term", "")}</span>: <span class="small">{j.get("explanation", "")}</span></div>'
            for j in item.get("jargon_explained", [])
        )
        companies_html = "".join(
            f'<div class="mb-2 border-bottom pb-1"><span class="fw-bold">{c.get("name", "")}</span>: <span class="small text-muted">{c.get("description", "")}</span></div>'
            for c in item.get("discussed_companies", [])
        )
        risks_html = "".join(f"<li>{r}</li>" for r in item.get("key_risks", []))

        return f"""
        <div class="card mb-5">
            <div class="card-header d-flex justify-content-between align-items-center flex-wrap">
                <h4 class="mb-0 fw-bold">📅 {item.get('_display_date', '')} - {item.get('source_title', '')[:40]}</h4>
                <div class="sentiment-badge" style="background: {bg}; color: {fg}; border: 1px solid {fg};">
                    宏觀情緒: {score} / 10
                </div>
            </div>
            <div class="card-body">
                <div class="summary-box mb-4">
                    <h6 class="fw-bold mb-2 text-primary"><i class="bi bi-file-text me-2"></i>本集速報 (AI 摘要)</h6>
                    <p class="mb-0 text-dark" style="line-height: 1.6;">{item.get('overall_summary', '無摘要')}</p>
                </div>

                <div class="row">
                    <div class="col-lg-8 border-end">
                        <h6 class="fw-bold mb-3"><i class="bi bi-graph-up-arrow me-2 text-primary"></i>產業趨勢</h6>
                        {trends_html or '<p class="text-muted">本集無明確產業趨勢內容。</p>'}
                    </div>
                    <div class="col-lg-4">
                        <h6 class="fw-bold mb-3 text-info"><i class="bi bi-building me-2"></i>其他討論公司</h6>
                        <div class="mb-4">{companies_html or '<span class="text-muted small">無</span>'}</div>

                        <h6 class="fw-bold mb-3 text-success"><i class="bi bi-book me-2"></i>財經黑話百科</h6>
                        <div class="mb-4">{jargon_html or '<span class="text-muted small">無</span>'}</div>

                        <h6 class="fw-bold mb-3 text-danger"><i class="bi bi-exclamation-triangle me-2"></i>關鍵風險提示</h6>
                        <ul class="small text-danger ps-3">{risks_html}</ul>
                    </div>
                </div>
            </div>
        </div>
        """

    def render_source_pane(self, key, source_data):
        info = self.sources.get(key, {})
        content_html = f'<div class="tab-pane fade" id="content-{key}" role="tabpanel">'
        content_html += f'<h2 class="fw-bold mb-1"><i class="bi {info.get("icon", "")} me-2"></i>{info.get("name", key)} 歷史分析</h2>'
        content_html += f'<p class="text-muted mb-4">{info.get("cadence", "")}</p>'
        if not source_data:
            content_html += '<div class="alert alert-light">目前尚無分析資料。</div>'
        else:
            for item in source_data:
                content_html += self.render_full_card(item)
        content_html += '</div>'
        return content_html

    def generate(self):
        data = self.load_data()
        data_by_source = {k: [d for d in data if d["_source_key"] == k] for k in self.sources.keys()}
        aggregated = self.aggregate_trends(data)

        html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quant AI 產業趨勢雷達</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        body {{ background-color: #f0f2f5; font-family: 'Inter', -apple-system, sans-serif; color: #1a1a1a; }}
        .sidebar {{ background: #ffffff; border-right: 1px solid #e0e0e0; height: 100vh; position: fixed; width: 260px; padding: 2rem 1rem; z-index: 1000; }}
        .main-content {{ margin-left: 260px; padding: 2rem 3rem; }}
        .nav-pills .nav-link {{ color: #4b5563; font-weight: 500; margin-bottom: 0.5rem; border-radius: 10px; padding: 0.8rem 1rem; transition: all 0.2s; text-align: left; }}
        .nav-pills .nav-link:hover {{ background: #f3f4f6; color: #111827; }}
        .nav-pills .nav-link.active {{ background: #2563eb !important; color: #ffffff; box-shadow: 0 4px 12px rgba(37,99,235,0.2); }}
        .card {{ border: none; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); margin-bottom: 2rem; overflow: hidden; }}
        .card-header {{ background: #ffffff; border-bottom: 1px solid #f0f0f0; padding: 1.5rem; }}
        .sentiment-badge {{ padding: 0.5rem 1rem; border-radius: 99px; font-weight: 700; font-size: 0.9rem; }}
        .rec-card {{ border-left: 6px solid #e5e7eb; padding: 1.2rem; background: #fafafa; border-radius: 0 12px 12px 0; margin-bottom: 1rem; }}
        .context-snippet {{ font-size: 0.85rem; color: #6b7280; background: #ffffff; padding: 0.8rem; border-radius: 8px; border: 1px dashed #e5e7eb; margin-top: 0.5rem; }}
        .horizon-tag {{ font-size: 0.7rem; letter-spacing: 0.05em; padding: 0.2rem 0.5rem; border-radius: 4px; font-weight: 800; margin-right: 0.3rem; }}
        .summary-box {{ background: #eff6ff; border-radius: 12px; padding: 1.5rem; border-left: 4px solid #3b82f6; }}
        @media (max-width: 768px) {{
            .sidebar {{ position: static; width: 100%; height: auto; }}
            .main-content {{ margin-left: 0; padding: 1rem; }}
        }}
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="d-flex align-items-center mb-5 px-2">
            <i class="bi bi-graph-up-arrow text-primary fs-3 me-3"></i>
            <h3 class="mb-0 fw-bold">Quant AI</h3>
        </div>
        <div class="nav flex-column nav-pills" role="tablist" aria-orientation="vertical">
            <button class="nav-link active" data-bs-toggle="pill" data-bs-target="#content-home" type="button"><i class="bi bi-grid-1x2-fill me-2"></i> 趨勢雷達</button>
            <button class="nav-link" data-bs-toggle="pill" data-bs-target="#content-hao" type="button"><i class="bi bi-tv me-2"></i> 財經皓角</button>
            <button class="nav-link" data-bs-toggle="pill" data-bs-target="#content-gooaye" type="button"><i class="bi bi-mic me-2"></i> 股癌專區</button>
            <button class="nav-link" data-bs-toggle="pill" data-bs-target="#content-market_anchor" type="button"><i class="bi bi-anchor me-2"></i> 定錨產業</button>
        </div>
        <div class="position-absolute bottom-0 start-0 p-4 w-100 text-muted small border-top">
            最後同步: {datetime.now().strftime('%Y-%m-%d %H:%M')}
        </div>
    </div>

    <div class="main-content">
        <div class="tab-content">
            <div class="tab-pane fade show active" id="content-home" role="tabpanel">
                <h2 class="fw-bold mb-1">📡 產業趨勢雷達</h2>
                <p class="text-muted mb-4">跨來源、跨集數彙整:同一產業被多個來源反覆提及,代表趨勢訊號更強。個股僅作為趨勢佐證,非投資建議。</p>
                <div class="card p-4">
                    {self.render_trend_radar(aggregated)}
                </div>
            </div>

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
        print("Successfully generated industry-trend dashboard!")


if __name__ == "__main__":
    gen = TrendDashboardGenerator("data/processed", "docs")
    gen.generate()
