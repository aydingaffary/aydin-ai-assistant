"""Market service."""

import time

from providers.arzdigital_provider import ArzDigitalProvider


class MarketService:
    """Prepare market information for users."""

    CACHE_TIME = 300  # 5 minutes

    def __init__(self):
        self.provider = ArzDigitalProvider()
        self.cached_data = None
        self.last_update = 0

    def get_market_report(self) -> str:
        """Return formatted market report."""

        if self.cached_data is None or time.time() - self.last_update > self.CACHE_TIME:
            self.cached_data = self.provider.get_market_data()
            self.last_update = time.time()

        data = self.cached_data

        message = (
            "💵 ارز و طلا\n\n"
            f"💵 دلار: {data['dollar']:,} تومان\n"
            f"💶 یورو: {data['euro']:,} تومان\n\n"
            f"🥇 طلای ۱۸ عیار: {data['gold18']:,} تومان\n"
            f"🌎 انس جهانی طلا: {data['gold_ounce']:,} تومان\n"
            f"🪙 سکه امامی: {data['emami_coin']:,} تومان"
        )

        return message
