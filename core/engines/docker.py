from selectolax.parser import HTMLParser
from urllib.parse import urlencode

CATEGORIES = ["general"]
WEIGHT = 1.0

def request(query, params):
    params["url"] = f"https://hub.docker.com/search?{urlencode({'q': query})}"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    # Docker Hub usa React, pero a veces deja pre-renderizados
    for node in tree.css('div[data-testid="searchResult"]'):
        title_node = node.css_first('a')
        desc_node = node.css_first('p')
        
        if title_node:
            results.append({
                "title": f"Docker Hub: {title_node.text().strip()}",
                "url": "https://hub.docker.com" + title_node.attributes.get('href', ''),
                "content": desc_node.text().strip() if desc_node else "Imagen de Docker.",
                "source": "docker"
            })
    return results
