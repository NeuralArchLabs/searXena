from selectolax.parser import HTMLParser
from urllib.parse import urlencode, unquote

CATEGORIES = ["general", "news"]
WEIGHT = 1.8

def request(query, params):
    # DDG Lite - Versión sin JS muy robusta
    offset = (params.get("pageno", 1) - 1) * 30
    params["url"] = f"https://duckduckgo.com/lite/?q={query}&s={offset}"
    params["headers"]["Accept"] = "text/html"

def response(resp):
    results = []
    tree = HTMLParser(resp.text)
    
    # En DDG Lite, los resultados están en una tabla de clase 'result-snippets'? No, tabla plana.
    # El patrón común es un subconjunto de filas por resultado.
    
    current_result = {}
    
    for row in tree.css('tr'):
        # Buscar el enlace del título
        title_link = row.css_first('a.result-link')
        if title_link:
            # Si ya teníamos uno a medias, lo guardamos (aunque DDG suele ser consistente)
            if current_result and current_result.get('title'):
                results.append(current_result)
                current_result = {}
            
            url = title_link.attributes.get('href', '')
            if url.startswith('//duckduckgo.com/l/?uddg='):
                url = unquote(url.split('uddg=')[1].split('&')[0])
            
            current_result = {
                "title": title_link.text().strip(),
                "url": url,
                "content": "",
                "source": "duckduckgo"
            }
            continue
            
        # Buscar el snippet en la siguiente fila
        snippet_td = row.css_first('td.result-snippet')
        if snippet_td and current_result:
            current_result["content"] = snippet_td.text().strip()
            # Una vez tenemos el snippet, ya podemos dar por cerrado este resultado
            results.append(current_result)
            current_result = {}
            
    # Último si quedó pendiente
    if current_result and current_result.get('title'):
        results.append(current_result)
            
    return results
