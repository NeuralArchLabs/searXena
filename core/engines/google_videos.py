from selectolax.parser import HTMLParser
from urllib.parse import urlencode, unquote

CATEGORIES = ["videos"]

def request(query, params):
    # Usamos el modo video tbm=vid en Google o búsqueda Youtube directa
    # Modo video filtrado (Google Video Search es mejor para agregación)
    query_params = {
        "q": query,
        "tbm": "vid",
        "hl": "es",
        "num": 20
    }
    params["url"] = f"https://www.google.com/search?{urlencode(query_params)}"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    # Selectores de video en Google
    for node in tree.css('div.MjjYud, div.g, div.SoDRR'):
        title_node = node.css_first('h3')
        url_node = node.css_first('a')
        img_node = node.css_first('img')
        snippet_node = node.css_first('div.VwiC3b, .GI74S, .yK77Y')
        duration_node = node.css_first('span.MU1pAb, .B97S7')
        
        if title_node and url_node:
            img_src = img_node.attributes.get('src') or img_node.attributes.get('data-src')
            url = url_node.attributes.get('href', '')
            
            if url.startswith('/url?q='):
                url = unquote(url[7:].split('&sa=')[0])
                
            if url.startswith('http') and not "google.com" in url:
                results.append({
                    "template": "videos.html",
                    "title": title_node.text().strip(),
                    "url": url,
                    "img_src": img_src if (img_src and img_src.startswith('http')) else None,
                    "thumbnail_src": img_src if (img_src and img_src.startswith('http')) else None,
                    "content": f"Duración: {duration_node.text().strip()} | " if duration_node else "" + (snippet_node.text().strip() if snippet_node else "Video de alta calidad.")
                })
                
    return results
