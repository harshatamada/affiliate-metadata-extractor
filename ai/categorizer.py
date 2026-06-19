import re
from collections import Counter

from ai.text_utils import clean_text, MARKETPLACE_TERMS

# Keyword → (Category, Subcategory)
CATEGORY_RULES = {
    # Electronics
    "iphone": ("Electronics", "Mobile"),
    "samsung": ("Electronics", "Mobile"),
    "redmi": ("Electronics", "Mobile"),
    "xiaomi": ("Electronics", "Mobile"),
    "asus": ("Electronics", "Laptop"),
    "chromebook": ("Electronics", "Laptop"),
    "macbook": ("Electronics", "Laptop"),
    "hp": ("Electronics", "Laptop"),
    "dell": ("Electronics", "Laptop"),
    "bluetooth": ("Electronics", "Accessories"),
    "wireless": ("Electronics", "Accessories"),
    "gaming": ("Electronics", "Laptop"),
    "ssd": ("Electronics", "Storage"),
    "5g": ("Electronics", "Mobile"),
    "amoled": ("Electronics", "Display"),
    "smart tv": ("Electronics", "Television"),
    "television": ("Electronics", "Television"),
    "processor": ("Electronics", "Laptop"),

    # Fashion
    "shirt": ("Fashion", "Clothing"),
    "tshirt": ("Fashion", "Clothing"),
    "jeans": ("Fashion", "Clothing"),
    "kurta": ("Fashion", "Clothing"),
    "dress": ("Fashion", "Clothing"),
    "casual": ("Fashion", "Clothing"),
    "design": ("Fashion", "Clothing"),
    "men": ("Fashion", "Clothing"),
    "women": ("Fashion", "Clothing"),
    "sneakers": ("Fashion", "Shoes"),
    "shoes": ("Fashion", "Shoes"),
    "oversized": ("Fashion", "Clothing"),
    "ethnic": ("Fashion", "Clothing"),
    "nike": ("Fashion", "Shoes"),
    "puma": ("Fashion", "Shoes"),
    "adidas": ("Fashion", "Shoes"),

    # Beauty
    "serum": ("Beauty", "Skincare"),
    "spf": ("Beauty", "Skincare"),
    "matte": ("Beauty", "Makeup"),
    "glow": ("Beauty", "Skincare"),
    "acne": ("Beauty", "Skincare"),

    # Home
    "sofa": ("Home", "Furniture"),
    "wooden": ("Home", "Furniture"),
    "bed": ("Home", "Furniture"),
    "table": ("Home", "Furniture"),
    "decor": ("Home", "Decor"),

    # Health & Fitness
    "whey": ("Health", "Supplements"),
    "protein": ("Health", "Supplements"),
    "muscle": ("Health", "Supplements"),
    "fitness": ("Health", "Supplements"),
    "gym": ("Sports", "Fitness"),
    "running": ("Sports", "Fitness"),

    # Baby
    "baby": ("Baby", "Care"),
    "kids": ("Baby", "Clothing"),
    "feeding": ("Baby", "Care"),
}

KEYWORD_STOPWORDS = {
    "with", "and", "the", "for", "is", "a", "at", "on", "in", "buy", "online",
    "new", "best", "price", "sale", "offer", "offers", "free", "shipping",
    "latest", "product", "available", "features", "specifications", "details",
    "india", "indian", "limited",
}

ALLOWED_SHORT_TAGS = {"5g", "4k", "hd", "uhd", "pro", "max", "xl", "xxl", "oe"}

TOKEN_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*", re.IGNORECASE)


def _is_valid_keyword(token):
    token = token.lower().strip()
    if not token or token in KEYWORD_STOPWORDS:
        return False
    if token.isdigit():
        return False
    if len(token) < 3:
        return False
    if token in MARKETPLACE_TERMS:
        return False
    return True


def _is_valid_tag(token):
    token = token.lower().strip()
    if not token or token in KEYWORD_STOPWORDS:
        return False
    if token.isdigit():
        return False
    if token in MARKETPLACE_TERMS:
        return False
    if len(token) < 3 and token not in ALLOWED_SHORT_TAGS:
        return False
    return True


def extract_keywords(text, top_n=10):
    cleaned = clean_text(text)
    words = TOKEN_PATTERN.findall(cleaned.lower())
    filtered = [w for w in words if _is_valid_keyword(w)]
    frequency = Counter(filtered)
    ordered = []
    for token in filtered:
        if token not in ordered:
            ordered.append(token)
    ranked = sorted(ordered, key=lambda w: (-frequency[w], ordered.index(w)))
    return ranked[:top_n]


def generate_tags(keywords, tag_count=3):
    tags = []
    for token in keywords:
        if _is_valid_tag(token):
            tags.append(token)
        if len(tags) >= tag_count:
            break
    return tags

def map_category(keywords):
    for word in keywords:
        if word in CATEGORY_RULES:
            return CATEGORY_RULES[word][0], CATEGORY_RULES[word][1]
    return "General", "General"

def process_product(product):

    text = " ".join([
        str(product.get("product_name") or ""),
        str(product.get("description") or ""),
        str(product.get("brand") or "")
    ])

    keywords = extract_keywords(text)
    tags = generate_tags(keywords)
    category, subcategory = map_category(keywords)

    return {
        "category": category,
        "subcategory": subcategory,
        "tags": tags,
        "keywords": keywords
    }

