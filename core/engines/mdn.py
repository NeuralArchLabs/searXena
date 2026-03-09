from selectolax.parser import HTMLParser
from urllib.parse import urlencode

CATEGORIES = ["general"]
WEIGHT = 1.0

def request(query, params):
    query_params = {
        "q": query
    }
    params["url"] = f"https://developer.mozilla.org/es/search?{urlencode(query_params)}"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    for node in tree.css('div.search-result'):
        title_node = node.css_first('h3 a')
        snippet_node = node.css_first('p.search-result-excerpt')
        
        if title_node:
            results.append({
                "title": f"MDN: {title_node.text().strip()}",
                "url": "https://developer.mozilla.org" + title_node.attributes.get('href', ''),
                "content": snippet_node.text().strip() if snippet_node else "Documentación para desarrolladores.",
                "source": "mdn"
            })
    return results
