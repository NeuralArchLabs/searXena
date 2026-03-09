from selectolax.parser import HTMLParser
from urllib.parse import urlencode

CATEGORIES = ["videos"]
WEIGHT = 1.0

def request(query, params):
    params["url"] = f"https://www.dailymotion.com/search/{query}"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    # Dailymotion suele inyectar JSON en scripts, pero buscaremos nodos HTML
    for node in tree.css('div.video-card'):
        title_node = node.css_first('div.title')
        url_node = node.css_first('a')
        img_node = node.css_first('img')
        
        if title_node and url_node:
            results.append({
                "template": "videos.html",
                "title": title_node.text().strip(),
                "url": "https://www.dailymotion.com" + url_node.attributes.get('href', ''),
                "img_src": img_node.attributes.get('src') if img_node else None,
                "content": "Video en Dailymotion.",
                "source": "dailymotion"
            })
    return results
