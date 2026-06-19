"""
Google Images engine.
Uses GSA User-Agent to bypass JS-redirect blocks.
Extracts real image URLs and encrypted-tbn thumbnails from the HTML.
"""
import re
import random
from urllib.parse import urlencode, unquote
from utils import LANGUAGE_MAP
from selectolax.parser import HTMLParser

CATEGORIES = ["images"]
WEIGHT = 1.5

_GSA_UAS = [
    "Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.105 Mobile Safari/537.36 NSTNWV",
    "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Mobile Safari/537.36 NSTNWV",
    "Mozilla/5.0 (Linux; Android 7.0; SM-G892A Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Mobile Safari/537.36 NSTNWV",
    "Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Mobile Safari/537.36 NSTNWV",
    "Mozilla/5.0 (Linux; Android 9; SM-G960F Build/PPR1.180610.011) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.104 Mobile Safari/537.36 NSTNWV",
]


def request(query, params):
    lang = params.get("language", "es")
    lang_code = LANGUAGE_MAP.get("google", {}).get(lang, "es")

    query_params = {
        "q": query,
        "tbm": "isch",
        "hl": lang_code,
        "num": 20,
    }
    params["url"] = f"https://www.google.com/search?{urlencode(query_params)}"
    params["headers"]["User-Agent"] = random.choice(_GSA_UAS)
    params["headers"]["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    params["headers"]["Accept-Language"] = f"{lang_code},en;q=0.7"
    params["headers"]["Accept-Encoding"] = "gzip, deflate"
    params["headers"]["Referer"] = "https://www.google.com/"

    cb_val = random.randint(20230000, 20249999)
    params["cookies"]["CONSENT"] = f"YES+cb.{cb_val}-04-p0.{lang}+FX+414"
    params["cookies"]["SOCS"] = "CAESHAgBEhJmb3NfbGVzcy9zZWFyY2gvaG9tZQ"


def response(resp):
    results = []
    html = resp.text

    if "httpservice/retry/enablejs" in html:
        return results

    tree = HTMLParser(html)

    # Extract real image URLs and encrypted-tbn thumbnail URLs from script/JSON data.
    # These appear as parallel arrays in the HTML — one real URL and one tbn per result.
    real_imgs = re.findall(
        r'"(https?://(?!www\.gstatic|encrypted-tbn|maps\.gstatic)[^"]{15,}?\.(?:jpg|jpeg|png|webp)(?:[^"]*?))"',
        html,
    )
    tbn_imgs = re.findall(r'"(https?://encrypted-tbn[^"]+)"', html)

    # Parse isv-r containers for source page URLs and titles
    for i, node in enumerate(tree.css("div.isv-r")):
        img_node = node.css_first("img.islir, img")
        alt = img_node.attributes.get("alt", "") if img_node else ""
        title = alt.replace("Image result for ", "").strip() if alt else ""

        # Get source page URL
        source_url = ""
        for a in node.css("a[href]"):
            href = a.attributes.get("href", "")
            if "/url?q=" in href:
                source_url = unquote(href.split("/url?q=")[1].split("&sa=")[0])
                break
            elif href.startswith("http") and "google.com" not in href:
                source_url = href
                break

        # Match real image and thumbnail from parallel arrays
        real_src = real_imgs[i] if i < len(real_imgs) else None
        tbn_src = tbn_imgs[i] if i < len(tbn_imgs) else None

        if not real_src and not tbn_src:
            continue

        results.append({
            "template": "images.html",
            "title": title or query,
            "url": source_url or real_src or "#",
            "img_src": real_src or tbn_src,
            "thumbnail_src": tbn_src or real_src,
            "source": "google_images",
            "content": f"Imagen de Google Images",
        })

    return results
