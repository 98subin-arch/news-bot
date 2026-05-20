"""
매일 오전 6시 한국 주요 경제 뉴스 헤드라인 자동 발송 스크립트

- 여러 언론사 RSS 피드에서 최신 경제 뉴스 수집
- HTML 형식으로 정리해서 이메일 발송
- GitHub Actions의 스케줄러로 매일 자동 실행
"""

import feedparser
import smtplib
import os
import sys
from email.mime.text import MIMEText
from datetime import datetime

# ========== 설정 영역 (필요시 여기만 수정) ==========

# 뉴스 소스: 한국 주요 경제 뉴스 RSS 피드
RSS_FEEDS = {
    "뉴시스 경제": "https://www.newsis.com/RSS/economy.xml",
    "뉴시스 금융": "https://www.newsis.com/RSS/bank.xml",
    "뉴시스 산업": "https://www.newsis.com/RSS/industry.xml",
    "연합뉴스 경제": "https://www.yna.co.kr/rss/economy.xml",
    "한국경제": "https://www.hankyung.com/feed/economy",
    "매일경제": "https://www.mk.co.kr/rss/30000001/",
}

ITEMS_PER_FEED = 5  # 언론사당 가져올 기사 수

# ===================================================


def fetch_feed(name, url):
    """RSS 피드에서 최신 기사 가져오기"""
    try:
        feed = feedparser.parse(url)
        if not feed.entries:
            print(f"⚠️  {name}: 가져온 기사 없음", file=sys.stderr)
            return []
        return feed.entries[:ITEMS_PER_FEED]
    except Exception as e:
        print(f"⚠️  {name} 오류: {e}", file=sys.stderr)
        return []


def build_html():
    """HTML 메일 본문 생성"""
    weekdays = ["월", "화", "수", "목", "금", "토", "일"]
    now = datetime.now()
    today = f"{now.year}년 {now.month}월 {now.day}일 ({weekdays[now.weekday()]})"

    html = f"""
    <html><body style="font-family: -apple-system, 'Apple SD Gothic Neo', sans-serif; max-width:680px; margin:0 auto; padding:20px;">
        <h1 style="border-bottom:3px solid #1a73e8; padding-bottom:10px; color:#202124;">
            📰 오늘의 경제 헤드라인
        </h1>
        <p style="color:#5f6368; margin-top:4px;">{today}</p>
    """

    total_articles = 0
    for source, url in RSS_FEEDS.items():
        entries = fetch_feed(source, url)
        if not entries:
            continue
        total_articles += len(entries)
        html += f'<h2 style="color:#1a73e8; margin-top:28px; font-size:18px;">{source}</h2><ul style="line-height:1.8; padding-left:20px;">'
        for entry in entries:
            title = entry.get("title", "제목 없음")
            link = entry.get("link", "#")
            html += f'<li style="margin:4px 0;"><a href="{link}" style="color:#202124; text-decoration:none;">{title}</a></li>'
        html += "</ul>"

    html += f"""
        <hr style="margin-top:36px; border:none; border-top:1px solid #e0e0e0;">
        <p style="color:#9aa0a6; font-size:12px; text-align:center;">
            총 {total_articles}개 기사 · 매일 오전 6시 자동 발송<br>
            {now.strftime('%Y-%m-%d %H:%M:%S')} KST
        </p>
    </body></html>
    """
    return html


def send_email(html):
    """SMTP로 메일 발송"""
    sender = os.environ["SENDER_EMAIL"]
    password = os.environ["SENDER_PASSWORD"]
    recipient = os.environ["RECIPIENT_EMAIL"]
    smtp_server = os.environ.get("SMTP_SERVER", "smtp.worksmobile.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))

    msg = MIMEText(html, "html", "utf-8")
    msg["Subject"] = f"📰 오늘의 경제 뉴스 ({datetime.now().strftime('%m월 %d일')})"
    msg["From"] = sender
    msg["To"] = recipient

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)

    print(f"✅ 메일 발송 완료 → {recipient}")


if __name__ == "__main__":
    html = build_html()
    send_email(html)
