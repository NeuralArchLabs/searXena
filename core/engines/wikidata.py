import httpx
import asyncio
import hashlib
from urllib.parse import urlencode

NAME = "wikidata"
CATEGORIES = ['general', 'it_science']
WEIGHT = 1.0

async def request(query, params):
    params["url"] = "internal://wikidata"

def get_commons_url(filename):
    """Genera una URL directa de thumbnail para un archivo de Wikimedia Commons"""
    if not filename: return None
    name = filename.replace(' ', '_')
    m = hashlib.md5()
    m.update(name.encode('utf-8'))
    h = m.hexdigest()
    # Estructura de Commons: /a/ab/Filename
    return f"https://upload.wikimedia.org/wikipedia/commons/thumb/{h[0]}/{h[0:2]}/{name}/400px-{name}"

async def response(resp):
    results = []
    query = resp.search_params.get("query")
    lang = resp.search_params.get("language", "es")
    headers = {"User-Agent": "searXena/1.1 (https://github.com/martinezpalomera92/searXena)"}

    search_params = {
        "action": "wbsearchentities",
        "format": "json",
        "search": query,
        "language": lang,
        "limit": 1
    }
    
    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            r = await client.get(f"https://www.wikidata.org/w/api.php?{urlencode(search_params)}", headers=headers)
            search_data = r.json()
            search_results = search_data.get("search", [])
            
            if not search_results:
                return []
            
            entity_id = search_results[0].get("id")
            label = search_results[0].get("label", "")
            description = search_results[0].get("description", "")

            detail_params = {
                "action": "wbgetentities",
                "format": "json",
                "ids": entity_id,
                "props": "claims|labels|descriptions",
                "languages": lang
            }
            r_detail = await client.get(f"https://www.wikidata.org/w/api.php?{urlencode(detail_params)}", headers=headers)
            detail_data = r_detail.json()
            entity_info = detail_data.get("entities", {}).get(entity_id, {})
            
            claims = entity_info.get("claims", {})
            img_src = None
            
            # Intentar obtener imagen de P18
            if "P18" in claims:
                img_name = claims["P18"][0].get("mainsnak", {}).get("datavalue", {}).get("value")
                if img_name:
                    img_src = get_commons_url(img_name)

            results.append({
                "template": "infobox.html",
                "title": label,
                "url": f"https://www.wikidata.org/wiki/{entity_id}",
                "content": description if description else "Información de Wikidata.",
                "img_src": img_src,
                "source": "wikidata",
                "lang": lang,
                "score": 4.0
            })
            
    except Exception as e:
        print(f"DEBUG Wikidata Error: {e}")
        
    return results
