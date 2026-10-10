
"""News service."""

from providers.news_rss import RSSNewsProvider


class NewsService:
    """Handle news fetching and source prioritization."""

    PERSIAN_SOURCE_PRIORITY = [
        "BBC فارسی",
        "ایسنا",
        "مهر",
        "خبرآنلاین",
        "رادیو فردا",
        "عصر ایران",
    ]

    ENGLISH_SOURCE_PRIORITY = [
        "BBC ENGLISH",
        "DW",
        "GUARDIAN",
        "AL JAZEERA",
        "NPR",
        "FRANCE24",
    ]

    TOPIC_KEYWORDS = {
        "ایران": [
            "iran", "iranian", "تهران", "ایران", "ایرانی", "hormuz",
        ],
        "آمریکا": [
            "usa", "america", "american", "united states",
            "آمریکا", "ترامپ",
        ],
        "انگلیس": [
            "uk", "britain", "british", "england",
            "بریتانیا", "انگلیس",
        ],
        "هوش مصنوعی": [
            "ai", "artificial intelligence", "machine learning",
            "هوش مصنوعی", "یادگیری ماشین",
        ],
    }

    def __init__(self) -> None:
        self.provider = RSSNewsProvider()

    def get_news(
        self,
        topic: str,
        limit: int = 3,
        offset: int = 0,
    ) -> list[dict]:
        """Return a page of recent news, prioritizing Persian sources."""

        if limit <= 0 or offset < 0:
            return []

        all_news = self.provider.get_news()

        if not all_news:
            return []

        topic = (topic or "").strip()
        search_words = self.TOPIC_KEYWORDS.get(topic.lower())

        if search_words:
            terms = [word.lower() for word in search_words]
            filtered_news = [
                item
                for item in all_news
                if any(
                    term in (
                        item.get("title", "")
                        + " "
                        + item.get("summary", "")
                    ).lower()
                    for term in terms
                )
            ]
        elif topic:
            filtered_news = [
                item
                for item in all_news
                if topic.lower()
                in (
                    item.get("title", "")
                    + " "
                    + item.get("summary", "")
                ).lower()
            ]
        else:
            filtered_news = all_news

        priority = (
            self.PERSIAN_SOURCE_PRIORITY
            + self.ENGLISH_SOURCE_PRIORITY
        )

        selected = []
        seen_links = set()
        seen_sources = set()

        # انتخاب حداکثر یک خبر از هر منبع، بر اساس اولویت.
        for source in priority:
            for item in filtered_news:
                item_source = item.get("source", "").upper()
                link = item.get("link", "")

                if item_source != source.upper():
                    continue

                if item_source in seen_sources:
                    continue

                if link and link in seen_links:
                    continue

                selected.append(item)
                seen_sources.add(item_source)

                if link:
                    seen_links.add(link)

                break

        # افزودن منابع ناشناخته، در صورت وجود.
        for item in filtered_news:
            item_source = item.get("source", "").upper()
            link = item.get("link", "")

            if item_source in seen_sources:
                continue

            if link and link in seen_links:
                continue

            selected.append(item)
            seen_sources.add(item_source)

            if link:
                seen_links.add(link)

        return selected[offset:offset + limit]
