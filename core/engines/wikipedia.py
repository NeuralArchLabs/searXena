import httpx
import asyncio
from urllib.parse import urlencode

NAME = "wikipedia"
CATEGORIES = ['general', 'it_science']
WEIGHT = 3.0

async def request(query, params):
    params["url"] = "internal://wikipedia"

async def response(resp):
    results = []
    query = resp.search_params.get("query")
    lang = resp.search_params.get("language", "es")
    
    headers = {
        "User-Agent": "searXena/1.1 (https://github.com/martinezpalomera92/searXena) Bot/1.0"
    }

    langs = [lang]
    if lang != 'en':
        langs.append('en')
    
    async def fetch_wiki(l):
        # Aumentamos exsentences y quitamos exintro para intentar obtener más texto si el intro es corto
        q_params = {
            "action": "query", "format": "json", "prop": "extracts|info|pageimages",
            "exsentences": 10,  # Más oraciones
            "explaintext": True,
            "inprop": "url", "pithumbsize": 600, # Imagen más grande
            "generator": "search",
            "gsrsearch": query, "gsrlimit": 5
        }
        api_url = f"https://{l}.wikipedia.org/w/api.php?{urlencode(q_params)}"
        try:
            async with httpx.AsyncClient(timeout=5.0, follow_redirects=True) as client:
                r = await client.get(api_url, headers=headers)
                if r.status_code == 200:
                    return r.json(), l
        except: pass
        return None, l

    pending = [fetch_wiki(l) for l in langs]
    completed = await asyncio.gather(*pending)

    for data, l in completed:
        if not data: continue
        pages = data.get("query", {}).get("pages", {})
        for page_id, page in pages.items():
            title = page.get("title", "")
            extract = page.get("extract", "")
            
            if extract and len(extract) > 40:
                results.append({
                    "title": title,
                    "url": page.get("fullurl", f"https://{l}.wikipedia.org/wiki/{title.replace(' ','_')}"),
                    "content": extract,
                    "img_src": page.get("thumbnail", {}).get("source") if "thumbnail" in page else None,
                    "template": "infobox.html",
                    "source": "wikipedia"
                })
    return results
