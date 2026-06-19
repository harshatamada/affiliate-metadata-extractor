# Affiliate Metadata Extractor

A pipeline that converts affiliate/product URLs into structured SEO-ready JSON.

## Features

* Affiliate URL Resolution
* URL Normalization
* Amazon Support
* Flipkart Support
* HTTPX Fetching
* Playwright Fallback
* Product Metadata Extraction
* Price Extraction
* SEO Title Generation
* Meta Description Generation
* Category & Subcategory Detection
* Tags & Keywords Generation
* AI Product Summary Generation

---

# Project Flow

```text
Affiliate URL
      ↓
URL Resolver (Node.js)
      ↓
Normalized Product URL
      ↓
HTML Fetching
      ↓
Metadata Extraction
      ↓
SEO Generation
      ↓
Structured JSON Output
```

---

# Folder Structure

```text
project/
│
├── ai/
│   ├── seo.py
│   ├── summary.py
│   ├── categorizer.py
│   └── text_utils.py
│
├── fetchers/
│   ├── httpx_fetcher.py
│   └── playwright_fetcher.py
│
├── parsers/
│   ├── jsonld_parser.py
│   └── metadata_parser.py
│
├── resolver/
│   ├── resolver.js
│   ├── package.json
│   └── node_modules/
│
├── extractor.py
├── main.py
├── pipeline.py
├── requirements.txt
└── README.md
```

---

# Requirements

## Python

Python 3.9+

Verify:

```bash
python --version
```

---

## Node.js

Node.js 18+

Verify:

```bash
node -v
npm -v
```

---

# Installation

## Clone Repository

```bash
git clone <repository-url>
cd affiliate-metadata-extractor
```

---

## Create Virtual Environment

Mac/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows

```bash
python -m venv venv
venv\Scripts\activate
```

---

## Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

## Install Node Dependencies

```bash
cd resolver

npm install

npx playwright install

cd ..
```

---

# Running the Project

Execute:

```bash
python pipeline.py
```

Example:

```text
Enter affiliate URL:
https://dl.flipkart.com/dl/...
```

---

# Example Output

```json
{
  "original_url": "...",
  "normalized_url": "...",
  "platform": "Flipkart",

  "product_name": "HP 15 Laptop",
  "price": "₹73,919",
  "brand": "HP",

  "image": "...",

  "summary": "...",

  "seo_title": "...",

  "meta_description": "...",

  "category": "Electronics",
  "subcategory": "Laptop",

  "tags": [
    "hp",
    "intel",
    "laptop"
  ],

  "keywords": [
    "hp",
    "intel",
    "windows",
    "laptop"
  ]
}
```

---

# Supported Platforms

Currently tested on:

* Amazon
* Flipkart

Future Support:

* Myntra
* Ajio
* Meesho
* Shopify Stores
* WooCommerce Stores

---

# Troubleshooting

## Playwright Browser Missing

Run:

```bash
npx playwright install
```

---

## Node Not Found

Install Node.js and verify:

```bash
node -v
npm -v
```

---

## Python Module Not Found

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Future Improvements

* Database Integration
* Human Review Workflow
* Multi-platform Price Extraction
* Better Category Detection
* LLM-based SEO Content Generation
* Product Specification Extraction
* Bulk URL Processing

---
