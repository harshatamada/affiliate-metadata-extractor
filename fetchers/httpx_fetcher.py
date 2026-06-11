import httpx


def fetch_html(url):

    headers = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
}

    try:

        response = httpx.get(
            url,
            headers=headers,
            follow_redirects=True,
            timeout=20
        )

        response.raise_for_status()

        return response.text

    except Exception as e:
       print("\nHTTPX FAILED")
       print(type(e))
       print(e)
       return None