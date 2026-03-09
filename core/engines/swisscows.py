from selectolax.parser import HTMLParser
from urllib.parse import urlencode

CATEGORIES = ["general"]
WEIGHT = 1.0

def request(query, params):
    query_params = {
        "query": query,
        "region": "es-ES"
    }
    params["url"] = f"https://swisscows.com/es/web?{urlencode(query_params)}"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    for node in tree.css('article.web-result'):
        title_node = node.css_first('h2 a')
        snippet_node = node.css_first('p')
        
        if title_node:
            results.append({
                "title": title_node.text().strip(),
                "url": title_node.attributes.get('href', ''),
                "content": snippet_node.text().strip() if snippet_node else "",
                "source": "swisscows"
            })
    return results
