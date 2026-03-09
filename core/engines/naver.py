from selectolax.parser import HTMLParser
from urllib.parse import urlencode

CATEGORIES = ["general"]
WEIGHT = 1.0

def request(query, params):
    query_params = {
        "query": query,
        "where": "web"
    }
    params["url"] = f"https://search.naver.com/search.naver?{urlencode(query_params)}"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    for node in tree.css('li.bx'):
        title_node = node.css_first('a.link_tit')
        snippet_node = node.css_first('div.dsc_area, p.dsc')
        
        if title_node:
            results.append({
                "title": title_node.text().strip(),
                "url": title_node.attributes.get('href', ''),
                "content": snippet_node.text().strip() if snippet_node else "Naver result.",
                "source": "naver"
            })
    return results
