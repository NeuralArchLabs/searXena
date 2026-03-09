from selectolax.parser import HTMLParser
from urllib.parse import urlencode

CATEGORIES = ["social", "general"]
WEIGHT = 1.0

def request(query, params):
    # Usar búsqueda de repositorios de GitHub
    params["url"] = f"https://github.com/search?{urlencode({'q': query, 'type': 'repositories'})}"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    # GitHub cambió su layout recientemente a React, pero suele dejar fragmentos
    for node in tree.css('div.search-title, div[data-testid="results-list"] div.Box-sc-dq7h35-0'):
        title_node = node.css_first('a')
        desc_node = node.css_first('p')
        
        if title_node:
            results.append({
                "title": f"GitHub: {title_node.text().strip()}",
                "url": "https://github.com" + title_node.attributes.get('href', ''),
                "content": desc_node.text().strip() if desc_node else "Repositorio en GitHub.",
                "source": "github"
            })
    return results
