import asyncio
import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extractor import OZENExtractor

async def main():
    url = "https://www.infobae.com/tecno/2026/06/19/gemini-live-deja-de-ser-solo-un-chatbot-la-ia-de-google-ahora-tiene-memoria-y-acceso-a-mas-servicios/"
    extractor = OZENExtractor()
    res = await extractor.extract(url)
    await extractor.close()
    
    content = res.get("content", "")
    print("Searching for 'publicidad' case-insensitive in content HTML...")
    matches = re.findall(r'([^<>\n]{0,100}publicidad[^<>\n]{0,100})', content, re.IGNORECASE)
    for i, m in enumerate(matches):
        print(f"{i+1}: ... {m.strip()} ...")
        
    print("\n--- RAW CONTENT FRAGMENT ARROUND MATCHES ---")
    # Print the lines containing 'publicidad'
    for line in content.splitlines():
        if "publicidad" in line.lower() or "anuncio" in line.lower():
            print(f"LINE: {line.strip()}")

if __name__ == "__main__":
    asyncio.run(main())
