import random
from urllib.parse import urlencode, unquote
from selectolax.parser import HTMLParser

CATEGORIES = ["general", "news", "videos", "images"]
WEIGHT = 1.5

def request(query, params):
    # Google estándar, robusto y limpio (Estilo SearXNG)
    offset = (params.get("pageno", 1) - 1) * 10
    
    query_params = {
        "q": query,
        "hl": "es",
        "start": offset,
        "num": 20, # Pedimos 20 para asegurar que después del filtrado queden bastantes
    }
    
    if params.get("category") == "news":
        query_params["tbm"] = "nws"
    elif params.get("category") == "videos":
        query_params["tbm"] = "vid"
    elif params.get("category") == "images":
        query_params["tbm"] = "isch"
        
    params["url"] = f"https://www.google.com/search?{urlencode(query_params)}"
    # Headers mínimos para evitar detección como bot complejo
    params["headers"]["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    # Selectores universales de Google
    for node in tree.css('div.g, div.MjjYud'):
        title_node = node.css_first('h3')
        url_node = node.css_first('a')
        snippet_node = node.css_first('div.VwiC3b, .yfY60c, .itX33, .BNeawe')
        
        if title_node and url_node:
            url = url_node.attributes.get('href', '')
            if url.startswith('/url?q='):
                url = unquote(url[7:].split('&sa=')[0])
            
            if url.startswith('http') and not "google.com" in url:
                results.append({
                    "title": title_node.text().strip(),
                    "url": url,
                    "content": snippet_node.text().strip() if snippet_node else "Ver más en Google.",
                    "source": "google"
                })
                
    # Imágenes
    if "tbm=isch" in resp.url:
        for node in tree.css('div.isv-r'):
            img_node = node.css_first('img')
            link_node = node.css_first('a[href^="http"]')
            if img_node:
                src = img_node.attributes.get('src') or img_node.attributes.get('data-src')
                if src:
                    results.append({
                        "template": "images.html",
                        "title": "Imagen de Google",
                        "url": link_node.attributes.get('href', '#') if link_node else "#",
                        "img_src": src,
                        "source": "google"
                    })

    return results
