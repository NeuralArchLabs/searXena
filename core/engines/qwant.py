import json
from urllib.parse import urlencode

CATEGORIES = ["general", "images", "videos", "news"]
WEIGHT = 1.0

# Qwant utiliza un API JSON para todos sus resultados (muy confiable)
API_URL = "https://api.qwant.com/v3/search/{type}?"

def request(query, params):
    category = params.get("category", "general")
    pageno = params.get("pageno", 1)
    
    # Mapear categorias Qwant
    q_type = "web"
    if category == "images": q_type = "images"
    elif category == "videos": q_type = "videos"
    elif category == "news": q_type = "news"
    
    query_params = {
        "q": query,
        "count": 10,
        "offset": (pageno - 1) * 10,
        # "t": q_type, # Ya lo pasamos en el API_URL
        "uiv": 4,
        "locale": "es_ES" 
    }
    
    if params.get("safesearch"):
        query_params["safesearch"] = params["safesearch"]
        
    params["url"] = API_URL.format(type=q_type) + urlencode(query_params)
    params["headers"]["X-Requested-With"] = "XMLHttpRequest"
    params["headers"]["Referer"] = "https://www.qwant.com/"

def response(resp):
    results = []
    try:
        data = resp.json()
        if data.get("status") != "success":
            return []
            
        items = data.get("data", {}).get("result", {}).get("items", [])
        
        for item in items:
            res = {
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "content": item.get("desc", ""),
                "source": "qwant"
            }
            
            # Formatos especificos
            if "media" in item:
                res["template"] = "images.html"
                res["img_src"] = item.get("media")
                res["thumbnail_src"] = item.get("thumbnail")
            elif "thumbnail" in item:
                if "/videos/" in resp.url or "videos" in resp.search_params.get("category", ""):
                    res["template"] = "videos.html"
                res["img_src"] = item.get("thumbnail")
                
            results.append(res)
    except Exception:
        pass
        
    return results
