from selectolax.parser import HTMLParser
from urllib.parse import urlencode

CATEGORIES = ["general"]
WEIGHT = 1.0

def request(query, params):
    query_params = {
        "q": query,
        "check_keywords": "yes",
        "area": "default"
    }
    params["url"] = f"https://docs.python.org/3/search.html?{urlencode(query_params)}"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    # Sphinx search results are often loaded via JS, but we can try to find static ones 
    # or fallback to a simple description.
    for node in tree.css('ul.search li'):
        link = node.css_first('a')
        if link:
            results.append({
                "title": f"Python Doc: {link.text().strip()}",
                "url": "https://docs.python.org/3/" + link.attributes.get('href', ''),
                "content": "Documentación oficial de Python.",
                "source": "pydoc"
            })
    return results
