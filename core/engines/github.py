from selectolax.parser import HTMLParser
from urllib.parse import urlencode

CATEGORIES = ["it"]

def request(query, params):
    params["url"] = f"https://github.com/search?q={urlencode({'q': query})}&type=repositories"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    # Github cambia su grid a menudo, pero estos selectores son estables para repositorios
    for node in tree.css('div.search-title, div.Box-row'):
        title_node = node.css_first('a[data-hydro-click], h3 a, a.v-align-middle')
        snippet_node = node.css_first('p.mb-1, .f4')
        
        if title_node:
            url = "https://github.com" + title_node.attributes.get('href', '')
            results.append({
                "title": title_node.text().strip(),
                "url": url,
                "content": snippet_node.text().strip() if snippet_node else "Repositorio en GitHub.",
                "score": 1.5
            })
    return results
