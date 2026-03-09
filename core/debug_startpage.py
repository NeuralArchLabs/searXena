import asyncio
import httpx
from selectolax.parser import HTMLParser
import sys
import os

async def debug_startpage(url, name):
    print(f"--- Debug HTML: {name} ---")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    
    async with httpx.AsyncClient(follow_redirects=True, verify=False) as client:
        # Startpage requiere un POST para busquedas o un GET especifico
        resp = await client.get(url, headers=headers)
        print(f"Status: {resp.status_code}")
        
        with open(f"debug_{name.lower()}.html", "w", encoding="utf-8") as f:
            f.write(resp.text)
        
        tree = HTMLParser(resp.text)
        results = tree.css('div.w-gl__result, .result')
        print(f"Selector 'div.w-gl__result' encontró: {len(results)}")

async def main():
    await debug_startpage("https://www.startpage.com/sp/search?query=gemini", "Startpage")

if __name__ == "__main__":
    asyncio.run(main())
