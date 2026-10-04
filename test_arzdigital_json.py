import json
import requests
from bs4 import BeautifulSoup

url = "https://arzdigital.com/currencies/united-states-dollar/"


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


script = soup.find(
    "script",
    type="application/ld+json",
)


data = json.loads(script.text)


for item in data["@graph"]:
    if "currentExchangeRate" in item:
        print(item["currentExchangeRate"])
