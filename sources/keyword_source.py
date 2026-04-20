import feedparser
from sources.base import BaseSource


class KeywordSource(BaseSource):

    def __init__(self):
        self.keywords = [
            "Prabowo",
            "Anies Baswedan",
            "Ganjar",
            "harga beras"
        ]

    def fetch(self):
        results = []

        for keyword in self.keywords:
            url = f"https://news.google.com/rss/search?q={keyword}&hl=id&gl=ID&ceid=ID:id"
            feed = feedparser.parse(url)

            for entry in feed.entries[:5]:  # limit per keyword
                results.append({
                    "text": entry.title,
                    "keyword": keyword
                })

        return results

    def normalize(self, raw):
        data = []

        for item in raw:
            data.append({
                "text": item["text"],
                "source": f"keyword:{item['keyword']}"
            })

        return data
    