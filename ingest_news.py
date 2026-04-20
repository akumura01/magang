import feedparser
import requests
import schedule
import time

PROJECT_ID = "politik"
API_URL = f"http://127.0.0.1:8000/projects/{PROJECT_ID}/analyze"

RSS_URL = "https://news.google.com/rss/search?q=politik+Indonesia&hl=id&gl=ID&ceid=ID:id"

seen_titles = set()


def fetch_news():
    feed = feedparser.parse(RSS_URL)

    for entry in feed.entries[:10]:
        text = entry.title

        if text in seen_titles:
            continue

        seen_titles.add(text)

        print(f"[INGEST] Sending: {text}")

        try:
            response = requests.post(API_URL, json={"text": text})

            if response.status_code == 200:
                data = response.json()
                print(f"[SUCCESS] Sentiment: {data.get('sentiment')}")
            else:
                print(f"[ERROR] Status: {response.status_code}")

        except Exception as e:
            print(f"[EXCEPTION] {e}")


def job():
    print("\n[JOB] Running scheduled news ingestion...")
    fetch_news()


schedule.every(1).minutes.do(job)

print("[SYSTEM] Scheduler started...")

while True:
    schedule.run_pending()
    time.sleep(1)