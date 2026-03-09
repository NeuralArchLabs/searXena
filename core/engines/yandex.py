from selectolax.parser import HTMLParser
from urllib.parse import urlencode

CATEGORIES = ["general"]
WEIGHT = 1.0

def request(query, params):
    query_params = {
        "text": query
    }
    params["url"] = f"https://yandex.com/search/?{urlencode(query_params)}"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    for node in tree.css('li.serp-item'):
        title_node = node.css_first('h2 a')
        snippet_node = node.css_first('div.text-container')
        
        if title_node:
            results.append({
                "title": title_node.text().strip(),
                "url": title_node.attributes.get('href', ''),
                "content": snippet_node.text().strip() if snippet_node else "",
                "source": "yandex"
            })
    return results
