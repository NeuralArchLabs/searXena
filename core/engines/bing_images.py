from selectolax.parser import HTMLParser
from urllib.parse import urlencode

CATEGORIES = ["images"]
WEIGHT = 1.3

def request(query, params):
    query_params = {
        "q": query,
        "first": (params.get("pageno", 1) - 1) * 35 + 1,
        "scenario": "ImageBasicHover",
        "datsrc": "I"
    }
    params["url"] = f"https://www.bing.com/images/search?{urlencode(query_params)}"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    for node in tree.css('div.imgpt'):
        img_node = node.css_first('img.mimg')
        url_node = node.css_first('a.iusc')
        
        if img_node:
            src = img_node.attributes.get('src')
            if src and not src.startswith('http'): src = "https://www.bing.com" + src
            
            results.append({
                "template": "images.html",
                "title": img_node.attributes.get('alt', 'Bing Image'),
                "url": url_node.attributes.get('href', src) if url_node else src,
                "img_src": src,
                "thumbnail_src": src,
                "source": "bing"
            })
    return results
