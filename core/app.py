from fastapi import FastAPI, Request, Form, Response, Query, Body
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Any
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
    lang = manager.settings.get("general", {}).get("default_lang", "es")
    return templates.TemplateResponse("index.html", {"request": request, "lang": lang})

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
    general_settings = manager.settings.get("general", {})
    return templates.TemplateResponse("settings.html", {
        "request": request, 
        "engines": engine_list,
        "general": general_settings,
        "lang": manager.settings.get("general", {}).get("default_lang", "es")
    })

@app.post("/save_settings")
async def save_settings(request: Request):
    form = await request.form()
    enabled_engines = form.getlist("engines")
    
    current = manager.settings
    if "engines" not in current:
        current["engines"] = []
        
    # Guardar motores de forma segura y evitar conflictos de categorías
    for name, module in manager.engines.items():
        found = False
        for cfg in current["engines"]:
            if cfg.get("name") == name:
                cfg["enabled"] = name in enabled_engines
                # Eliminar las categorías cacheadas en JSON si existen, para que siempre lea del .py
                if "categories" in cfg:
                    del cfg["categories"]
                found = True
                break
        if not found:
            current["engines"].append({
                "name": name,
                "enabled": name in enabled_engines
            })
    
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

    headers = {
        "Cache-Control": "public, max-age=604800" # Cachear localmente por una semana
    }
    return StreamingResponse(stream_resource(), media_type="image/png", headers=headers)

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
    if category == "it_science":
        category = "it"
        
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
    
    # Los infoboxes (como OSM) son esenciales en General y Mapas
    if category in ["general", "maps"]:
        full_results = infoboxes + results
    else:
        full_results = results

    response = templates.TemplateResponse("results.html", {
        "request": request, 
        "query": q, 
        "results": full_results,
        "category": category,
        "pageno": pageno,
        "lang": manager.settings.get("general", {}).get("default_lang", "es")
    })
    
    # Cabeceras de Privacidad Estrictas
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    return response

# --- API endpoints para IA / LLMs ---

class ToolSearchRequest(BaseModel):
    query: str = Field(..., description="Query string for search")
    category: str = Field("general", description="Category of search: general, images, videos, news, it, shopping")
    pageno: int = Field(1, description="Page number/offset for the search results")
    include_engines: Optional[List[str]] = Field(None, description="List of specific engine names to use (e.g. ['google', 'github']). Ignored if empty.")
    exclude_engines: Optional[List[str]] = Field(None, description="List of specific engine names to exclude. Ignored if empty.")
    limit: int = Field(10, description="Cantidad máxima de resultados a retornar (default 10 para ahorrar contexto).")

@app.post("/api/v1/search")
async def api_search(request_data: ToolSearchRequest):
    """
    Endpoint nativo en JSON estructurado para Agentes de IA
    """
    results, infoboxes = await manager.search(
        request_data.query,
        category=request_data.category,
        pageno=request_data.pageno,
        include_engines=request_data.include_engines,
        exclude_engines=request_data.exclude_engines
    )
    
    # Limpiamos resultados para IA
    keys_to_remove = ["template", "engine_positions", "score", "sources"]
    
    clean_results = []
    # Convertimos los results de dicts, omitiendo las llaves para front end
    for r in infoboxes + results:
        clean_r = {k: v for k, v in r.items() if k not in keys_to_remove}
        clean_results.append(clean_r)
        
    total = len(clean_results)
    limited = clean_results[:request_data.limit]
    
    return {
        "results": limited,
        "meta": {
            "total_found": total,
            "limit_applied": request_data.limit,
            "has_more": total > request_data.limit,
            "suggestion": f"Hay {total} resultados en total guardados en cache. Estas viendo solo los primeros {request_data.limit}. Para ver el resto, repite esta misma llamada a la herramienta pero cambia el parametro 'limit' a {total} o superior." if total > request_data.limit else None
        }
    }

@app.get("/api/v1/tools_schema")
async def api_tools_schema():
    """
    Devuelve el esquema nativo listando la herramienta general del buscador 
    para ser mapeada directamente en APIs de LLMs modernos (OpenAI, Anthropic, Gemini, etc.)
    """
    engines_list = [name for name, _ in manager.engines.items()]
    return {
      "type": "function",
      "function": {
        "name": "searxena_search",
        "description": "Realiza una meta-búsqueda en la web. Útil para obtener información general, código, noticias, o buscar bibliotecas de IT y productos.",
        "parameters": {
          "type": "object",
          "properties": {
            "query": {
              "type": "string",
              "description": "El término de búsqueda"
            },
            "category": {
              "type": "string",
              "enum": ["general", "it", "shopping", "news", "images", "videos"],
              "description": "El canal de búsqueda a utilizar según la intención. General es el default."
            },
            "pageno": {
              "type": "integer",
              "description": "Número de página de resultados (1 por defecto)."
            },
            "include_engines": {
              "type": "array",
              "items": {"type": "string", "enum": engines_list},
              "description": "Opcional. Exige el uso exclusivo de este arreglo de motores."
            },
            "exclude_engines": {
              "type": "array",
              "items": {"type": "string", "enum": engines_list},
              "description": "Opcional. Motores específicos a excluir de los resultados."
            },
            "limit": {
              "type": "integer",
              "description": "Cantidad máxima de resultados para ahorrar contexto (default 10)."
            }
          },
          "required": ["query"]
        }
      }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
