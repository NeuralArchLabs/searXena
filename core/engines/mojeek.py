from selectolax.parser import HTMLParser
from urllib.parse import urlencode

CATEGORIES = ["general"]

def request(query, params):
    params["url"] = f"https://www.mojeek.com/search?{urlencode({'q': query})}"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    for node in tree.css('li.result'):
        title_node = node.css_first('a.title')
        snippet_node = node.css_first('p.s')
        
        if title_node:
            results.append({
                "title": title_node.text().strip(),
                "url": title_node.attributes.get('href', ''),
                "content": snippet_node.text().strip() if snippet_node else "",
                "score": 0.9 # Mojeek es independiente, valioso para diversidad
            })
    return results
