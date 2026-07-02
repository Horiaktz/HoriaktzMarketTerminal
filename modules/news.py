import feedparser

RSS = "https://feeds.finance.yahoo.com/rss/2.0/headline?s=%5EGSPC&region=US&lang=en-US"


def get_news(limit=5):
    feed = feedparser.parse(RSS)

    return [entry.title for entry in feed.entries[:limit]]