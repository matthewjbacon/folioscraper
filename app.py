from flask import Flask, request, jsonify
from requests_html import HTMLSession

app = Flask(__name__)

def scrape_zillow(session, url):
    response = session.get(url)
    response.html.render(timeout=30)

    address = response.html.find('[data-testid="home-details-summary-headline"]', first=True)
    price = response.html.find('[data-testid="price"]', first=True)
    facts = response.html.find('[data-testid="bed-bath-beyond-text"]')

    beds = facts[0].text if len(facts) > 0 else None
    baths = facts[1].text if len(facts) > 1 else None
    sqft = facts[2].text if len(facts) > 2 else None

    return {
        "address": address.text if address else None,
        "price": price.text if price else None,
        "beds": beds,
        "baths": baths,
        "sqft": sqft,
        "source_url": url
    }

def scrape_realtor(session, url):
    response = session.get(url)
    response.html.render(timeout=30)

    address = response.html.find('h1[data-testid="address"]', first=True)
    price = response.html.find('span[data-label="pc-price"]', first=True)
    beds = response.html.find('li[data-label="pc-meta-beds"] span', first=True)
    baths = response.html.find('li[data-label="pc-meta-baths"] span', first=True)
    sqft = response.html.find('li[data-label="pc-meta-sqft"] span', first=True)

    return {
        "address": address.text if address else None,
        "price": price.text if price else None,
        "beds": beds.text if beds else None,
        "baths": baths.text if baths else None,
        "sqft": sqft.text if sqft else None,
        "source_url": url
    }

@app.route("/scrape_property", methods=["POST"])
def scrape_property():
    try:
        data = request.get_json()
        url = data.get("url")

        if not url:
            return jsonify({"error": "Missing URL"}), 400

        session = HTMLSession()

        if "zillow.com" in url:
            result = scrape_zillow(session, url)
        elif "realtor.com" in url:
            result = scrape_realtor(session, url)
        else:
            return jsonify({"error": "URL must be from zillow.com or realtor.com"}), 400

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)