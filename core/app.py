from fastapi import FastAPI, Request, Form, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, RedirectResponse
import uvicorn
import os
import json
from engine_manager import EngineManager
import engines.suggestions as suggestions

from urllib.parse import quote_plus, urlparse
import re

app = FastAPI(title="searXena")

# Configuración de base
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Register filters
templates.env.filters["urlencode"] = lambda s: quote_plus(str(s)) if s else ""

# Inicializar EngineManager con persistencia
manager = EngineManager(BASE_DIR)

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/autoc")
async def autocomplete(q: str = ""):
    results = await suggestions.get_suggestions(q)
    return JSONResponse(results)

@app.get("/settings")
async def get_settings(request: Request):
    engine_list = []
    for name, module in manager.engines.items():
        engine_list.append({
            "name": name,
            "enabled": module.ENABLED,
            "categories": module.CATEGORIES,
            "weight": module.WEIGHT
        })
    return templates.TemplateResponse("settings.html", {"request": request, "engines": engine_list})

@app.post("/save_settings")
async def save_settings(request: Request):
    form = await request.form()
    enabled_engines = form.getlist("engines")
    
    current = manager.settings
    # Guardar motores
    for engine_cfg in current["engines"]:
        engine_cfg["enabled"] = engine_cfg["name"] in enabled_engines
    
    # Guardar preferencias generales
    general = current.get("general", {})
    general["safe_search"] = int(form.get("safesearch", 0))
    general["default_lang"] = form.get("language", "es")
    general["autocomplete"] = form.get("autocomplete", "google")
    current["general"] = general

    manager.save_settings(current)
    manager.load_engines() 
    
    return RedirectResponse(url="/settings", status_code=303)

import httpx
from fastapi.responses import StreamingResponse

@app.get("/proxify")
async def proxify(url: str):
    """Proxy local para imágenes y recursos externos para proteger la IP del usuario."""
    if not url: return Response(status_code=400)
    
    # Intentar limpiar URLs de Google que a veces vienen mal
    if "google.com/url?q=" in url:
        from urllib.parse import unquote
        url = unquote(url.split("?q=")[1].split("&")[0])
        
    # Arreglar URLs relativas de Wikipedia
    if url.startswith("//"):
        url = "https:" + url

    async def stream_resource():
        async with httpx.AsyncClient(verify=False, timeout=15.0, follow_redirects=True) as client:
            try:
                async with client.stream("GET", url) as resp:
                    if resp.status_code == 200:
                        async for chunk in resp.aiter_bytes():
                            yield chunk
                    else:
                        # Fallback simple
                        pass
            except Exception:
                pass

    return StreamingResponse(stream_resource(), media_type="image/png")

# Meta-búsqueda orquestada con paginación
@app.get("/search")
@app.post("/search")
async def search(request: Request):
    q = request.query_params.get("q")
    category = request.query_params.get("category", "general")
    pageno = int(request.query_params.get("pageno", 1))
    
    if request.method == "POST":
        form = await request.form()
        q = q or form.get("q")
        category = category or form.get("category", "general")
        pageno = int(form.get("pageno", 1))

    if not q:
        return RedirectResponse(url="/")

    # Sistema de Bangs (SearXNG style)
    if q.startswith("!"):
        parts = q.split(" ", 1)
        bang = parts[0].lower()
        if bang in manager.bangs:
            target = manager.bangs[bang]
            q = parts[1] if len(parts) > 1 else ""
            if target in ["images", "videos", "news", "it", "shopping"]:
                category = target

    results, infoboxes = [], []
    
    if category == "shopping":
        # Modificar la query internamente para forzar a los motores generales a arrojar resultados comerciales
        search_q = q if any(w in q.lower() for w in ["comprar", "precio", "oferta", "tienda"]) else f"{q} comprar"
        
        # Petición única y normal, sin paginaciones dobles raras.
        results, infoboxes = await manager.search(search_q, category=category, pageno=pageno)
    else:
        results, infoboxes = await manager.search(q, category=category, pageno=pageno)
    
    # Filtrado y reorganización inteligente para compras
    reorganized = []
    
    # Dominios súper comunes para asegurar que entren aunque no tengan precio explícito en el snippet
    shopping_domains = ["amazon.", "ebay.", "mercadolibre.", "aliexpress.", "walmart.", "target.", "bestbuy.", "etsy.", "shopee.", "liverpool.", "coppel.", "steren.", "homedepot.", "cyberpuerta."]
    
    for r in results:
        # 1. Intentar extraer precio del snippet (Regex)
        if "price" not in r:
            match = re.search(r'([\$€£]\s?\d+[\.,]\d{2,3})', r.get("content", ""))
            if match:
                r["price"] = match.group(1)
                
        has_price = bool(r.get("price"))
        
        url = r.get("url", "")
        domain = urlparse(url).netloc.lower()
        is_shop_domain = any(sd in domain for sd in shopping_domains)
        
        # 2. Es producto si tiene precio, o si viene de una tienda conocida
        is_shop = has_price or is_shop_domain
        
        if is_shop:
            r["template"] = "shopping.html"
            if "shopping_store" not in r:
                r["shopping_store"] = domain.replace("www.", "").split(".")[0]
            if r.get("thumbnail_src") and not r.get("img_src"):
                r["img_src"] = r["thumbnail_src"]
        
        # 3. Filtrar
        if category == "shopping":
            if is_shop:
                reorganized.append(r)
        else:
            reorganized.append(r)
            
    if category == "shopping":
        results = reorganized
    
    # Solo mostrar infoboxes (respuestas destacadas) en la categoría GENERAL
    if category == "general":
        full_results = infoboxes + results
    else:
        full_results = results

    response = templates.TemplateResponse("results.html", {
        "request": request, 
        "query": q, 
        "results": full_results,
        "category": category,
        "pageno": pageno
    })
    
    # Cabeceras de Privacidad Estrictas
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    return response

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
