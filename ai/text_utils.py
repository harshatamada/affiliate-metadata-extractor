import re

MARKETPLACE_TERMS = {
    "amazon",
    "amazon.in",
    "flipkart",
    "flipkart.com",
    "myntra",
    "snapdeal",
    "ebay",
}

NOISE_PATTERNS = [
    r"price in india",
    r"buy online",
    r"buy",
    r"online only",
    r"shop online",
    r"best price",
    r"best seller",
    r"available at",
    r"sold by",
    r"free shipping",
    r"cashback",
    r"cash on delivery",
    r"discount",
    r"offer",
    r"offers",
    r"sale",
    r"coupon",
    r"off",
    r"amazon\.in",
    r"flipkart\.com",
    r"amazon",
    r"flipkart",
    r"myntra",
    r"snapdeal",
    r"ebay",
]

NOISE_REGEX = re.compile(
    r"(?i)\b(?:" + r"|".join(NOISE_PATTERNS) + r")\b"
)
CURRENCY_REGEX = re.compile(r"(?i)\b(?:rs\.?|inr|₹)\s?[\d,]+(?:\.\d+)?\b")
SEPARATOR_REGEX = re.compile(r"\s*[-–|:]\s*")
FLIPKART_CLEANUP_PATTERNS = [
    re.compile(r"(?i)\s*-\s*buy\b.*$"),
    re.compile(r"(?i)\bonline at best price\b"),
    re.compile(r"(?i)\bshop online\b"),
    re.compile(r"(?i)\bflipkart\.com\b"),
]
NORMALIZE_SPACES = re.compile(r"\s{2,}")


def clean_text(text):
    if not text:
        return ""

    text = str(text)
    text = NOISE_REGEX.sub(" ", text)
    text = CURRENCY_REGEX.sub(" ", text)
    text = NORMALIZE_SPACES.sub(" ", text)
    text = text.strip(" -–_:|,.")
    return text.strip()


def _normalize_segment(segment):
    normalized = re.sub(r"[^\w\s-]", " ", segment.lower())
    normalized = NORMALIZE_SPACES.sub(" ", normalized).strip()
    return normalized


def clean_product_name(title):
    if not title:
        return ""

    title = str(title).strip()
    for pattern in FLIPKART_CLEANUP_PATTERNS:
        title = pattern.sub("", title)

    segments = [s.strip() for s in SEPARATOR_REGEX.split(title) if s.strip()]
    cleaned_segments = []
    seen = set()

    for segment in segments:
        segment = clean_text(segment)
        if not segment:
            continue

        normalized = _normalize_segment(segment)
        if not normalized or normalized in seen:
            continue

        if normalized in MARKETPLACE_TERMS:
            continue

        seen.add(normalized)
        cleaned_segments.append(segment)

    candidate = " ".join(cleaned_segments).strip()
    candidate = re.sub(r"[^\w\s-]", " ", candidate)
    candidate = NORMALIZE_SPACES.sub(" ", candidate).strip()

    if not candidate:
        return clean_text(title)

    candidate = re.sub(r"(?i)\b(.+?)\s+\1\b", r"\1", candidate)
    candidate = NORMALIZE_SPACES.sub(" ", candidate).strip()

    if len(candidate) > 120:
        candidate = candidate[:120].rstrip()
        if " " in candidate:
            candidate = candidate.rsplit(" ", 1)[0]
        candidate += "..."

    return candidate
