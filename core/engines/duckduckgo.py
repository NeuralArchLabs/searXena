from selectolax.parser import HTMLParser
import json

CATEGORIES = ["general", "news"]

def request(query, params):
    # La versión HTML es lenta y limitada a 10 resultados.
    # Usamos el endpoint JS que devuelve datos más ricos, simulando el motor de SearXNG.
    pageno = params.get("pageno", 1)
    
    # Parámetros para forzar más resultados por página
    # DuckDuckGo no permite 'num=20' pero permite offset manual
    params["url"] = f"https://duckduckgo.com/html/?q={query}&s={(pageno-1)*30}&dc={(pageno-1)*30}&v=l&o=json"
    params["headers"]["Referer"] = "https://duckduckgo.com/"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    # DuckDuckGo HTML tiene selectores simples pero robustos
    for node in tree.css('div.result'):
        if 'result--ad' in (node.attributes.get('class') or ''):
            continue
            
        title_node = node.css_first('a.result__a')
        snippet_node = node.css_first('a.result__snippet')
        
        if title_node:
            results.append({
                "title": title_node.text().strip(),
                "url": title_node.attributes.get('href', ''),
                "content": snippet_node.text().strip() if snippet_node else "",
                "score": 1.0 # Base DuckDuckGo
            })
            
    return results
