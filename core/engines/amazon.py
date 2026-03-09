from selectolax.parser import HTMLParser
from urllib.parse import urlencode

NAME = "amazon"
CATEGORIES = ["shopping"]
WEIGHT = 1.5

def request(query, params):
    # Amazon es estricto, usamos un User-Agent moderno y parámetros mínimos
    params["url"] = f"https://www.google.com/search?q=site:amazon.com+{query}"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    # Extraer resultados de búsqueda de Google que apuntan a Amazon
    for node in tree.css('div.g'):
        title_node = node.css_first('h3')
        url_node = node.css_first('a')
        snippet_node = node.css_first('div.VwiC3b')
        
        if title_node and url_node:
            url = url_node.attributes.get('href', '')
            if "amazon.com" in url:
                results.append({
                    "title": title_node.text().strip().replace("Amazon.com: ", ""),
                    "url": url,
                    "content": snippet_node.text().strip() if snippet_node else "Producto en Amazon.",
                    "source": "amazon",
                    "template": "shopping.html"
                })
    return results
