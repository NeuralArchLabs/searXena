from selectolax.parser import HTMLParser
from urllib.parse import urlencode

CATEGORIES = ["news"]
WEIGHT = 1.0

def request(query, params):
    params["url"] = f"https://www.reuters.com/site-search/?query={query}"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    for node in tree.css('li.search-results__item__2syuX'):
        title_node = node.css_first('h3 a')
        if title_node:
            results.append({
                "title": title_node.text().strip(),
                "url": "https://www.reuters.com" + title_node.attributes.get('href', ''),
                "content": "Noticia global en Reuters.",
                "source": "reuters"
            })
    return results
