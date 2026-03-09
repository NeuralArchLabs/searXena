from selectolax.parser import HTMLParser
from urllib.parse import urlencode

CATEGORIES = ["images"]
WEIGHT = 1.0

def request(query, params):
    params["url"] = f"https://www.pinterest.com/search/pins/?q={query}"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    for node in tree.css('div[data-test-id="pin"]'):
        img = node.css_first('img')
        link = node.css_first('a')
        if img and link:
            results.append({
                "template": "images.html",
                "title": img.attributes.get('alt', 'Pinterest Pin'),
                "url": "https://www.pinterest.com" + link.attributes.get('href', ''),
                "img_src": img.attributes.get('src'),
                "thumbnail_src": img.attributes.get('src'),
                "source": "pinterest"
            })
    return results
