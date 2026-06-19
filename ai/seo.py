import re

from ai.text_utils import clean_product_name, clean_text


def _truncate(text, max_length):
    if len(text) <= max_length:
        return text
    text = text[:max_length].rstrip()
    if " " in text:
        text = text.rsplit(" ", 1)[0]
    return text + "..."


def generate_seo_title(product):

    title = clean_product_name(product.get("product_name") or "")

    if not title:
        return "Product Review, Specifications & Price"

    suffix = "Features, Price & Review"
    seo_title = f"{title} | {suffix}"

    if len(seo_title) > 65:
        suffix = "Review & Specifications"
        seo_title = f"{title} | {suffix}"

    if len(seo_title) > 65:
        title = title[: 65 - len(suffix) - 3].rstrip()
        seo_title = f"{title} | {suffix}"

    return seo_title


def generate_meta_description(product):

    title = clean_product_name(product.get("product_name") or "")
    description = clean_text(str(product.get("description") or ""))
    category = str(product.get("category") or "").strip()
    price = str(product.get("price") or "").strip()

    fragments = ["Discover"]
    if title:
        fragments.append(title)

    if price:
        fragments.append(f"priced at {price}")

    if category:
        fragments.append(f"in {category}")

    prefix = " ".join(fragments).strip()
    suffix = "Explore features, specifications and product details."

    if description:
        snippet = re.split(r"(?<=[.!?])\s+", description)[0].strip()
        if snippet:
            suffix = snippet

    meta = f"{prefix}. {suffix}" if prefix else suffix
    meta = re.sub(r"\s+", " ", meta).strip()

    return _truncate(meta, 155)
