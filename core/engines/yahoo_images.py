from selectolax.parser import HTMLParser
from urllib.parse import urlencode, unquote
from utils import LANGUAGE_MAP

CATEGORIES = ["images"]
WEIGHT = 1.0

def request(query, params):
    lang = params.get("language", "es")
    lang_code = LANGUAGE_MAP.get("yahoo", {}).get(lang, "en-US")
    
    query_params = {
        "p": query,
        "ei": "UTF-8",
        "b": (params.get("pageno", 1) - 1) * 60 + 1,
        "setlang": lang_code
    }
    params["url"] = f"https://images.search.yahoo.com/search/images?{urlencode(query_params)}"
    params["headers"]["Accept-Language"] = f"{lang_code},{lang};q=0.9,en;q=0.8"
    params["headers"]["Accept-Encoding"] = "gzip, deflate"
    params["headers"]["Referer"] = "https://images.search.yahoo.com/"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    for node in tree.css('li.ld'):
        img_node = node.css_first('img')
        link_node = node.css_first('a')
        
        if img_node and link_node:
            url = link_node.attributes.get('href', '')
            src = img_node.attributes.get('data-src') or img_node.attributes.get('src')
            
            if "r.search.yahoo.com" in url:
                try:
                    if '/RU=' in url:
                        url = unquote(url.split('/RU=')[1].split('/RK=')[0])
                except: pass

            if url and src:
                results.append({
                    "template": "images.html",
                    "title": img_node.attributes.get('alt', 'Yahoo Image'),
                    "url": url,
                    "img_src": src,
                    "thumbnail_src": src,
                    "source": "yahoo_images"
                })
    return results
