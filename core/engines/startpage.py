from selectolax.parser import HTMLParser
from urllib.parse import urlencode

CATEGORIES = ["general"]
WEIGHT = 3.0

def request(query, params):
    # Startpage (Proxied Google results)
    query_params = {
        "query": query,
        "cat": "web",
        "t": "device",
        "lui": "english"
    }
    params["url"] = f"https://www.startpage.com/sp/search?{urlencode(query_params)}"
    params["headers"]["Referer"] = "https://www.startpage.com/"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    # Robust selectors for Startpage
    for node in tree.css('div.result, .result, article.result'):
        title_link = node.css_first('a.result-link, a.result-title, h2 a')
        snippet_node = node.css_first('p.description, .result-snippet, .description')
        
        if title_link:
            url = title_link.attributes.get('href', '')
            if url.startswith('http') and not "startpage.com" in url:
                results.append({
                    "title": title_link.text().strip(),
                    "url": url,
                    "content": snippet_node.text().strip() if snippet_node else "",
                    "source": "startpage"
                })
    return results
