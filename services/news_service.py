"""News service."""

from providers.news_rss import RSSNewsProvider


class NewsService:
    """Handle news fetching."""

    def __init__(self) -> None:
        self.provider = RSSNewsProvider()

    def get_news(
        self,
        topic: str,
        limit: int = 3,
    ) -> list[dict]:
        """Return diverse news related to topic."""

        all_news = self.provider.get_news()

        if not topic:
            return all_news[:limit]

        keywords = {
            "ایران": [
                "iran",
                "iranian",
                "tehran",
                "persian",
                "hormuz",
                "islamic republic",
            ],
            "آمریکا": [
                "usa",
                "america",
                "american",
                "us",
                "trump",
            ],
            "انگلیس": [
                "uk",
                "britain",
                "british",
                "england",
            ],
            "هوش مصنوعی": [
                "ai",
                "artificial intelligence",
                "machine learning",
            ],
        }

        search_words = keywords.get(
            topic.lower(),
            [topic.lower()],
        )

        filtered_news = []

        for item in all_news:
            text = (
                item.get("title", "")
                + " "
                + item.get("summary", "")
            ).lower()

            if any(
                word in text
                for word in search_words
            ):
                filtered_news.append(item)

        selected = []

        source_priority = [
            "BBC",
            "DW",
            "GUARDIAN",
            "AL JAZEERA",
            "NPR",
            "FRANCE24",
        ]

        # اولویت دادن به منابع مختلف
        for source in source_priority:
            for item in filtered_news:
                if item["source"] == source:
                    selected.append(item)
                    break

            if len(selected) == limit:
                break

        # اگر منبع کافی نبود، از همان منابع باقی‌مانده پر کن
        if len(selected) < limit:
            for item in filtered_news:
                if item not in selected:
                    selected.append(item)

                if len(selected) == limit:
                    break

        return selected