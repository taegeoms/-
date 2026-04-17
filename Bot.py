1"}
import requests
from bs4 import BeautifulSoup
import time
import os
from openai import OpenAI

# ===== 환경변수 =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

HEADERS = {"User-Agent": "Mozilla/5.0"}

sent_links = set()

# ===== 뉴스 가져오기 =====
def get_news():
    url = "https://search.naver.com/search.naver?where=news&query=마약"
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")

    result = []
    for item in soup.select(".news_area"):
        title = item.select_one(".news_tit").text
        link = item.select_one(".news_tit")["href"]

        if "news.naver.com" in link:
            result.append((title, link))

    return result

# ===== 기사 본문 =====
def get_content(url):
    try:
        res = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(res.text, "html.parser")

        body = soup.select_one("#dic_area")
        return body.text.strip() if body else None
    except:
        return None

# ===== 요약 =====
def summarize(text):
    if not text:
        return "본문 없음"

    prompt = f"""
다음 뉴스 핵심만 3줄 요약:

{text[:2000]}
"""

    res = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return res.choices[0].message.content.strip()

# ===== 텔레그램 =====
def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": msg
    }
    requests.post(url, data=data)

# ===== 메인 루프 =====
def run():
    print("봇 실행 중...")

    while True:
        try:
            news = get_news()

            for title, link in news:
                if link in sent_links:
                    continue

                print("전송:", title)

                content = get_content(link)
                summary = summarize(content)

                message = f"📰 {title}\n\n{summary}\n\n🔗 {link}"
                send(message)

                sent_links.add(link)
                time.sleep(2)

            time.sleep(300)

    
        except Exception as e:
            print("에러:", e)
            time.sleep(60)

if name == "main":
    ru
