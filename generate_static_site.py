import json
import os
from pathlib import Path
from datetime import datetime

class StaticSiteGenerator:
    """Generates a static HTML site from analysis results."""
    
    def __init__(self, data_dir: str, output_dir: str):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def load_data(self):
        files = list(self.data_dir.glob("analysis_*.json"))
        all_data = []
        for f in files:
            with open(f, 'r', encoding='utf-8') as file:
                data = json.load(file)
                # Identify source
                source_key = "unknown"
                if "hao" in f.name: source_key = "hao"
                elif "gooaye" in f.name: source_key = "gooaye"
                elif "market_anchor" in f.name: source_key = "market_anchor"
                data["_source_key"] = source_key
                all_data.append(data)
        return sorted(all_data, key=lambda x: x.get("timestamp", ""), reverse=True)

    def generate(self):
        data = self.load_data()
        
        # Simple HTML Template
        html = f"""
        <!DOCTYPE html>
        <html lang="zh-TW">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>AI 投資研究助理</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body {{ background-color: #f8f9fa; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
                .card {{ margin-bottom: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .sentiment-score {{ font-size: 2rem; font-weight: bold; color: #0d6efd; }}
                .source-badge {{ font-size: 0.8rem; padding: 5px 10px; border-radius: 20px; }}
            </style>
        </head>
        <body>
            <nav class="navbar navbar-dark bg-dark">
                <div class="container">
                    <a class="navbar-brand" href="#">📈 AI 投資研究助理</a>
                    <span class="navbar-text">最後更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}</span>
                </div>
            </nav>

            <div class="container mt-4">
                <div class="row">
        """

        for item in data:
            source_name = {"hao": "財經皓角", "gooaye": "股癌", "market_anchor": "定錨產業"}.get(item["_source_key"], "未知來源")
            macro = item.get("macro_view", {})
            score = round(macro.get("overall_sentiment", 0), 2)
            
            html += f"""
                    <div class="col-md-12">
                        <div class="card">
                            <div class="card-body">
                                <div class="d-flex justify-content-between align-items-center">
                                    <h5 class="card-title">📅 {item.get('timestamp', '').split('T')[0]} - {source_name}</h5>
                                    <span class="badge bg-primary source-badge">{source_name}</span>
                                </div>
                                <hr>
                                <div class="row">
                                    <div class="col-md-3 text-center border-end">
                                        <div class="text-muted">宏觀情緒</div>
                                        <div class="sentiment-score">{score}/10</div>
                                        <div class="small">{"🟢 樂觀" if score >= 7 else "🟡 中立" if score >= 4 else "🔴 悲觀"}</div>
                                    </div>
                                    <div class="col-md-9">
                                        <h6>💡 投資建議</h6>
                                        <table class="table table-sm">
                                            <thead><tr><th>代號</th><th>動作</th><th>信心度</th><th>理由</th></tr></thead>
                                            <tbody>
            """
            for rec in item.get("recommendations", []):
                action_class = "text-success" if rec['action'] == "BUY" else "text-danger" if rec['action'] == "SELL" else "text-warning"
                html += f"""
                                                <tr>
                                                    <td><strong>{rec['ticker']}</strong></td>
                                                    <td class="{action_class}">{rec['action']}</td>
                                                    <td>{int(rec['confidence_score']*100)}%</td>
                                                    <td><small>{rec['reason']}</small></td>
                                                </tr>
                """
            
            html += """
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
            """

        html += """
                </div>
            </div>
            <footer class="text-center py-4 text-muted">
                &copy; 2026 AI Investment Agent | Generated by GitHub Actions
            </footer>
        </body>
        </html>
        """
        
        with open(self.output_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Generated static site at {self.output_dir / 'index.html'}")

if __name__ == "__main__":
    generator = StaticSiteGenerator("data/processed", "docs")
    generator.generate()
