from selectolax.parser import HTMLParser
from urllib.parse import urlencode

def request(query, params):
    # Qwant Lite es más estable para scraping sin API key
    query_params = {
        "q": query,
        "locale": "en_US",
        "p": params.get("pageno", 1)
    }
    params["url"] = f"https://lite.qwant.com/?{urlencode(query_params)}"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    for node in tree.css('article'):
        title_node = node.css_first('h2 a')
        url_node = node.css_first('span.url')
        snippet_node = node.css_first('p')
        
        if title_node:
            results.append({
                "title": title_node.text().strip(),
                "url": title_node.attributes.get('href', ''),
                "content": snippet_node.text().strip() if snippet_node else ""
            })
    return results
