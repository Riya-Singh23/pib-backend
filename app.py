import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
from xml.etree import ElementTree as ET

app = Flask(__name__)
CORS(app)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

@app.route('/pib-news', methods=['GET'])
def get_pib_news():
    count = int(request.args.get('count', 10))
    news_list = []

    # Always go straight to Google News RSS (most reliable)
    try:
        rss_url = "https://news.google.com/rss/search?q=Department+Agriculture+Farmers+Welfare+India+government&hl=en-IN&gl=IN&ceid=IN:en"
        rss_response = requests.get(rss_url, headers=HEADERS, timeout=10)
        root = ET.fromstring(rss_response.content)

        for item in root.findall('.//item')[:count]:
            title = item.findtext('title', '')
            link = item.findtext('link', '')
            pub_date = item.findtext('pubDate', datetime.now().strftime("%a, %d %b %Y"))
            if title:
                news_list.append({
                    "title": title,
                    "link": link,
                    "published": pub_date
                })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    if not news_list:
        return jsonify({"error": "Could not fetch news"}), 503

    return jsonify({
        "status": "success",
        "total": len(news_list),
        "news": news_list
    })

if __name__ == "__main__":
    app.run(debug=True)
