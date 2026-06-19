import html
import json
import re

from bs4 import BeautifulSoup


PRICE_REGEX = re.compile(r'₹\s?[\d,]+(?:\.\d+)?')
COUPON_TERMS = re.compile(r'coupon|cashback|bank offer|instant discount|discount|offer|bundle|voucher|save|deal', re.I)


def format_price(value):
    if not value:
        return None

    if isinstance(value, (int, float)):
        integer = int(value)
        return f"₹{integer:,}"

    text = str(value)
    match = re.search(r'([\d,]+(?:\.\d+)?)', text)
    if not match:
        return None

    number = match.group(1).replace(',', '')
    try:
        if '.' in number:
            float_value = float(number)
            integer = int(float_value)
        else:
            integer = int(number)
    except ValueError:
        return None

    return f"₹{integer:,}"


def extract_jsonld_price(soup):
    scripts = soup.find_all('script', type='application/ld+json')
    for script in scripts:
        try:
            payload = json.loads(script.string or '{}')
        except (json.JSONDecodeError, TypeError):
            continue

        if isinstance(payload, list):
            for item in payload:
                price = _extract_price_from_jsonld_item(item)
                if price:
                    return price
        else:
            price = _extract_price_from_jsonld_item(payload)
            if price:
                return price

    return None


def _extract_price_from_jsonld_item(item):
    if not isinstance(item, dict):
        return None

    if item.get('@type', '').lower() == 'product' or 'offers' in item:
        offers = item.get('offers')
        if isinstance(offers, list):
            for offer in offers:
                price = _extract_price_from_jsonld_item(offer)
                if price:
                    return price
        elif isinstance(offers, dict):
            price = offers.get('price') or offers.get('priceCurrency')
            return format_price(price)

    return None


def extract_amazon_price(soup):
    price_ids = [
        'priceblock_ourprice',
        'priceblock_dealprice',
        'priceblock_saleprice',
        'priceblock_pospromoprice',
    ]

    for price_id in price_ids:
        node = soup.find(id=price_id)
        if node:
            price = format_price(node.get_text())
            if price:
                return price

    for price_whole in soup.select('span.a-price-whole'):
        fraction = price_whole.find_next('span', class_='a-price-fraction')
        candidate = price_whole.get_text()
        if fraction:
            candidate = f"{candidate}.{fraction.get_text()}"
        price = format_price(candidate)
        if price:
            return price

    for offscreen in soup.select('span.a-offscreen'):
        text = offscreen.get_text() or ''
        if text and not COUPON_TERMS.search(text):
            price = format_price(text)
            if price:
                return price

    return None


def extract_flipkart_price(soup):
    selectors = [
        'div._30jeq3._16Jk6d',
        'div._30jeq3',
        'span._2-ut7f._1WpvJ7',
        'div._1vC4OE',
    ]

    for selector in selectors:
        node = soup.select_one(selector)
        if node:
            price = format_price(node.get_text())
            if price:
                return price

    meta_price = extract_metadata_price(soup)
    if meta_price:
        return meta_price

    return None


def extract_metadata_price(soup):
    meta_selectors = [
        ('meta', {'itemprop': 'price'}),
        ('meta', {'property': 'product:price:amount'}),
        ('meta', {'name': 'price'}),
        ('meta', {'name': 'product:price:amount'}),
        ('span', {'itemprop': 'price'}),
    ]

    for tag_name, attrs in meta_selectors:
        tag = soup.find(tag_name, attrs=attrs)
        if tag:
            value = tag.get('content') or tag.get_text()
            price = format_price(value)
            if price:
                return price

    return None


def extract_price_from_html(html_text, soup):
    if html_text and 'amazon.' in html_text.lower():
        price = extract_amazon_price(soup)
        if price:
            return price

    if html_text and 'flipkart.' in html_text.lower():
        price = extract_flipkart_price(soup)
        if price:
            return price

    price = extract_jsonld_price(soup)
    if price:
        return price

    price = extract_metadata_price(soup)
    if price:
        return price

    matches = PRICE_REGEX.finditer(html_text or '')
    for match in matches:
        context = (html_text or '')[max(0, match.start() - 80): match.end() + 80]
        if COUPON_TERMS.search(context):
            continue
        price = format_price(match.group(0))
        if price:
            return price

    return None


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

    price = extract_price_from_html(html, soup)

    return {
        "product_name": data["title"],
        "description": data["description"],
        "image": data["image"],
        "brand": data["brand"],
        "product_type": None,
        "price": price
    }