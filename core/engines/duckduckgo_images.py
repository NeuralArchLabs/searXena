from selectolax.parser import HTMLParser
import re
import json

CATEGORIES = ["images"]

def request(query, params):
    # Usamos el modo imagen de DuckDuckGo que es MUCHO más fiable para scraping
    # 1. Necesitamos obtener un VQD (token de verificación) primero, pero DDG a veces permite peticiones directas a /i.js si el referer es correcto.
    # Intentamos la versión HTML "lite" que es más estable para scraping directo si falla el JS.
    params["url"] = f"https://duckduckgo.com/html/?q={query}&iax=images&ia=images"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    # Si la versión HTML falla, intentamos buscar bloques de imágenes en el DOM
    # Nota: DuckDuckGo a veces requiere JS para las imágenes reales, 
    # por lo que usaremos BING como motor de respaldo si DDG falla.
    
    for node in tree.css('div.tile--img'):
        img_node = node.css_first('img.tile--img__img')
        url_node = node.css_first('a.tile--img__sub')
        
        if img_node:
            src = img_node.attributes.get('src')
            if src and not src.startswith('http'):
                src = "https:" + src
                
            results.append({
                "template": "images.html",
                "title": img_node.attributes.get('alt', 'Imagen'),
                "url": url_node.attributes.get('href', src) if url_node else src,
                "img_src": src,
                "thumbnail_src": src,
                "content": "DuckDuckGo Image"
            })
            
    return results
