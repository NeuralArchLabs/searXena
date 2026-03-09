import asyncio
import httpx
from selectolax.parser import HTMLParser
import sys
import os

# Añadir el directorio base al path para importar motores
sys.path.insert(0, os.getcwd())

import engines.google as google
import engines.duckduckgo as duckduckgo

async def test_engine(engine, name):
    print(f"--- Probando motor: {name} ---")
    params = {
        "pageno": 1,
        "category": "general",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        },
        "timeout": 10.0,
        "method": "GET",
        "data": {},
        "cookies": {},
        "url": None
    }
    
    try:
        # Algunos motores esperan un query string
        class EngineMock:
            NAME = name.lower()
            WEIGHT = 1.0
        
        engine.request("gemini", params)
        print(f"URL: {params['url']}")
        
        async with httpx.AsyncClient(follow_redirects=True, verify=False) as client:
            resp = await client.get(params['url'], headers=params['headers'])
            print(f"Status Code: {resp.status_code}")
            
            class FakeResp:
                def __init__(self, r, p):
                    self.text = r.text
                    self.url = str(r.url)
                    self.search_params = p
                def json(self): return {}
                
            results = engine.response(FakeResp(resp, params))
            print(f"Resultados encontrados: {len(results)}")
            for r in results[:3]:
                print(f"- {r.get('title')} ({r.get('url')})")
                
    except Exception as e:
        print(f"Error en {name}: {e}")

async def main():
    await test_engine(google, "Google")
    await test_engine(duckduckgo, "DuckDuckGo")

if __name__ == "__main__":
    asyncio.run(main())
