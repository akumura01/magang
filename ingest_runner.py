import requests
import schedule
import time

from sources.news_source import NewsSource

PROJECT_ID = "politik"
API_URL = f"http://127.0.0.1:8000/projects/{PROJECT_ID}/analyze"

seen = set()

sources = [
    NewsSource()
]


def run_ingestion():
    print("\n[RUNNER] Starting ingestion cycle...")

    for source in sources:
        raw = source.fetch()
        data = source.normalize(raw)

        for item in data:
            text = item["text"]

            if text in seen:
                continue

            seen.add(text)

            print(f"[{item['source'].upper()}] {text}")

            try:
                res = requests.post(API_URL, json={"text": text})

                if res.status_code == 200:
                    print("[OK]")
                else:
                    print("[FAIL]", res.status_code)

            except Exception as e:
                print("[ERROR]", e)


def job():
    run_ingestion()


schedule.every(10).minutes.do(job)

print("[SYSTEM] Multi-source ingestion started...")

while True:
    schedule.run_pending()
    time.sleep(1)