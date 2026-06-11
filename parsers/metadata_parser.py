from bs4 import BeautifulSoup


def parse_metadata(html):

    soup = BeautifulSoup(html, "html.parser")

    data = {
        "title": None,
        "description": None,
        "image": None,
        "brand": None
    }

    # OpenGraph title
    title = soup.find(
        "meta",
        property="og:title"
    )

    if title:
        data["title"] = title.get("content")

    # Amazon product title fallback
    if not data["title"]:

        product_title = soup.find(
            id="productTitle"
        )

        if product_title:
            data["title"] = (
                product_title.get_text()
                .strip()
            )

    # HTML title fallback
    if not data["title"] and soup.title:
        data["title"] = (
            soup.title.text.strip()
        )

    # Description
    desc = soup.find(
        "meta",
        attrs={"name": "description"}
    )

    if desc:
        data["description"] = desc.get("content")

    # OpenGraph image
    image = soup.find(
        "meta",
        property="og:image"
    )

    if image:
        data["image"] = image.get("content")

    # Amazon image fallback
    if not data["image"]:

        image = soup.find(
            "img",
            id="landingImage"
        )

        if image:
            data["image"] = (
                image.get("data-old-hires")
                or image.get("src")
            )

    # Amazon brand fallback
    brand = soup.find(
        id="bylineInfo"
    )

    if brand:
        data["brand"] = (
            brand.get_text()
            .replace("Brand:", "")
            .strip()
        )

    return {
        "product_name": data["title"],
        "description": data["description"],
        "image": data["image"],
        "brand": data["brand"],
        "product_type": None
    }