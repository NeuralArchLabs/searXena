from selectolax.parser import HTMLParser
from urllib.parse import urlencode

CATEGORIES = ["general"]
WEIGHT = 1.0

def request(query, params):
    query_params = {
        "q": query,
        "p": params.get("pageno", 1) - 1
    }
    params["url"] = f"https://www.ecosia.org/search?{urlencode(query_params)}"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    for node in tree.css('div.result, section.mainline article'):
        title_node = node.css_first('h2 a')
        snippet_node = node.css_first('.result-snippet, .content')
        
        if title_node:
            results.append({
                "title": title_node.text().strip(),
                "url": title_node.attributes.get('href', ''),
                "content": snippet_node.text().strip() if snippet_node else "",
                "source": "ecosia"
            })
    return results
