from selectolax.parser import HTMLParser
from urllib.parse import urlencode

CATEGORIES = ["general"]

def request(query, params):
    params["url"] = f"https://metager.org/meta/meta.ger3?{urlencode({'eingabe': query})}"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    for node in tree.css('div.result, section.result'):
        title_node = node.css_first('h2 a')
        snippet_node = node.css_first('div.result-description, p')
        
        if title_node:
            results.append({
                "title": title_node.text().strip(),
                "url": title_node.attributes.get('href', ''),
                "content": snippet_node.text().strip() if snippet_node else "",
                "score": 1.1 # MetaGer es de alta calidad
            })
    return results
