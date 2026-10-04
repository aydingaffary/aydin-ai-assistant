"""Market service."""

from providers.arzdigital_provider import ArzDigitalProvider


class MarketService:
    """Prepare market information for users."""

    def __init__(self):
        self.provider = ArzDigitalProvider()

    def get_market_report(self) -> str:
        """Return formatted market report."""

        data = self.provider.get_market_data()

        message = (
            "💵 ارز و طلا\n\n"
            f"💵 دلار: {data['dollar']:,} تومان\n"
            f"💶 یورو: {data['euro']:,} تومان\n\n"
            f"🥇 طلای ۱۸ عیار: {data['gold18']:,} تومان\n"
            f"🌎 انس جهانی طلا: {data['gold_ounce']:,} تومان\n"
            f"🪙 سکه امامی: {data['emami_coin']:,} تومان"
        )

        return message
