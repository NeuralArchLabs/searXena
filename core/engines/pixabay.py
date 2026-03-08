from selectolax.parser import HTMLParser
from urllib.parse import urlencode

CATEGORIES = ["images", "videos"]

def request(query, params):
    params["url"] = f"https://pixabay.com/images/search/{urlencode({'q': query})}"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    # Imagenes
    for node in tree.css('div.cell--i699w img'):
        src = node.attributes.get('src') or node.attributes.get('data-lazy')
        if src:
            results.append({
                "template": "images.html",
                "title": node.attributes.get('alt', 'Pixabay Image'),
                "url": src,
                "img_src": src,
                "thumbnail_src": src,
                "content": ""
            })
            
    # Si esta en modo video, podriamos inyectar videos pero Pixabay separa los dominios
    return results
