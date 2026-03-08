from selectolax.parser import HTMLParser
from urllib.parse import urlencode

CATEGORIES = ["images"]

def request(query, params):
    params["url"] = f"https://unsplash.com/s/photos/{urlencode({'q': query})}"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    # Unsplash inyecta imagenes en un formato de grid moderno
    for node in tree.css('img[data-test="photo-grid-multi-col-img"]'):
        src = node.attributes.get('src')
        if src:
            results.append({
                "template": "images.html",
                "title": node.attributes.get('alt', 'Unsplash Image'),
                "url": src, # URL directa
                "img_src": src + "&w=800&q=80", # Ajustar calidad
                "thumbnail_src": src + "&w=300&q=50",
                "content": ""
            })
    return results
