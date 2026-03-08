import re
from selectolax.parser import HTMLParser

def request(query, params):
    # Startpage requiere una peticion POST compleja para evitar el bloqueo inmediato
    # Usamos la version "device" que es mas ligera
    params["method"] = "POST"
    params["url"] = "https://www.startpage.com/sp/search"
    params["data"] = {
        "query": query,
        "cat": "web",
        "sc": "TLsB0oITjZ8F21", # Token estatico aproximado, en produccion se extrae dinamicamente
        "language": "english"
    }
    params["headers"]["Referer"] = "https://www.startpage.com/"

def response(resp):
    results = []
    # Startpage a veces inyecta resultados en un script React o como HTML
    # Buscamos el patron de resultados estandar
    tree = HTMLParser(resp.text)
    
    for node in tree.css('div.result'):
        title_node = node.css_first('a.result-link, a.w-gl__result-title')
        snippet_node = node.css_first('p.result-snippet, div.w-gl__description')
        
        if title_node:
            results.append({
                "title": title_node.text().strip(),
                "url": title_node.attributes.get('href', ''),
                "content": snippet_node.text().strip() if snippet_node else ""
            })
    return results
