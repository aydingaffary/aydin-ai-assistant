import requests
from bs4 import BeautifulSoup

URLS = {
    "dollar": "https://arzdigital.com/currencies/united-states-dollar/",
}


for name, url in URLS.items():
    print("=" * 50)
    print(name)

    response = requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
        },
        timeout=10,
    )

    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )

    texts = soup.find_all(string=lambda x: x and "تومان" in x)

    for text in texts[:10]:
        print(text.strip())
