from selectolax.parser import HTMLParser
from urllib.parse import urlencode

CATEGORIES = ["general"]

def request(query, params):
    pageno = params.get("pageno", 1)
    params["url"] = f"https://search.brave.com/search?{urlencode({'q': query, 'offset': (pageno-1)*20})}"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    # Brave usa clases de estilo 'result-title' y 'result-details'
    for node in tree.css('div.snippet, div.result'):
        title_node = node.css_first('a.title, a.result-link h2, .heading-sm')
        snippet_node = node.css_first('p.snippet-description, .result-content, .description')
        
        if title_node:
            url = title_node.attributes.get('href', '') or (node.css_first('a').attributes.get('href') if node.css_first('a') else '')
            if url and url.startswith('http') and not "brave.com" in url:
                results.append({
                    "title": title_node.text().strip(),
                    "url": url,
                    "content": snippet_node.text().strip() if snippet_node else "Información de Brave Search.",
                    "score": 1.2
                })
    return results
