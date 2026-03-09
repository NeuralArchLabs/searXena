from selectolax.parser import HTMLParser
from urllib.parse import urlencode

CATEGORIES = ["general"]
WEIGHT = 1.0

def request(query, params):
    query_params = {
        "q": query,
        "s": (params.get("pageno", 1) - 1) * 10
    }
    params["url"] = f"https://www.mojeek.com/search?{urlencode(query_params)}"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    for node in tree.css('ul.results-standard li'):
        title_node = node.css_first('a.t')
        snippet_node = node.css_first('p.s')
        
        if title_node:
            results.append({
                "title": title_node.text().strip(),
                "url": title_node.attributes.get('href', ''),
                "content": snippet_node.text().strip() if snippet_node else "",
                "source": "mojeek"
            })
    return results
