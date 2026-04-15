import feedparser
from sources.base import BaseSource


class NewsSource(BaseSource):

    def __init__(self):
        self.RSS_URL = "https://news.google.com/rss/search?q=politik+Indonesia&hl=id&gl=ID&ceid=ID:id"

    def fetch(self):
        feed = feedparser.parse(self.RSS_URL)
        return feed.entries[:10]

    def normalize(self, entries):
        data = []

        for entry in entries:
            data.append({
                "text": entry.title,
                "source": "news"
            })

        return data