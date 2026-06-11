# Affiliate Metadata Extractor

Extract structured product information from e-commerce URLs.

## Features

- Amazon support
- Flipkart support
- Myntra support
- JSON-LD extraction
- OpenGraph extraction
- Metadata extraction
- Product image extraction
- Brand extraction

## Output

```json
{
  "product_name": "...",
  "description": "...",
  "image": "...",
  "brand": "...",
  "source": "jsonld"
}
## Installation

pip install -r requirements.txt
playwright install

## Run
python main.py
