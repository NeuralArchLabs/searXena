import asyncio
import os
import sys

async def main():
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from extractor import OZENExtractor
    
    extractor = OZENExtractor()
    # Test on a known URL containing images, e.g. a Xataka page or another news page
    url = "https://www.applesfera.com/desarrollo-de-software/apple-explica-que-solo-serie-iphone-15-pro-cumple-requisitos-apple-intelligence"
    print(f"Extracting from {url}...")
    res = await extractor.extract(url)
    
    content = res.get("content", "")
    print(f"Content length: {len(content)}")
    print("Does it contain img tag?")
    import re
    imgs = re.findall(r'<img[^>]+>', content)
    print(f"Found {len(imgs)} img tags:")
    for img in imgs[:5]:
        print("  ", img)
        
    await extractor.close()

if __name__ == "__main__":
    asyncio.run(main())
