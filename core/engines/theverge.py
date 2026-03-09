from selectolax.parser import HTMLParser
from urllib.parse import urlencode

CATEGORIES = ["news"]
WEIGHT = 1.0

def request(query, params):
    params["url"] = f"https://www.theverge.com/search?q={query}"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    for node in tree.css('div.c-compact-river__entry'):
        title_node = node.css_first('h2 a')
        if title_node:
            results.append({
                "title": title_node.text().strip(),
                "url": title_node.attributes.get('href', ''),
                "content": "Noticia en The Verge.",
                "source": "theverge"
            })
    return results
