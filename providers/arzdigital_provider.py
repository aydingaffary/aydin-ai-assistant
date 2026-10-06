"""ArzDigital data provider."""

import json
import re
from concurrent.futures import ThreadPoolExecutor

import requests


class ArzDigitalProvider:
    """Get market prices from ArzDigital."""

    HEADERS = {
        "User-Agent": "Mozilla/5.0",
    }

    def __init__(self):
        self.session = requests.Session()

    def get_page_json_description(self, url: str) -> str | None:
        """Extract JSON-LD description from page."""

        response = self.session.get(
            url,
            headers=self.HEADERS,
            timeout=10,
        )

        response.raise_for_status()

        match = re.search(
            r'<script type="application/ld\+json">(.*?)</script>',
            response.text,
            re.S,
        )

        if not match:
            return None

        data = json.loads(match.group(1))

        for item in data.get("@graph", []):
            if "description" in item:
                return item["description"]

        return None

    def get_exchange_price(self, url: str) -> int | None:
        """Extract currency price."""

        description = self.get_page_json_description(url)

        if not description:
            return None

        match = re.search(
            r"(\d[\d,]+)\s*تومان",
            description,
        )

        if not match:
            return None

        return int(match.group(1).replace(",", ""))

    def get_market_data(self) -> dict:
        """Return main market prices."""

        urls = {
            "dollar": "https://arzdigital.com/currencies/united-states-dollar/",
            "euro": "https://arzdigital.com/currencies/euro/",
            "gold18": "https://arzdigital.com/gold/gold-gerami-18/",
            "gold_ounce": "https://arzdigital.com/gold/gold-ounce/",
            "emami_coin": "https://arzdigital.com/gold-coins/emami-gold/",
        }

        with ThreadPoolExecutor(max_workers=5) as executor:
            results = executor.map(
                self.get_exchange_price,
                urls.values(),
            )

        return dict(zip(urls.keys(), results))
