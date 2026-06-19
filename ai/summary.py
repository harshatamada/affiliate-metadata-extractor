import re

from ai.text_utils import clean_product_name, clean_text


def _truncate(text, max_length=155):
    if len(text) <= max_length:
        return text
    text = text[:max_length].rstrip()
    if " " in text:
        text = text.rsplit(" ", 1)[0]
    return text + "..."


def _first_sentence(text):
    if not text:
        return ""
    sentence = re.split(r"(?<=[.!?])\s+", text)[0].strip()
    return sentence or text


def generate_summary(product):

    title = clean_product_name(product.get("product_name") or "")
    description = clean_text(str(product.get("description") or ""))
    brand = str(product.get("brand") or "").strip()
    price = str(product.get("price") or "").strip()

    if brand and brand.lower() not in title.lower():
        title_phrase = f"{title} from {brand}" if title else brand
    else:
        title_phrase = title or brand

    if price:
        if description:
            description_snippet = _first_sentence(description)
            return _truncate(
                f"{title_phrase} is available for {price}. {description_snippet}"
            )
        return f"{title_phrase} is available for {price}. Explore features, specifications and product details."

    if description:
        description_snippet = _first_sentence(description)
        if title_phrase:
            return _truncate(f"{title_phrase}. {description_snippet}")
        return _truncate(description_snippet)

    if title_phrase:
        return f"{title_phrase}. Explore features, specifications and product details."

    return "Explore product features, specifications and details."


def generate_highlights(product):

    highlights = []

    title = str(product.get("product_name") or "")
    brand = str(product.get("brand") or "")

    if brand:
        highlights.append(f"Brand: {brand}")

    if title:
        highlights.append(title[:80])

    return highlights[:5]


def generate_product_summary(product):

    return {
        "summary": generate_summary(product),
        "highlights": generate_highlights(product)
    }