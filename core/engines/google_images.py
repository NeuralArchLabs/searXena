from selectolax.parser import HTMLParser
from urllib.parse import urlencode, unquote

CATEGORIES = ["images"]

def request(query, params):
    # Google Images modo móvil es más fácil de scrapear sin JS
    query_params = {
        "q": query,
        "tbm": "isch",
        "tbs": "rimg",
        "hl": "es"
    }
    params["url"] = f"https://www.google.com/search?{urlencode(query_params)}"
    params["headers"]["User-Agent"] = "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    # En la versión móvil, las imágenes suelen ser <img> simples o dentro de un <td>/<div>
    for node in tree.css('img.rg_i, img.y_a, img[src*="gstatic"]'):
        src = node.attributes.get('src') or node.attributes.get('data-src')
        if src and src.startswith('http'):
            results.append({
                "template": "images.html",
                "title": node.attributes.get('alt', 'Google Image'),
                "url": src,
                "img_src": src,
                "thumbnail_src": src,
                "content": "Google Images Mobile"
            })
            
    return results
