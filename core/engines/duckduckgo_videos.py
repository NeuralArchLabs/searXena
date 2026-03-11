import httpx
from utils import fetch_vqd
from urllib.parse import urlencode

CATEGORIES = ["videos"]
WEIGHT = 1.3

async def request(query, params):
    client = params['client']
    vqd = await fetch_vqd(query, client)
        
    if not vqd: return

    query_params = {
        "l": "wt-wt",
        "o": "json",
        "q": query,
        "vqd": vqd,
        "f": ",,,",
        "p": 1
    }
    params["url"] = f"https://duckduckgo.com/v.js?{urlencode(query_params)}"

def response(resp):
    results = []
    try:
        data = resp.json()
        for item in data.get("results", []):
            results.append({
                "template": "videos.html",
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "img_src": item.get("image", ""),
                "thumbnail_src": item.get("thumbnail", ""),
                "content": f"{item.get('provider', '')} • {item.get('duration', '')}",
                "iframe_src": f"https://www.youtube-nocookie.com/embed/{item.get('id')}" if 'youtube' in item.get('url', '') else None,
                "source": "duckduckgo"
            })
    except Exception:
        pass
    return results
