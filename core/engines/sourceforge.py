from selectolax.parser import HTMLParser
from urllib.parse import urlencode

CATEGORIES = ["general"]
WEIGHT = 1.0

def request(query, params):
    params["url"] = f"https://sourceforge.net/directory/?q={query}"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    for node in tree.css('li.project-card'):
        title_node = node.css_first('h2.result-title')
        link_node = node.css_first('a.result-link')
        snippet_node = node.css_first('p.description')
        
        if title_node and link_node:
            results.append({
                "title": f"SourceForge: {title_node.text().strip()}",
                "url": "https://sourceforge.net" + link_node.attributes.get('href', ''),
                "content": snippet_node.text().strip() if snippet_node else "Software en SourceForge.",
                "source": "sourceforge"
            })
    return results
