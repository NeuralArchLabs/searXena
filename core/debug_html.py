import asyncio
import httpx
from selectolax.parser import HTMLParser
import sys
import os

# Añadir el directorio base al path para importar motores
sys.path.insert(0, os.getcwd())

import engines.google as google
import engines.duckduckgo as duckduckgo

async def debug_html(url, name):
    print(f"--- Debug HTML: {name} ---")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    
    async with httpx.AsyncClient(follow_redirects=True, verify=False) as client:
        resp = await client.get(url, headers=headers)
        print(f"Status: {resp.status_code}")
        print(f"HTML Snippet (first 1000 chars):\n{resp.text[:1000]}")
        
        # Guardar para inspeccion completa si es necesario
        with open(f"debug_{name.lower()}.html", "w", encoding="utf-8") as f:
            f.write(resp.text)

async def main():
    await debug_html("https://www.google.com/search?q=gemini&hl=es", "Google")
    await debug_html("https://duckduckgo.com/lite/?q=gemini", "DuckDuckGo")

if __name__ == "__main__":
    asyncio.run(main())
