from fetchers.httpx_fetcher import fetch_html
from fetchers.playwright_fetcher import fetch_html_playwright

from extractor import extract_product_data


import json

def run_extraction(data):

    url = data["normalizedUrl"]

    

    html = fetch_html(url)

    if html:
        print("HTML length:", len(html))

    blocked = False

    if not html:
        blocked = True

    elif "<title>Robot Check</title>" in html:
        blocked = True

    elif "sorry, we just need to make sure you're not a robot" in html.lower():
        blocked = True

    print("BLOCKED =", blocked)

    if blocked:

       

        html = fetch_html_playwright(url)

    if not html:
        print("Failed to fetch page")
        return None

    product = extract_product_data(html)

    # Fallback if extraction quality is poor
    if (
        product.get("product_name") == "Amazon.in"
        or product.get("image") is None
    ):
        

        html = fetch_html_playwright(url)

        if html:
            product = extract_product_data(html)

   

    return product