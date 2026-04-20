import requests
import schedule
import time
import feedparser
from sources.keyword_source import KeywordSource
from sources.news_source import NewsSource

PROJECTS = {
    "politik": ["Prabowo", "Anies Baswedan", "Ganjar"],
    "ekonomi": ["harga beras", "inflasi", "BBM"],
    "tech": ["AI", "startup", "teknologi"]
}

seen = set()

sources = [
    NewsSource(),
    KeywordSource()
]


def run_ingestion():
    print("\n[RUNNER] Multi-project ingestion cycle...")

    for project_id, keywords in PROJECTS.items():

        print(f"\n[PROJECT] {project_id}")

        for keyword in keywords:

            url = f"https://news.google.com/rss/search?q={keyword}&hl=id&gl=ID&ceid=ID:id"
            feed = feedparser.parse(url)

            for entry in feed.entries[:5]:
                text = entry.title

                key = f"{project_id}:{text}"

                if key in seen:
                    continue

                seen.add(key)

                print(f"[{project_id.upper()}][{keyword}] {text}")

                try:
                    API_URL = f"http://127.0.0.1:8000/projects/{project_id}/analyze"

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
job()

while True:
    schedule.run_pending()
    time.sleep(1)