from selectolax.parser import HTMLParser
from urllib.parse import urlencode

CATEGORIES = ["videos"]
WEIGHT = 1.3

def request(query, params):
    query_params = {
        "q": query,
        "qft": "",
        "first": (params.get("pageno", 1) - 1) * 35 + 1
    }
    params["url"] = f"https://www.bing.com/videos/search?{urlencode(query_params)}"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    for node in tree.css('div.dg_u'):
        title_node = node.css_first('div.title')
        url_node = node.css_first('a')
        img_node = node.css_first('img')
        
        if title_node and url_node:
            results.append({
                "template": "videos.html",
                "title": title_node.text().strip(),
                "url": "https://www.bing.com" + url_node.attributes.get('href', ''),
                "img_src": img_node.attributes.get('src') if img_node else None,
                "content": "Video de Bing.",
                "source": "bing"
            })
    return results
