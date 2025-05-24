from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
from urllib.parse import urlparse

app = Flask(__name__)

def scrape_zillow(page):
    page.wait_for_timeout(4000)  # wait for content to fully load

    address_el = page.query_selector('h1[data-testid="home-details-summary-headline"]')
    price_el = page.query_selector('span[data-testid="price"]')

    facts = page.query_selector_all('ul[data-testid="bed-bath-beyond"] li span')

    beds = facts[0].inner_text() if len(facts) > 0 else None
    baths = facts[1].inner_text() if len(facts) > 1 else None
    sqft = facts[2].inner_text() if len(facts) > 2 else None

    return {
        "platform": "Zillow",
        "address": address_el.inner_text() if address_el else None,
        "price": price_el.inner_text() if price_el else None,
        "beds": beds,
        "baths": baths,
        "sqft": sqft
    }

def scrape_realtor(page):
    page.wait_for_timeout(3000)  # wait for page load (adjust if needed)
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
