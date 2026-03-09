from selectolax.parser import HTMLParser
from urllib.parse import urlencode

CATEGORIES = ["images"]
WEIGHT = 1.0

def request(query, params):
    params["url"] = f"https://giphy.com/search/{query}"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    for node in tree.css('a[class*="StyledLink"]'):
        img = node.css_first('img')
        if img:
            src = img.attributes.get('src')
            if src:
                results.append({
                    "template": "images.html",
                    "title": "Giphy GIF",
                    "url": "https://giphy.com" + node.attributes.get('href', ''),
                    "img_src": src,
                    "thumbnail_src": src,
                    "source": "giphy"
                })
    return results
