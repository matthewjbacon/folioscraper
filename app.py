from flask import Flask, request, jsonify
from requests_html import HTMLSession
from urllib.parse import urlparse

app = Flask(__name__)

@app.route("/scrape", methods=["POST"])
def scrape():
    try:
        data = request.get_json()
        url = data.get("url")

        if not url:
            return jsonify({"error": "Missing URL"}), 400

        # Normalize and check domain
        domain = urlparse(url).netloc.lower()

        session = HTMLSession()
        response = session.get(url)
        response.html.render(timeout=30)

        if "zillow.com" in domain:
            address = response.html.find('[data-testid="home-details-summary-headline"]', first=True)
            price = response.html.find('[data-testid="price"]', first=True)
            facts = response.html.find('[data-testid="bed-bath-beyond-text"]')

            beds = facts[0].text if len(facts) > 0 else None
            baths = facts[1].text if len(facts) > 1 else None
            sqft = facts[2].text if len(facts) > 2 else None

            return jsonify({
                "platform": "Zillow",
                "address": address.text if address else None,
                "price": price.text if price else None,
                "beds": beds,
                "baths": baths,
                "sqft": sqft,
                "source_url": url
            })

        elif "realtor.com" in domain:
            address = response.html.find('span[itemprop="streetAddress"]', first=True)
            price = response.html.find('span[data-label="pc-price"]', first=True)
            beds = response.html.find('li[data-label="pc-meta-beds"]', first=True)
            baths = response.html.find('li[data-label="pc-meta-baths"]', first=True)
            sqft = response.html.find('li[data-label="pc-meta-sqft"]', first=True)

            return jsonify({
                "platform": "Realtor",
                "address": address.text if address else None,
                "price": price.text if price else None,
                "beds": beds.text if beds else None,
                "baths": baths.text if baths else None,
                "sqft": sqft.text if sqft else None,
                "source_url": url
            })

        else:
            return jsonify({"error": "Unsupported domain"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
