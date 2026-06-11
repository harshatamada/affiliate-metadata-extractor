from fetchers.httpx_fetcher import fetch_html
from fetchers.playwright_fetcher import fetch_html_playwright

from extractor import extract_product_data


url = input("Enter normalized URL: ")

print("\nTrying HTTPX...")

html = fetch_html(url)
print("HTML is None:", html is None)

if html:
    print("HTML length:", len(html))
    print("First 500 chars:")
    print(html[:500])

blocked = False

if not html:
    blocked = True

elif "<title>Robot Check</title>" in html:
    blocked = True

elif "sorry, we just need to make sure you're not a robot" in html.lower():
    blocked = True

print("BLOCKED =", blocked)

if blocked:

    print("\nTrying Playwright...")

    html = fetch_html_playwright(url)


if not html:

    print("Failed to fetch page")

    exit()


product = extract_product_data(html)

print("\nRESULT\n")

print(product)
with open(
    "debug.html",
    "w",
    encoding="utf-8"
) as f:
    f.write(html)