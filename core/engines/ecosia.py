from selectolax.parser import HTMLParser
from urllib.parse import urlencode

def request(query, params):
    params["url"] = f"https://www.ecosia.org/search?q={urlencode({'q': query})}"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    for node in tree.css('div.mainline-results div.result, div.card-web'):
        title_node = node.css_first('a.result-title, h2 a')
        snippet_node = node.css_first('p.result-snippet, div.content')
        
        if title_node:
            results.append({
                "title": title_node.text().strip(),
                "url": title_node.attributes.get('href', ''),
                "content": snippet_node.text().strip() if snippet_node else ""
            })
    return results
