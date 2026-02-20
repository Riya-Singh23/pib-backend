import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.pib.gov.in/",
}

@app.route('/pib-news', methods=['GET'])
def get_pib_news():
    count = int(request.args.get('count', 10))

    try:
        url = "https://pib.gov.in/allRel.aspx"
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        news_list = []

        # PIB press release items
        content_area = soup.find_all('div', class_='content-area')

        for item in soup.select('ul.release-list li, div.release-detail, .all-release li')[:count]:
            title_tag = item.find('a')
            if title_tag:
                title = title_tag.get_text(strip=True)
                link = title_tag.get('href', '')
                if link and not link.startswith('http'):
                    link = "https://pib.gov.in/" + link.lstrip('/')

                date_tag = item.find('span') or item.find('p')
                date = date_tag.get_text(strip=True) if date_tag else datetime.now().strftime("%d %b %Y")

                if title:
                    news_list.append({
                        "title": title,
                        "link": link,
                        "published": date
                    })

        # Fallback — try Google News RSS for PIB (no blocking)
        if not news_list:
            rss_url = "https://news.google.com/rss/search?q=site:pib.gov.in&hl=en-IN&gl=IN&ceid=IN:en"
            rss_response = requests.get(rss_url, headers=HEADERS, timeout=10)
            from xml.etree import ElementTree as ET
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

        if not news_list:
            return jsonify({"error": "Could not fetch PIB news"}), 503

        return jsonify({
            "status": "success",
            "total": len(news_list),
            "news": news_list
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)