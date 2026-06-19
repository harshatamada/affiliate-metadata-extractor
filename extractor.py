from parsers.jsonld_parser import parse_jsonld
from parsers.metadata_parser import parse_metadata


def extract_product_data(html):

    jsonld = parse_jsonld(html)

    if jsonld:

        return {
            "product_name": jsonld.get("name"),
            "description": jsonld.get("description"),
            "image": jsonld.get("image"),
            "brand": jsonld.get("brand"),
            "price": jsonld.get("price"),
            "product_type": jsonld.get("@type"),
            "source": "jsonld"
        }

    metadata = parse_metadata(html)

    return {
     "product_name": metadata.get("product_name"),
     "description": metadata.get("description"),
     "image": metadata.get("image"),
     "brand": metadata.get("brand"),
     "price": metadata.get("price"),
     "product_type": metadata.get("product_type"),
     "source": "metadata"
}