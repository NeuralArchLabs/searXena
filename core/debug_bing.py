import asyncio
import httpx
from selectolax.parser import HTMLParser
import sys
import os

async def debug_bing(url, name):
    print(f"--- Debug HTML: {name} ---")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8"
    }
    
    async with httpx.AsyncClient(follow_redirects=True, verify=False) as client:
        resp = await client.get(url, headers=headers)
        print(f"Status: {resp.status_code}")
        
        with open(f"debug_{name.lower()}.html", "w", encoding="utf-8") as f:
            f.write(resp.text)
        
        tree = HTMLParser(resp.text)
        # Buscar algo que parezca un resultado
        results = tree.css('li.b_algo')
        print(f"Selector 'li.b_algo' encontró: {len(results)}")

async def main():
    await debug_bing("https://www.bing.com/search?q=gemini", "Bing")

if __name__ == "__main__":
    asyncio.run(main())
