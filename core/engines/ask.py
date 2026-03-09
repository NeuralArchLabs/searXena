from selectolax.parser import HTMLParser
from urllib.parse import urlencode

CATEGORIES = ["general"]
WEIGHT = 1.0

def request(query, params):
    query_params = {
        "q": query,
        "page": params.get("pageno", 1)
    }
    params["url"] = f"https://www.ask.com/web?{urlencode(query_params)}"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    for node in tree.css('div.PartialSearchResults-item'):
        title_node = node.css_first('a.PartialSearchResults-item-title-link')
        snippet_node = node.css_first('p.PartialSearchResults-item-abstract')
        
        if title_node:
            results.append({
                "title": title_node.text().strip(),
                "url": title_node.attributes.get('href', ''),
                "content": snippet_node.text().strip() if snippet_node else "",
                "source": "ask"
            })
    return results
