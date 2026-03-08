import random
import time
import string
from urllib.parse import urlencode, unquote
from selectolax.parser import HTMLParser

CATEGORIES = ["general", "news", "videos", "images"]

def ui_async(start: int) -> str:
    # Simulación de identificadores de sesión de Google para mejores resultados
    _arcid_range = string.ascii_letters + string.digits + "_-"
    arc_rnd = "".join(random.choices(_arcid_range, k=23))
    return f"arc_id:srp_{arc_rnd}_1{start:02},use_ac:true,_fmt:prog"

def request_categorized(query, category, params):
    # Google usa bloques de 10-20 resultados. 
    # SearXNG suele pedir de 10 en 10, pero aquí pediremos 20 para densidad masiva.
    start = (params.get("pageno", 1) - 1) * 20
    
    query_params = {
        "q": query,
        "hl": "es",
        "start": start,
        "num": 20, # ¡DOBLE DENSIDAD!
        "filter": "0"
    }
    
    if category == "news":
        query_params["tbm"] = "nws"
    elif category == "videos":
        query_params["tbm"] = "vid"
    elif category == "images":
        query_params["tbm"] = "isch"
    else:
        # Modo Async para resultados frescos y densos
        query_params["asearch"] = "arc"
        query_params["async"] = ui_async(start)
    
    params["url"] = f"https://www.google.com/search?{urlencode(query_params)}"
    params["headers"]["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"

def request(query, params):
    request_categorized(query, "general", params)

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    # 1. Scraping Web denso
    for node in tree.css('div.MjjYud, div.g, div.SoDRR, div.WlyS9b'):
        title_node = node.css_first('h3, div[role="link"] span, .mCBkyc')
        url_node = node.css_first('a')
        snippet_node = node.css_first('div.VwiC3b, .GI74S, .yK77Y, .Y69UXb')
        
        if title_node and url_node:
            title = title_node.text().strip()
            url = url_node.attributes.get('href', '')
            
            # Limpiar redirecciones de Google
            if url.startswith('/url?q='):
                url = unquote(url[7:].split('&sa=')[0])
            
            if url.startswith('http') and not "google.com" in url:
                results.append({
                    "title": title,
                    "url": url,
                    "content": snippet_node.text().strip() if snippet_node else "Información de Google."
                })
    
    # 2. Scraping Imágenes (si aplica)
    if "tbm=isch" in resp.search_params.get("url", ""):
        for node in tree.css('img.rg_i, img.Q4iVhc'):
            src = node.attributes.get('src') or node.attributes.get('data-src')
            if src:
                results.append({
                    "template": "images.html",
                    "title": "Google Image",
                    "url": src,
                    "img_src": src,
                    "thumbnail_src": src,
                    "content": ""
                })

    return results
