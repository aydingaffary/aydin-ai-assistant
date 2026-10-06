import requests
import json
import re


def get_description(url):
    response = requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
        },
    )

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


urls = {
    "gold18": "https://arzdigital.com/gold/gold-gerami-18/",
    "ounce": "https://arzdigital.com/gold/gold-ounce/",
    "emami": "https://arzdigital.com/gold-coins/emami-gold/",
}


for name, url in urls.items():
    print("\n", name)
    print(get_description(url))
