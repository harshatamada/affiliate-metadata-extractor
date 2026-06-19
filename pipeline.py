import subprocess
import json

from main import run_extraction

from ai.seo import (
    generate_seo_title,
    generate_meta_description
)

from ai.summary import (
    generate_product_summary
)

from ai.categorizer import (
    process_product
)

affiliate_url = input("Enter affiliate URL: ")

# -----------------------------
# STEP 1: Resolve URL
# -----------------------------
resolver_output = subprocess.check_output(
    ["node", "resolver/resolver.js", affiliate_url],
    text=True
)

resolver_data = json.loads(resolver_output)

# -----------------------------
# STEP 2: Extract Product Data
# -----------------------------
product = run_extraction({
    "normalizedUrl": resolver_data["normalizedUrl"]
})

if not product:
    print("Extraction failed")
    exit()

# -----------------------------
# STEP 3: SEO
# -----------------------------
seo_title = generate_seo_title(product)

meta_description = generate_meta_description(product)

# -----------------------------
# STEP 4: Summary
# -----------------------------
summary_data = generate_product_summary(product)

# -----------------------------
# STEP 5: Category / Tags
# -----------------------------
category_data = process_product(product)

# -----------------------------
# STEP 6: Final Output
# -----------------------------
final_output = {

    # Resolver
    "original_url": resolver_data.get("originalUrl"),
    "normalized_url": resolver_data.get("normalizedUrl"),
    "platform": resolver_data.get("platform"),

    # Extraction
    "product_name": product.get("product_name"),
    "description": product.get("description"),
    "image": product.get("image"),
    "brand": product.get("brand"),
    "product_type": product.get("product_type"),
    "price": product.get("price"),

    # Summary
    "summary": summary_data.get("summary"),
    "highlights": summary_data.get("highlights"),

    # SEO
    "seo_title": seo_title,
    "meta_description": meta_description,

    # Categorization
    "category": category_data.get("category"),
    "subcategory": category_data.get("subcategory"),
    "tags": category_data.get("tags"),
    "keywords": category_data.get("keywords")
}

print(json.dumps(final_output, indent=2, ensure_ascii=False))