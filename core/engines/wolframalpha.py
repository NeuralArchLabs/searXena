from selectolax.parser import HTMLParser
from urllib.parse import urlencode

CATEGORIES = ["general", "it"]
WEIGHT = 3.0

# WolframAlpha sin API (Scraper de modo mini)
# Nota: WolframAlpha es muy estricto con los User-Agents.
def request(query, params):
    params["url"] = f"https://www.wolframalpha.com/input/?{urlencode({'i': query})}"
    params["headers"]["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    # WolframAlpha suele cargar datos via JS despues, 
    # pero a veces deja pre-renderizados en el HTML (especialmente definiciones)
    for node in tree.css('section[class*="Pod"]'):
        title_node = node.css_first('h2')
        content_node = node.css_first('img')
        
        if title_node:
            results.append({
                "template": "infobox.html",
                "title": f"Wolfram|Alpha: {title_node.text().strip()}",
                "url": resp.url,
                "content": content_node.attributes.get('alt', 'Consultando WolframAlpha...') if content_node else "Información técnica.",
                "source": "wolframalpha"
            })
            
    return results
