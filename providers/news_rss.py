
"""RSS news provider."""

import logging

import feedparser

logger = logging.getLogger(__name__)


class RSSNewsProvider:
    """Fetch news from Persian and English RSS feeds."""

    SOURCES = {
        # منابع فارسی، به ترتیب اولویت
        "BBC فارسی": "https://feeds.bbci.co.uk/persian/rss.xml",
        "ایسنا": "https://www.isna.ir/rss",
        "مهر": "https://www.mehrnews.com/rss",
        "خبرآنلاین": "https://www.khabaronline.ir/rss",
        "رادیو فردا": "https://www.radiofarda.com/api/zrttpol-vomx-tpeoogpi",
        "عصر ایران": "https://www.asriran.com/fa/rss/allnews",

        # منابع انگلیسی
        "BBC English": "https://feeds.bbci.co.uk/news/rss.xml",
        "DW": "https://rss.dw.com/rdf/rss-en-all",
        "Guardian": "https://www.theguardian.com/world/rss",
        "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
        "NPR": "https://feeds.npr.org/1001/rss.xml",
        "France24": "https://www.france24.com/en/rss",
    }

    def get_news(
        self,
        source: str | None = None,
        limit: int = 5,
    ) -> list[dict]:
        """Return latest news items from available RSS feeds."""

        news = []

        if source in self.SOURCES:
            sources = {source: self.SOURCES[source]}
        else:
            sources = self.SOURCES

        for name, url in sources.items():
            try:
                feed = feedparser.parse(url)

                if getattr(feed, "bozo", False):
                    logger.warning(
                        "RSS feed returned a parsing warning (%s)",
                        name,
                    )

                for item in feed.entries[:limit]:
                    title = getattr(item, "title", "").strip()
                    summary = getattr(item, "summary", "").strip()
                    link = getattr(item, "link", "").strip()

                    if not title or not link:
                        continue

                    news.append(
                        {
                            "source": name.upper(),
                            "title": title,
                            "summary": summary,
                            "link": link,
                        }
                    )

            except Exception:
                logger.exception("News source failed (%s)", name)

        return news
