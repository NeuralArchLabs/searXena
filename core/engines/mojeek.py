from selectolax.parser import HTMLParser
from urllib.parse import urlencode

CATEGORIES = ["general"]
WEIGHT = 1.2

def request(query, params):
    query_params = {
        "q": query,
        "s": (params.get("pageno", 1) - 1) * 10
    }
    params["url"] = f"https://www.mojeek.com/search?{urlencode(query_params)}"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    # Mojeek uses ul.results-standard or div.results
    for node in tree.css('ul.results-standard li, div.results article, .results li, article'):
        title_node = node.css_first('a.title, a.t, h2 a, h3 a')
        snippet_node = node.css_first('p.s, .snippet, .description, .s')
        
        if title_node:
            url = title_node.attributes.get('href', '')
            if url.startswith('http'):
                results.append({
                    "title": title_node.text().strip(),
                    "url": url,
                    "content": snippet_node.text().strip() if snippet_node else "",
                    "source": "mojeek"
                })
    return results
