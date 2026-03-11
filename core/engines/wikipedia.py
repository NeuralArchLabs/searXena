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
        "User-Agent": "searXena/1.2 (https://github.com/martinezpalomera92/searXena) Bot/1.0"
    }

    langs = [lang]
    if lang != 'en':
        langs.append('en')
    
    async def fetch_wiki(l):
        q_params = {
            "action": "query", "format": "json", 
            "prop": "extracts|info|pageimages|images|pageprops",
            "explaintext": True, 
            "exchars": 1200, 
            "inprop": "url", "pithumbsize": 800, 
            "generator": "search", "gsrsearch": query, "gsrlimit": 5
        }
        api_url = f"https://{l}.wikipedia.org/w/api.php?{urlencode(q_params)}"
        try:
            async with httpx.AsyncClient(timeout=6.0, follow_redirects=True) as client:
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
            
            # 1. Intentar imagen principal de la API
            img_src = page.get("thumbnail", {}).get("source")
            
            # 2. Intentar page_image de pageprops
            if not img_src:
                pp = page.get("pageprops", {})
                img_name = pp.get("page_image_free") or pp.get("page_image")
                if img_name:
                     img_src = f"https://commons.wikimedia.org/wiki/Special:FilePath/{img_name.replace(' ', '_')}?width=800"

            # 3. Fallback agresivo a la lista de imágenes
            if not img_src and "images" in page:
                for img in page["images"]:
                    img_title = img.get("title", "")
                    img_lower = img_title.lower()
                    
                    if not any(ext in img_lower for ext in ['.jpg', '.jpeg', '.png', '.webp', '.svg']):
                        continue
                        
                    forbidden = [
                        "symbol", "question", "edit-clear", "ambox", "magnifying", "folder", "padlock",
                        "speaker", "decrease", "increase", "sound", "placeholder",
                        "stub", "generic", "map", "flag", "translation", "language", "p_ext"
                    ]
                    if any(f in img_lower for f in forbidden):
                        continue
                    
                    clean_name = img_title.replace("Archivo:", "").replace("File:", "").replace(" ", "_").strip()
                    img_src = f"https://commons.wikimedia.org/wiki/Special:FilePath/{clean_name}?width=800"
                    
                    # Si el nombre de la imagen tiene el título o la palabra logo, es casi seguro la correcta
                    clean_query = query.lower().replace(" ", "")
                    it_clean = img_lower.replace("_","").replace("-","")
                    if clean_query in it_clean or "logo" in it_clean or "brand" in it_clean:
                        break

            if extract and len(extract) > 40:
                results.append({
                    "title": title,
                    "url": page.get("fullurl", f"https://{l}.wikipedia.org/wiki/{title.replace(' ','_')}"),
                    "content": extract,
                    "img_src": img_src,
                    "template": "infobox.html",
                    "source": "wikipedia"
                })
    return results
