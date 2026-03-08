import importlib
import os
import sys
import asyncio
import httpx
import json
import time
from typing import List, Dict, Any, Set
from collections import defaultdict

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
            "!g": "google", "!w": "wikipedia", "!yt": "videos", 
            "!gh": "github", "!so": "stackoverflow", "!i": "images",
            "!n": "news", "!ddg": "duckduckgo", "!bi": "bing",
            "!red": "reddit", "!py": "pypi", "!npm": "npm"
        }

        # Ad-block global list (SearXNG style)
        self.ad_patterns = [
            "googleads", "pagead", "doubleclick", "partner.googleadservices",
            "adservice", "sponsored", "ads-", "ad-content", "promocionado",
            "publicidad", "anuncio"
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
                    
                    cfg = config_engines.get(engine_name, {"enabled": True, "categories": ["general"], "weight": 1.0})
                    module.ENABLED = cfg.get("enabled", True)
                    module.CATEGORIES = cfg.get("categories", ["general"])
                    module.WEIGHT = cfg.get("weight", 1.0)
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

        # 3. Parallel Search
        tasks = []
        timeout_limit = self.settings["general"].get("timeout", 4.0)

        if target_engine:
            # Si hay un bang, forzamos ese motor o categoria
            if target_engine in self.engines:
                tasks.append(self.call_engine(self.engines[target_engine], clean_query, category, pageno, timeout_limit))
            else:
                # Si el bang es una categoria, buscamos en esa categoria
                category = target_engine 

        if not tasks:
            for name, engine in self.engines.items():
                if engine.ENABLED and category in engine.CATEGORIES:
                    tasks.append(self.call_engine(engine, clean_query, category, pageno, timeout_limit))
        
        # Fallback
        if not tasks:
            for name, engine in self.engines.items():
                if engine.ENABLED and "general" in engine.CATEGORIES:
                    tasks.append(self.call_engine(engine, clean_query, "general", pageno, timeout_limit))

        # Parallel Wait
        results_list = await asyncio.gather(*tasks, return_exceptions=True)
        valid_results = [r for r in results_list if isinstance(r, list)]
        
        ranked = self.process_and_rank(valid_results)
        
        # Cache Result
        ttl = self.settings["general"].get("cache_ttl", 600)
        self._cache[cache_key] = (ranked, now + ttl)
        
        return ranked

    async def call_engine(self, engine, query, category, pageno, timeout_limit):
        try:
            params = {
                "pageno": pageno,
                "category": category,
                "url": None,
                "method": "GET",
                "headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                    "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                    "Connection": "keep-alive"
                },
                "data": {},
                "cookies": {},
                "timeout": timeout_limit
            }
            
            # Ejecutar lógica del motor
            if hasattr(engine, "request_categorized"):
                engine.request_categorized(query, category, params)
            else:
                engine.request(query, params)
            
            if not params["url"]:
                return []

            async with httpx.AsyncClient(
                follow_redirects=True, 
                timeout=params["timeout"],
                limits=httpx.Limits(max_keepalive_connections=50, max_connections=200),
                http2=True
            ) as client:
                if params["method"] == "POST":
                    resp = await client.post(params["url"], data=params["data"], headers=params["headers"], cookies=params["cookies"])
                else:
                    resp = await client.get(params["url"], headers=params["headers"], cookies=params["cookies"])
                
                if resp.status_code != 200:
                    return []

                class ResponseWrapper:
                    def __init__(self, r, p):
                        self.text = r.text
                        self.status_code = r.status_code
                        self.search_params = p
                        self.url = r.url
                    def json(self):
                        return json.loads(self.text)
                
                results = engine.response(ResponseWrapper(resp, params))
                
                clean = []
                for r in results:
                    r["source"] = engine.NAME
                    r["engine_weight"] = engine.WEIGHT
                    if self.is_legit(r):
                        clean.append(r)
                return clean
        except Exception:
            return []

    def is_legit(self, result: Dict) -> bool:
        url = result.get('url', '').lower()
        title = result.get('title', '').lower()
        content = result.get('content', '').lower()

        # Filtrado de anuncios avanzado
        for pattern in self.ad_patterns:
            if pattern in url or (pattern in title and len(title) < 45) or (pattern in content[:40]):
                return False
                
        if not url.startswith('http'):
            return False
            
        return True

    def process_and_rank(self, results_groups):
        score_map = defaultdict(lambda: {"title": "", "url": "", "content": "", "score": 0.0, "sources": set(), "img_src": None})
        
        for results in results_groups:
            for position, res in enumerate(results):
                # Normalización de URL para deduplicación
                url = res['url'].lower().replace('https://', '').replace('http://', '').replace('www.', '').split('#')[0].rstrip('/')
                
                item = score_map[url]
                if not item["content"] or len(res['content']) > len(item['content']):
                    item["title"] = res['title']
                    item["url"] = res['url']
                    item["content"] = res['content']
                
                if res.get("img_src"):
                    item["img_src"] = res["img_src"]
                
                weight = res.get("engine_weight", 1.0)
                # Ranking Armónico: Mayor peso si aparece arriba en motores confiables
                item["score"] += (weight / (position + 1))
                item["sources"].add(res['source'])
        
        final = []
        for url, data in score_map.items():
            data["sources"] = list(data["sources"])
            # Bonus por diversidad de fuentes
            data["score"] *= (1 + 0.15 * (len(data["sources"]) - 1))
            final.append(data)
            
        return sorted(final, key=lambda x: x['score'], reverse=True)
