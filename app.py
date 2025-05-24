from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

@app.route("/scrape", methods=["POST"])
def scrape():
    try:
        data = request.get_json()
        url = data.get("url")

        if not url or ("zillow.com" not in url and "realtor.com" not in url):
            return jsonify({"error": "Invalid or missing URL"}), 400

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        # Address
        address = soup.find("h1")
        address_text = address.text.strip() if address else None

        # Realtor.com logic
        if "realtor.com" in url:
            meta = soup.find("script", {"type": "application/ld+json"})
            if meta:
                json_text = meta.string
                match_beds = re.search(r'"numberOfRooms":\s*(\d+)', json_text)
                match_price = re.search(r'"price":\s*(\d+)', json_text)

                beds = match_beds.group(1) if match_beds else None
                price = f"${match_price.group(1)}" if match_price else None

                # Optional parsing of baths, sqft from HTML
                details = soup.find_all("li", class_="property-meta-item")
                baths = sqft = None
                for item in details:
                    text = item.get_text()
                    if "bath" in text.lower():
                        baths = text
                    elif "sqft" in text.lower():
                        sqft = text

                return jsonify({
                    "address": address_text,
                    "price": price,
                    "beds": beds,
                    "baths": baths,
                    "sqft": sqft,
                    "source_url": url
                })

        # Zillow logic (simplified)
        if "zillow.com" in url:
            title = soup.find("title")
            title_text = title.text if title else None
            return jsonify({
                "address": title_text,
                "price": None,
                "beds": None,
                "baths": None,
                "sqft": None,
                "source_url": url
            })

        return jsonify({"error": "Unsupported domain"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
