from selectolax.parser import HTMLParser
from urllib.parse import urlencode

CATEGORIES = ["it"]

def request(query, params):
    params["url"] = f"https://pypi.org/search/?q={urlencode({'q': query})}"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    for node in tree.css('li a.package-snippet'):
        title_node = node.css_first('span.package-snippet__name')
        version_node = node.css_first('span.package-snippet__version')
        desc_node = node.css_first('p.package-snippet__description')
        
        if title_node:
            results.append({
                "title": f"PyPI: {title_node.text().strip()} ({version_node.text().strip() if version_node else ''})",
                "url": "https://pypi.org" + node.attributes.get('href', ''),
                "content": desc_node.text().strip() if desc_node else "Python package.",
                "score": 1.2
            })
    return results
