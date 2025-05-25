from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
from urllib.parse import urlparse

app = Flask(__name__)

def scrape_zillow(page):
    try:
        # Wait for the price element to ensure the page has loaded
        page.wait_for_selector('[data-testid="price"]', timeout=10000)

        # Extract address
        address_el = page.query_selector('h1')
        address = address_el.inner_text().strip() if address_el else None

        # Extract price
        price_el = page.query_selector('[data-testid="price"]')
        price = price_el.inner_text().strip() if price_el else None

        # Extract facts (beds, baths, sqft)
        facts = page.query_selector_all('[data-testid="bed-bath-beyond"] [data-testid="bed-bath-item"]')
        beds = facts[0].inner_text().strip() if len(facts) > 0 else None
        baths = facts[1].inner_text().strip() if len(facts) > 1 else None
        sqft = facts[2].inner_text().strip() if len(facts) > 2 else None

        return {
            "platform": "Zillow",
            "address": address,
            "price": price,
            "beds": beds,
            "baths": baths,
            "sqft": sqft
        }
    except Exception as e:
        print(f"Error scraping Zillow: {e}")
        return {
            "platform": "Zillow",
            "address": None,
            "price": None,
            "beds": None,
            "baths": None,
            "sqft": None
        }

def scrape_realtor(page):
    page.wait_for_timeout(3000)
    address_el = page.query_selector('span[itemprop="streetAddress"]')
    price_el = page.query_selector('span[data-label="pc-price"]')
    beds_el = page.query_selector('li[data-label="pc-meta-beds"]')
    baths_el = page.query_selector('li[data-label="pc-meta-baths"]')
    sqft_el = page.query_selector('li[data-label="pc-meta-sqft"]')

    return {
        "platform": "Realtor",
        "address": address_el.inner_text() if address_el else None,
        "price": price_el.inner_text() if price_el else None,
        "beds": beds_el.inner_text() if beds_el else None,
        "baths": baths_el.inner_text() if baths_el else None,
        "sqft": sqft_el.inner_text() if sqft_el else None
    }

@app.route("/scrape", methods=["POST"])
def scrape():
    try:
        data = request.get_json()
        url = data.get("url")
        if not url:
            return jsonify({"error": "Missing URL"}), 400

        domain = urlparse(url).netloc.lower()

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url, wait_until="domcontentloaded")

            if "zillow.com" in domain:
                result = scrape_zillow(page)
            elif "realtor.com" in domain:
                result = scrape_realtor(page)
            else:
                return jsonify({"error": "Unsupported domain"}), 400

            browser.close()

        result["source_url"] = url
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
