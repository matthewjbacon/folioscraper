from flask import Flask, request, jsonify
from zillow_scraper import scrape_zillow_data
import os

app = Flask(__name__)

@app.route("/scrape_zillow", methods=["POST"])
def scrape_zillow():
    try:
        data = request.get_json()
        url = data.get("url")

        if not url or "zillow.com" not in url:
            return jsonify({"error": "Invalid or missing Zillow URL"}), 400

        result = scrape_zillow_data(url)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)