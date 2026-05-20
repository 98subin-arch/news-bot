"""
매일 오전 6시 한국 주요 경제 뉴스 헤드라인을 HTML로 생성
GitHub Pages로 호스팅하여 웹페이지로 확인
"""

import feedparser
import sys
from datetime import datetime

# ========== 설정 영역 ==========

RSS_FEEDS = {
    "뉴시스 경제": "https://www.newsis.com/RSS/economy.xml",
    "뉴시스 금융": "https://www.newsis.com/RSS/bank.xml",
    "뉴시스 산업": "https://www.newsis.com/RSS/industry.xml",
    "연합뉴스 경제": "https://www.yna.co.kr/rss/economy.xml",
    "연합뉴스 산업": "https://www.yna.co.kr/rss/industry.xml",
    "매일경제": "https://www.mk.co.kr/rss/30000001/",
}

ITEMS_PER_FEED = 10  # 언론사당 가져올 기사 수

# ===============================


def fetch_feed(name, url):
    """RSS 피드에서 최신 기사 가져오기"""
    try:
        feed = feedparser.parse(url)
        if not feed.entries:
            print(f"⚠️  {name}: 기사 없음", file=sys.stderr)
            return []
        return feed.entries[:ITEMS_PER_FEED]
    except Exception as e:
        print(f"⚠️  {name}: {e}", file=sys.stderr)
        return []


def build_html():
    weekdays = ["월", "화", "수", "목", "금", "토", "일"]
    now = datetime.now()
    today_str = f"{now.year}년 {now.month}월 {now.day}일 ({weekdays[now.weekday()]})"

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📰 오늘의 경제 뉴스</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, 'Apple SD Gothic Neo', 'Segoe UI', 'Malgun Gothic', sans-serif;
            background: #f5f5f7;
            color: #1d1d1f;
            line-height: 1.6;
            padding: 20px;
        }}
        .container {{
            max-width: 820px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 2px 24px rgba(0,0,0,0.06);
            overflow: hidden;
        }}
        header {{
            background: linear-gradient(135deg, #1a73e8, #0d47a1);
            color: white;
            padding: 36px 32px;
        }}
        header h1 {{
            font-size: 30px;
            font-weight: 700;
            margin-bottom: 8px;
            letter-spacing: -0.5px;
        }}
        header .date {{
            font-size: 16px;
            opacity: 0.92;
            font-weight: 500;
        }}
        .content {{ padding: 28px 32px; }}
        .source {{ margin-bottom: 32px; }}
        .source:last-child {{ margin-bottom: 0; }}
        .source h2 {{
            color: #1a73e8;
            font-size: 19px;
            font-weight: 700;
            padding-bottom: 10px;
            margin-bottom: 14px;
            border-bottom: 2px solid #e8f0fe;
        }}
        .source ul {{ list-style: none; }}
        .source li {{
            padding: 10px 0;
            border-bottom: 1px solid #f2f2f4;
            display: flex;
            align-items: baseline;
        }}
        .source li:last-child {{ border-bottom: none; }}
        .source li::before {{
            content: "•";
            color: #1a73e8;
            display: inline-block;
            width: 14px;
            margin-right: 4px;
            font-weight: bold;
            flex-shrink: 0;
        }}
        .source a {{
            color: #1d1d1f;
            text-decoration: none;
            font-size: 15.5px;
            line-height: 1.5;
            transition: color 0.15s;
        }}
        .source a:hover {{ color: #1a73e8; }}
        footer {{
            text-align: center;
            padding: 22px;
            background: #fafafa;
            color: #86868b;
            font-size: 13px;
            border-top: 1px solid #f0f0f0;
            line-height: 1.8;
        }}
        @media (max-width: 600px) {{
            body {{ padding: 10px; }}
            header {{ padding: 24px 22px; }}
            .content {{ padding: 20px 22px; }}
            header h1 {{ font-size: 23px; }}
            header .date {{ font-size: 14px; }}
            .source a {{ font-size: 15px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📰 오늘의 경제 헤드라인</h1>
            <div class="date">{today_str}</div>
        </header>
        <div class="content">
"""

    total = 0
    for source, url in RSS_FEEDS.items():
        entries = fetch_feed(source, url)
        if not entries:
            continue
        total += len(entries)
        html += f'<div class="source"><h2>{source}</h2><ul>'
        for entry in entries:
            title = entry.get("title", "제목 없음")
            link = entry.get("link", "#")
            html += f'<li><a href="{link}" target="_blank" rel="noopener">{title}</a></li>'
        html += "</ul></div>\n"

    html += f"""
        </div>
        <footer>
            총 <strong>{total}개</strong> 기사 · 마지막 업데이트 {now.strftime('%Y-%m-%d %H:%M')} KST<br>
            매일 오전 6시 자동 업데이트
        </footer>
    </div>
</body>
</html>
"""
    return html


if __name__ == "__main__":
    html = build_html()
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ index.html 생성 완료")
