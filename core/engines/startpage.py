from selectolax.parser import HTMLParser

CATEGORIES = ["general"]
WEIGHT = 3.0

def request(query, params):
    # Startpage (Proxied Google results)
    params["url"] = f"https://www.startpage.com/sp/search?query={query}"
    params["headers"]["Accept"] = "text/html"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    # Selector probado en debug: div.w-gl__result
    for node in tree.css('div.w-gl__result'):
        title_link = node.css_first('a.w-gl__result-title')
        snippet_node = node.css_first('p.w-gl__description')
        
        if title_link:
            results.append({
                "title": title_link.text().strip(),
                "url": title_link.attributes.get('href', ''),
                "content": snippet_node.text().strip() if snippet_node else "",
                "source": "startpage"
            })
    return results
