import requests
from bs4 import BeautifulSoup
import re
import json

def scrape_zillow_data(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch page. Status code: {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")
    data_script = soup.find("script", string=re.compile("type: 'ForSale'"))

    if not data_script:
        raise Exception("Zillow data script not found.")

    json_text = re.search(r'<!--(.*?)-->', str(data_script), re.DOTALL)
    if not json_text:
        raise Exception("Failed to extract JSON from script.")

    data = json.loads(json_text.group(1))

    return {
        "address": data.get("address"),
        "price": data.get("price"),
        "beds": data.get("bedrooms"),
        "baths": data.get("bathrooms"),
        "sqft": data.get("livingArea"),
        "zpid": data.get("zpid"),
        "source_url": url
    }
