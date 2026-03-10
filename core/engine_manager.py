import importlib
import os
import sys
import asyncio
import httpx
import json
import time
from typing import List, Dict, Any, Set
from collections import defaultdict

from utils import gen_useragent

class EngineManager:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.settings_path = os.path.join(base_dir, "settings.json")
        self.engines_dir = os.path.join(base_dir, "engines")
        self.settings = self.load_settings()
        self.engines = {}
        self._cache = {} 
        self.load_engines()

        # Bangs map (SearXNG style)
        self.bangs = {
            "!g": "google", "!w": "wikipedia", "!yt": "youtube", 
            "!gh": "github", "!so": "stackoverflow", "!i": "images",
            "!n": "news", "!ddg": "duckduckgo", "!bi": "bing",
            "!red": "reddit", "!py": "pypi", "!npm": "npm",
            "!qw": "qwant", "!wa": "wolframalpha", "!v": "videos",
            "!sc": "swisscows", "!ec": "ecosia", "!mo": "mojeek",
            "!sp": "startpage", "!ya": "yahoo", "!ak": "ask",
            "!ba": "baidu", "!na": "naver", "!se": "seznam",
            "!gb": "gigablast", "!ar": "arxiv", "!md": "mdn",
            "!pd": "pydoc", "!gl": "gitlab", "!sf": "sourceforge",
            "!do": "docker", "!eb": "ebay", "!wh": "wallhaven",
            "!ls": "librestock", "!fl": "flickr", "!gp": "giphy",
            "!pi": "pinterest", "!un": "unsplash"
        }

        # Ad-block global list (SearXNG style)
        self.ad_patterns = [
            "googleads", "pagead", "doubleclick", "partner.googleadservices",
            "adservice", "sponsored", "ads-", "ad-content", "amazon-ad", 
            "bingads", "yandex.ru/ads", "facebook.com/ads", "taboola", 
            "outbrain", "aclk?", "gampad/"
        ]
        
        # User-Agent rotation list (if needed globally)
        self.ua_list = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ]

    def load_settings(self):
        try:
            if not os.path.exists(self.settings_path):
                return self.get_default_settings()
            with open(self.settings_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return self.get_default_settings()

    def get_default_settings(self):
        return {
            "general": {"timeout": 4.0, "cache_ttl": 600, "instance_name": "searXena"},
            "engines": []
        }

    def save_settings(self, new_settings):
        try:
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                json.dump(new_settings, f, indent=4)
            self.settings = new_settings
        except Exception:
            pass

    def load_engines(self):
        if self.base_dir not in sys.path:
            sys.path.insert(0, self.base_dir)
            
        config_engines = {e["name"]: e for e in self.settings.get("engines", [])}

        for filename in os.listdir(self.engines_dir):
            if filename.endswith(".py") and not filename.startswith("__") and filename != "suggestions.py":
                engine_name = filename[:-3]
                try:
                    if f"engines.{engine_name}" in sys.modules:
                        importlib.reload(sys.modules[f"engines.{engine_name}"])
                    module = importlib.import_module(f"engines.{engine_name}")
                    
                    # Module defaults
                    default_enabled = getattr(module, "ENABLED", True)
                    default_categories = getattr(module, "CATEGORIES", ["general"])
                    default_weight = getattr(module, "WEIGHT", 1.0)

                    cfg = config_engines.get(engine_name, {})
                    module.ENABLED = cfg.get("enabled", default_enabled)
                    module.CATEGORIES = cfg.get("categories", default_categories)
                    module.WEIGHT = cfg.get("weight", default_weight)
                    module.NAME = engine_name
                    
                    if hasattr(module, "request") and hasattr(module, "response"):
                        self.engines[engine_name] = module
                except Exception:
                    pass

    async def search(self, query: str, category: str = "general", pageno: int = 1):
        # 1. Handle Bangs
        target_engine = None
        clean_query = query
        for bang, engine_name in self.bangs.items():
            if query.startswith(bang + " "):
                target_engine = engine_name
                clean_query = query[len(bang)+1:]
                break
            elif query.endswith(" " + bang):
                target_engine = engine_name
                clean_query = query[:-len(bang)-1]
                break

        # 2. Check Cache
        cache_key = f"{clean_query}:{category}:{pageno}:{target_engine}"
        now = time.time()
        if cache_key in self._cache:
            results, expiry = self._cache[cache_key]
            if now < expiry:
                return results

        # 3. Parallel Search - Mejor selección de motores (Estilo SearXNG)
        tasks = []
        timeout_limit = self.settings["general"].get("timeout", 4.0)
        
        # Filtro de motores por categoría (Mejorado)
        category_engines = []
        for name, engine in self.engines.items():
            if engine.ENABLED and category in engine.CATEGORIES:
                category_engines.append(engine)
        
        # Si no hay motores en la categoría, buscar en general (Fallback)
        if not category_engines:
            for name, engine in self.engines.items():
                if engine.ENABLED and "general" in engine.CATEGORIES:
                    category_engines.append(engine)
                    
        # PRIORIZACIÓN (SearXNG): 
        # No corremos todos los motores a la vez si son masivos, 
        # ordenamos por PESO y tomamos los mejores para evitar latencias extremas.
        category_engines.sort(key=lambda x: x.WEIGHT, reverse=True)
        # Pool ampliado (SearXNG suele correr 20+ pero aquí mantendremos 15 por CPU)
        selection = category_engines[:15]
        
        if target_engine and target_engine in self.engines:
             tasks = [self.call_engine(self.engines[target_engine], clean_query, category, pageno, timeout_limit)]
        else:
            for engine in selection:
                tasks.append(self.call_engine(engine, clean_query, category, pageno, timeout_limit))

        # Parallel Wait (Buscamos que sean ultra-veloces)
        try:
            results_list = await asyncio.gather(*tasks, return_exceptions=True)
            valid_results = [r for r in results_list if isinstance(r, list)]
        except Exception:
            valid_results = []
        
        results, infoboxes = self.process_and_rank(valid_results)
        
        # Cache Result
        ttl = self.settings["general"].get("cache_ttl", 600)
        self._cache[cache_key] = ((results, infoboxes), now + ttl)
        
        return results, infoboxes

    async def call_engine(self, engine, query, category, pageno, timeout_limit):
        try:
            params = {
                "query": query,
                "pageno": pageno,
                "category": category,
                "safesearch": self.settings.get("general", {}).get("safe_search", 1),
                "language": self.settings.get("general", {}).get("default_lang", "es"),
                "time_range": None,
                "url": None,
                "method": "GET",
                "headers": {
                    "User-Agent": gen_useragent(),
                    "Accept-Language": f"{self.settings.get('general', {}).get('default_lang', 'es')},es;q=0.9,en;q=0.8",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                    "Connection": "keep-alive"
                },
                "data": {},
                "cookies": {},
                "timeout": timeout_limit,
                "engine_data": {}
            }
            
            # Ejecutar lógica del motor
            if hasattr(engine, "request_categorized"):
                if asyncio.iscoroutinefunction(engine.request_categorized):
                    await engine.request_categorized(query, category, params)
                else:
                    engine.request_categorized(query, category, params)
            else:
                if asyncio.iscoroutinefunction(engine.request):
                    await engine.request(query, params)
                else:
                    engine.request(query, params)
            
            results = []
            if params.get("url") and params["url"].startswith("internal://"):
                class FakeResponse:
                    def __init__(self, p):
                        self.text = ""
                        self.status_code = 200
                        self.search_params = p
                        self.url = p["url"]
                    def json(self): return {}
                results = engine.response(FakeResponse(params))
            elif params.get("url"):
                async with httpx.AsyncClient(
                    follow_redirects=True, 
                    timeout=params["timeout"],
                    limits=httpx.Limits(max_keepalive_connections=50, max_connections=200),
                    http2=True,
                    verify=False # Evitar errores SSL en entornos restringidos
                ) as client:
                    if params["method"] == "POST":
                        resp = await client.post(params["url"], data=params["data"], headers=params["headers"], cookies=params["cookies"])
                    else:
                        resp = await client.get(params["url"], headers=params["headers"], cookies=params["cookies"])
                    
                    engine_name = getattr(engine, "NAME", engine.__name__.split('.')[-2] if '.' in engine.__name__ else engine.__name__)
                    if engine_name in ["google", "bing", "duckduckgo"]:
                         print(f"DEBUG: {engine_name} status: {resp.status_code}")
                    
                    if resp.status_code in [200, 202]:
                        class ResponseWrapper:
                            def __init__(self, r, p):
                                self.text = r.text
                                self.status_code = r.status_code
                                self.search_params = p
                                self.url = str(r.url)
                            def json(self):
                                return json.loads(self.text)
                        
                        results = engine.response(ResponseWrapper(resp, params))
                
            clean = []
            if isinstance(results, list):
                engine_name = getattr(engine, "NAME", engine.__name__.split('.')[-1])
                engine_weight = getattr(engine, "WEIGHT", 1.0)
                for r in results:
                    r["source"] = engine_name
                    r["engine_weight"] = engine_weight
                    if self.is_legit(r):
                        clean.append(r)
            return clean
        except Exception as e:
            eng_name = getattr(engine, "NAME", "unknown")
            print(f"ERROR in engine {eng_name}: {repr(e)}")
            import traceback
            traceback.print_exc()
            return []

    def is_legit(self, result: Dict) -> bool:
        url = result.get('url', '').lower()
        title = result.get('title', '').lower()
        content = result.get('content', '').lower()

        # 1. Filtrado de anuncios (Solo si el patrón es muy específico o en URL)
        for pattern in self.ad_patterns:
            if pattern in url:
                return False
            # Solo filtrar por título/contenido si es corto (anuncios típicos)
            if (pattern in title and len(title) < 40) or (pattern in content[:20]):
                return False
                
        # 2. Relaxed Legitimacy - No tirar resultados legítimos
        if len(title) < 3: return False
        if "..." in title and len(title) < 15: return False
        
        # 3. Solo URLs de confianza o útiles
        if not url.startswith('http') and not url.startswith('#'):
            return False
            
        return True

    def process_and_rank(self, results_groups):
        score_map = defaultdict(lambda: {"title": "", "url": "", "content": "", "score": 0.0, "sources": set(), "engine_positions": []})
        infoboxes = [] # Resultados destacados (Wiki, Calculadora, OSM)
        
        for results in results_groups:
            for position, res in enumerate(results):
                # 1. Extraer INFOTOOLS (Respuestas Destacadas Reales)
                if res.get("template") == "infobox.html":
                    # Evitar duplicar infoboxes exactos de la misma fuente
                    if not any(i['title'] == res['title'] and i['source'] == res['source'] for i in infoboxes):
                        infoboxes.append(res)
                    continue

                # 2. Normalización de URL para deduplicación robusta (SearXNG style)
                raw_url = res.get('url', '').lower()
                clean_url = raw_url.replace('https://', '').replace('http://', '').replace('www.', '').split('#')[0].rstrip('/')
                if not clean_url: continue
                
                item = score_map[clean_url]
                
                # Preservar el título más limpio y descripción más rica
                if not item["title"] or (len(res.get('content', '')) > len(item.get('content', '')) and len(res.get('title', '')) > 5):
                    for key, val in res.items():
                        if key not in ["score", "sources", "engine_positions"]:
                            item[key] = val
                
                # 3. Ranking Armónico Ponderado
                # SearXNG recompensa mucho aparecer en el TOP 1 de cualquier motor confiable.
                engine_weight = res.get("engine_weight", 1.0)
                
                # Bonus por Dominios de Autoridad Superior
                auth_bonus = 1.0
                trusted_list = [".edu", ".org", ".gov", "wikipedia.org", "reuters.com", "arxiv.org", "stackoverflow.com", "github.com"]
                if any(ext in clean_url for ext in trusted_list):
                    auth_bonus = 1.25
                
                # Penalización por snippets "con puntos suspensivos" iniciales que no aportan valor
                snippet_penalty = 1.0
                content = res.get('content', '')
                if content.startswith('...') or len(content) < 40:
                    snippet_penalty = 0.8

                # Fórmula: (Peso Motor * Bonus Auth * Snippet Penalty) / Raiz(Posición + 1)
                # La raíz cuadrada de la posición suaviza la caída de relevancia, pero prioriza el top 3.
                item["score"] += (engine_weight * auth_bonus * snippet_penalty) / ((position + 1) ** 0.5)
                item["sources"].add(res['source'])
                item["engine_positions"].append(position)
        
        # 4. Consolidar y Aplicar Bonus de Diversidad (Si aparece en muchos motores)
        final = []
        for url, data in score_map.items():
            data["sources"] = list(data["sources"])
            # Bonus de Consenso: Si aparece en muchos motores, es fiable.
            consensus_bonus = 1.0 + (0.5 * (len(data["sources"]) - 1))
            data["score"] *= consensus_bonus
            
            # Penalización por URL de poca profundidad (homes/meta-urls suelen ser menos relevantes que artículos)
            if url.count('/') < 2: data["score"] *= 0.85

            final.append(data)
            
        # Ordenación Final por Score
        final.sort(key=lambda x: x["score"], reverse=True)
        
        # Limitar resultados para limpieza absoluta
        limited_results = final[:40]
        
        return limited_results, infoboxes
