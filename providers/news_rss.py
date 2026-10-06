"""RSS news provider."""

import feedparser
import logging
logger = logging.getLogger(__name__)
class RSSNewsProvider:
    """Fetch news from multiple RSS feeds."""

    SOURCES = {
        "BBC": "https://feeds.bbci.co.uk/news/rss.xml",
        "DW": "https://rss.dw.com/rdf/rss-en-all",
        "Guardian": "https://www.theguardian.com/world/rss",
        "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
        "NPR": "https://feeds.npr.org/1001/rss.xml",
        "France24": "https://www.france24.com/en/rss",
        "ISNA": "https://www.isna.ir/rss",
    }

    def get_news(
        self,
        source: str | None = None,
        limit: int = 5,
    ) -> list[dict]:
        """Return latest news items."""

        news = []

        sources = (
            {source: self.SOURCES[source]}
            if source in self.SOURCES
            else self.SOURCES
        )

        for name, url in sources.items():
            try:
                feed = feedparser.parse(url)

                for item in feed.entries:
                    news.append(
                        {
                            "source": name.upper(),
                            "title": item.title,
                            "summary": getattr(item, "summary", ""),
                            "link": item.link,
                        }
                    )

            except Exception as error:
                logger.warning(
                    "News source failed (%s): %s",
                    name,
                    error,
                )

        return news