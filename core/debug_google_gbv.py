import asyncio
import httpx
from selectolax.parser import HTMLParser
import sys
import os

async def debug_google_gbv(url, name):
    print(f"--- Debug HTML: {name} ---")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    
    async with httpx.AsyncClient(follow_redirects=True, verify=False) as client:
        resp = await client.get(url, headers=headers)
        print(f"Status: {resp.status_code}")
        
        with open(f"debug_{name.lower()}.html", "w", encoding="utf-8") as f:
            f.write(resp.text)
        
        tree = HTMLParser(resp.text)
        # Buscar algo que parezca un resultado
        results = tree.css('div.g')
        print(f"Selector 'div.g' encontró: {len(results)}")
        
        # Probar selectores de la version basica
        results_basica = tree.css('div.ZIN63') # A veces usado en GBV
        print(f"Selector 'div.ZIN63' encontró: {len(results_basica)}")

async def main():
    await debug_google_gbv("https://www.google.com/search?q=gemini&gbv=1", "Google_GBV")

if __name__ == "__main__":
    asyncio.run(main())
