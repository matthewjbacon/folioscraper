import os
from flask import Flask, request, jsonify
from requests_html import HTMLSession

app = Flask(__name__)

@app.route("/scrape", methods=["POST"])
def scrape():
    try:
        data = request.get_json()
        url = data.get("url")

        if not url or ("zillow.com" not in url and "realtor.com" not in url):
            return jsonify({"error": "Invalid or missing URL"}), 400

        session = HTMLSession()
        response = session.get(url)
        response.html.render(timeout=30)

        if "zillow.com" in url:
            address = response.html.find('[data-testid="home-details-summary-headline"]', first=True)
            price = response.html.find('[data-testid="price"]', first=True)
            facts = response.html.find('[data-testid="bed-bath-beyond-text"]')
            beds = facts[0].text if len(facts) > 0 else None
            baths = facts[1].text if len(facts) > 1 else None
            sqft = facts[2].text if len(facts) > 2 else None
        else:  # realtor.com
            address = response.html.find('.address', first=True)
            price = response.html.find('.rui__x3geed-0', first=True)  # You may need to adjust this selector
            beds = response.html.find('.rui__x3geed-2', first=True)
            baths = response.html.find('.rui__x3geed-3', first=True)
            sqft = response.html.find('.rui__x3geed-4', first=True)

        return jsonify({
            "address": address.text if address else None,
            "price": price.text if price else None,
            "beds": beds.text if beds else None,
            "baths": baths.text if baths else None,
            "sqft": sqft.text if sqft else None,
            "source_url": url
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
