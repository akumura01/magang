import feedparser
import requests

API_URL = "http://127.0.0.1:8000/analyze"

# Google News RSS (Indonesia politics)
RSS_URL = "https://news.google.com/rss/search?q=politik+Indonesia&hl=id&gl=ID&ceid=ID:id"

def fetch_news():
    feed = feedparser.parse(RSS_URL)

    for entry in feed.entries[:10]:  # limit 10 news
        text = entry.title

        print(f"Sending: {text}")

        response = requests.post(API_URL, json={"text": text})

        if response.status_code == 200:
            print("Saved:", response.json())
        else:
            print("Error:", response.status_code)

import schedule
import time

def job():
    print("Running scheduled news ingestion...")
    fetch_news()

# Run every 10 minutes (you can change this)
schedule.every(10).minutes.do(job)

print("Scheduler started...")

while True:
    schedule.run_pending()
    time.sleep(1)
    