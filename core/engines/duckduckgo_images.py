import httpx
from utils import fetch_vqd
from urllib.parse import urlencode

CATEGORIES = ["images"]
WEIGHT = 2.0

async def request(query, params):
    # Usar un cliente temporal para obtener el VQD (Validation Query Digest)
    async with httpx.AsyncClient(timeout=5.0, follow_redirects=True) as client:
        vqd = await fetch_vqd(query, client)
        
    if not vqd:
        # Fallback si falla el VQD (usando versión Lite pre-renderizada)
        params["url"] = f"https://duckduckgo.com/html/?q={query}&iax=images&ia=images"
        return

    # Usar el API JSON de DuckDuckGo para imágenes (mucho más rico)
    query_params = {
        "l": "wt-wt",
        "o": "json",
        "q": query,
        "vqd": vqd,
        "f": ",,,",
        "p": 1
    }
    params["url"] = f"https://duckduckgo.com/i.js?{urlencode(query_params)}"

def response(resp):
    results = []
    # Si es JSON (API real)
    try:
        data = resp.json()
        for item in data.get("results", []):
            results.append({
                "template": "images.html",
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "img_src": item.get("image", ""),
                "thumbnail_src": item.get("thumbnail", ""),
                "source": "duckduckgo"
            })
        if results: return results
    except Exception:
        pass
        
    # Fallback Scraper (si el API falló)
    from selectolax.parser import HTMLParser
    tree = HTMLParser(resp.text)
    for node in tree.css('div.tile--img'):
        img_node = node.css_first('img.tile--img__img')
        if img_node:
            src = img_node.attributes.get('src')
            if src and not src.startswith('http'): src = "https:" + src
            results.append({
                "template": "images.html",
                "title": img_node.attributes.get('alt', 'Imagen'),
                "url": src,
                "img_src": src,
                "thumbnail_src": src,
                "source": "duckduckgo"
            })
    return results
