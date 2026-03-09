from selectolax.parser import HTMLParser
from urllib.parse import urlencode

CATEGORIES = ["social", "general"]
WEIGHT = 1.0

def request(query, params):
    params["url"] = f"https://stackoverflow.com/search?{urlencode({'q': query})}"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    for node in tree.css('div.s-post-summary'):
        title_node = node.css_first('h3 a')
        snippet_node = node.css_first('div.s-post-summary--content-excerpt')
        
        if title_node:
            results.append({
                "title": title_node.text().strip(),
                "url": "https://stackoverflow.com" + title_node.attributes.get('href', ''),
                "content": snippet_node.text().strip() if snippet_node else "Pregunta en StackOverflow.",
                "source": "stackoverflow"
            })
    return results
