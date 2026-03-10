import httpx
from urllib.parse import urlencode

CATEGORIES = ['general', 'it', 'science']

def request(query, params):
    # Wikidata para Infobox
    query_params = {
        "action": "wbsearchentities",
        "format": "json",
        "search": query,
        "language": "es",
        "limit": 1
    }
    params["url"] = f"https://www.wikidata.org/w/api.php?{urlencode(query_params)}"

def response(resp):
    results = []
    try:
        data = resp.json()
        search = data.get("search", [])
        if search:
            entity = search[0]
            # Si hemos encontrado una entidad, creamos un resultado "Infobox"
            results.append({
                "template": "infobox.html",
                "title": entity.get("label", ""),
                "url": f"https://www.wikidata.org/wiki/{entity.get('id')}",
                "content": entity.get("description", "Información enciclopédica encontrada en Wikidata."),
                "score": 5.0 # ¡Directo al top!
            })
    except Exception:
        pass
    
    return results
