from selectolax.parser import HTMLParser
from urllib.parse import urlencode

CATEGORIES = ["general"]
WEIGHT = 1.0

def request(query, params):
    params["url"] = f"https://search.seznam.cz/?q={query}"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    for node in tree.css('div.SearchResult'):
        title_node = node.css_first('h3 a')
        snippet_node = node.css_first('div.SearchResult-snippet')
        
        if title_node:
            results.append({
                "title": title_node.text().strip(),
                "url": title_node.attributes.get('href', ''),
                "content": snippet_node.text().strip() if snippet_node else "",
                "source": "seznam"
            })
    return results
