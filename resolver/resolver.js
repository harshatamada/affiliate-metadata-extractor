const axios = require('axios');
const { URL, URLSearchParams } = require('url');

const USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36';
const MAX_REDIRECTS = 10;
const HTTP_TIMEOUT = 10000;
const BROWSER_TIMEOUT = 15000;
const COMMON_TRACKING_PARAMS = [
  'fbclid',
  'gclid',
  'aff_id',
  'affiliate_id',
  'tag',
  'ref',
];
const PRESERVE_QUERY_KEYS = ['pid', 'sku', 'productid', 'asin'];

function log() {}

function normalizeUrl(urlString) {
  try {
    const url = new URL(urlString);
    const params = new URLSearchParams(url.search);
    for (const key of Array.from(params.keys())) {
      const lower = key.toLowerCase();
      if (lower.startsWith('utm_') || lower.startsWith('ref_') || COMMON_TRACKING_PARAMS.includes(lower)) {
        if (!PRESERVE_QUERY_KEYS.includes(lower)) {
          params.delete(key);
        }
      }
    }
    url.search = params.toString();
    url.hash = '';
    let normalized = url.toString();
    if (isAmazonUrl(normalized)) {
      const asin = extractAmazonASIN(normalized);
      if (asin) {
        normalized = `https://${url.host}/dp/${asin}`;
      }
    }
    return normalized;
  } catch (error) {
    log('normalizeUrl error', error.message);
    return urlString;
  }
}

function isAmazonUrl(urlString) {
  try {
    const host = new URL(urlString).host.toLowerCase();
    return host.includes('amazon.');
  } catch {
    return false;
  }
}

function extractAmazonASIN(urlString) {
  try {
    const url = new URL(urlString);
    const path = url.pathname;
    const patterns = [
      /\/dp\/([A-Z0-9]{10})(?:[/?]|$)/i,
      /\/gp\/product\/([A-Z0-9]{10})(?:[/?]|$)/i,
      /\/gp\/aw\/d\/([A-Z0-9]{10})(?:[/?]|$)/i,
      /\/product\/([A-Z0-9]{10})(?:[/?]|$)/i,
    ];
    for (const pattern of patterns) {
      const match = path.match(pattern);
      if (match && match[1]) {
        return match[1].toUpperCase();
      }
    }
    const search = url.searchParams;
    const asin = search.get('ASIN') || search.get('asin');
    return asin ? asin.toUpperCase() : null;
  } catch {
    return null;
  }
}

function detectPlatform(urlString, html = '') {
  try {
    const host = new URL(urlString).host.toLowerCase();
    if (host.includes('amazon.')) return 'Amazon';
    if (host.includes('flipkart.')) return 'Flipkart';
    if (host.includes('myntra.')) return 'Myntra';
    if (host.includes('ajio.')) return 'Ajio';
    if (host.includes('meesho.')) return 'Meesho';
    if (host.endsWith('myshopify.com') || html.includes('cdn.shopify.com')) return 'Shopify';
    if (html.includes('woocommerce') || host.includes('wp-content') || host.includes('woocommerce')) return 'WooCommerce';
    if (html.includes('product') || html.includes('add-to-cart')) return 'Generic ecommerce';
    return 'Unknown';
  } catch {
    return 'Unknown';
  }
}

function extractProductId(urlString) {
  try {
    const url = new URL(urlString);
    const search = url.searchParams;
    for (const key of ['pid', 'sku', 'productid', 'ASIN', 'asin']) {
      if (search.has(key)) {
        return search.get(key);
      }
    }
    if (isAmazonUrl(urlString)) {
      return extractAmazonASIN(urlString) || '';
    }
    const path = url.pathname;
    const match = path.match(/\/(?:product|products|p|item)\/(\w+)/i);
    return match ? match[1] : '';
  } catch {
    return '';
  }
}

function extractCanonical(urlString, html) {
  const base = (() => {
    try {
      return new URL(urlString);
    } catch {
      return null;
    }
  })();
  const canonicalMatch = html.match(/<link[^>]+rel=["']canonical["'][^>]*>/i);
  if (canonicalMatch) {
    const hrefMatch = canonicalMatch[0].match(/href=["']([^"']+)["']/i);
    if (hrefMatch && hrefMatch[1]) {
      try {
        return new URL(hrefMatch[1], base).toString();
      } catch {
        return hrefMatch[1];
      }
    }
  }
  const ogMatch = html.match(/<meta[^>]+property=["']og:url["'][^>]*>/i) || html.match(/<meta[^>]+name=["']og:url["'][^>]*>/i);
  if (ogMatch) {
    const contentMatch = ogMatch[0].match(/content=["']([^"']+)["']/i);
    if (contentMatch && contentMatch[1]) {
      try {
        return new URL(contentMatch[1], base).toString();
      } catch {
        return contentMatch[1];
      }
    }
  }
  return '';
}

function detectJavaScriptRedirect(html) {
  if (!html) return false;
  const patterns = [
    /window\.location(?:\.href)?\s*=\s*['"][^'"]+['"]/i,
    /location\.href\s*=\s*['"][^'"]+['"]/i,
    /location\.replace\(/i,
    /<meta[^>]+http-equiv=["']refresh["'][^>]*>/i,
    /window\.location\.replace\(/i,
  ];
  return patterns.some((pattern) => pattern.test(html));
}

async function requestWithRetry(url, options = {}) {
  const maxAttempts = 2;
  let lastError = null;
  for (let attempt = 0; attempt <= maxAttempts; attempt += 1) {
    try {
      return await axios({
        url,
        method: 'get',
        headers: { 'User-Agent': USER_AGENT, Accept: 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' },
        timeout: HTTP_TIMEOUT,
        maxRedirects: 0,
        validateStatus: (status) => status >= 200 && status < 600,
        responseType: 'text',
        ...options,
      });
    } catch (error) {
      lastError = error;
      if (attempt === maxAttempts || !error.code || ['ECONNRESET', 'ETIMEDOUT', 'EAI_AGAIN', 'ENOTFOUND'].indexOf(error.code) === -1) {
        throw error;
      }
      log('retry', attempt + 1, url, error.code);
    }
  }
  throw lastError;
}

async function httpResolve(startUrl) {
  const chain = [startUrl];
  let currentUrl = startUrl;
  let lastResponse = null;
  let html = '';

  for (let redirectCount = 0; redirectCount < MAX_REDIRECTS; redirectCount += 1) {
    const response = await requestWithRetry(currentUrl);
    lastResponse = response;
    const status = response.status;
    const location = response.headers.location;
    html = typeof response.data === 'string' ? response.data : '';

    if (status >= 300 && status < 400 && location) {
      let nextUrl;
      try {
        nextUrl = new URL(location, currentUrl).toString();
      } catch {
        nextUrl = location;
      }
      chain.push(nextUrl);
      currentUrl = nextUrl;
      continue;
    }
    break;
  }

  if (!lastResponse) {
    throw new Error('Unable to resolve URL');
  }

  return {
    finalUrl: currentUrl,
    redirectChain: chain,
    html,
    needsBrowser: detectJavaScriptRedirect(html) && lastResponse.status === 200,
  };
}

async function browserResolve(url) {
  let playwright;
  try {
    playwright = require('playwright');
  } catch (error) {
    throw new Error('Playwright not installed; browser fallback unavailable');
  }

  const chain = [url];
  const browser = await playwright.chromium.launch({ headless: true });
  const context = await browser.newContext({ userAgent: USER_AGENT });
  const page = await context.newPage();
  page.on('framenavigated', (frame) => {
    if (frame === page.mainFrame()) {
      const current = frame.url();
      if (chain[chain.length - 1] !== current) {
        chain.push(current);
      }
    }
  });

  try {
    await page.goto(url, { timeout: BROWSER_TIMEOUT, waitUntil: 'domcontentloaded' });
    try {
      await page.waitForNavigation({ timeout: 8000, waitUntil: 'domcontentloaded' });
    } catch {
      // ignore no navigation event
    }
    const finalUrl = page.url();
    return { finalUrl, redirectChain: chain, html: await page.content() };
  } finally {
    await browser.close();
  }
}

async function fetchHtml(url) {
  const response = await requestWithRetry(url);
  return typeof response.data === 'string' ? response.data : '';
}

function validateUrl(input) {
  if (!input || typeof input !== 'string') {
    throw new Error('URL is required');
  }
  try {
    return new URL(input.trim()).toString();
  } catch (error) {
    throw new Error('Invalid URL');
  }
}

async function resolveUrl(originalUrl) {
  const output = {
   success: false,
    originalUrl: originalUrl || '',
    resolvedUrl: '',
    canonicalUrl: '',
    normalizedUrl: '',
    platform: '',
    redirectChain: [],
    productId: '',
    errors: [],
  };

  try {
    const validated = validateUrl(originalUrl);
    output.originalUrl = validated;
    const httpResult = await httpResolve(validated);
    output.redirectChain = httpResult.redirectChain;
    let finalUrl = httpResult.finalUrl;
    let html = httpResult.html;

    if (httpResult.needsBrowser) {
      log('JavaScript redirect detected; falling back to Playwright');
      const browserResult = await browserResolve(finalUrl);
      output.redirectChain = [...new Set([...output.redirectChain, ...browserResult.redirectChain])];
      finalUrl = browserResult.finalUrl;
      html = browserResult.html;
    }

    const canonicalAddress = extractCanonical(finalUrl, html);
    if (canonicalAddress) {
      output.canonicalUrl = canonicalAddress;
      finalUrl = canonicalAddress;
    } else {
      output.canonicalUrl = finalUrl;
    }

    output.resolvedUrl = finalUrl;
    output.normalizedUrl = normalizeUrl(finalUrl);
    output.platform = detectPlatform(finalUrl, html);
    output.productId = extractProductId(finalUrl);
    output.success = true;
  } catch (error) {
    output.errors.push(error.message || String(error));
    log('resolveUrl error', error);
  }

 return output;
}

if (require.main === module) {
  const inputUrl = process.argv[2];
resolveUrl(inputUrl)
  .then((result) => {

   process.stdout.write(
  JSON.stringify(result, null, 2)
);

  })
    .catch((error) => {
      process.stdout.write(JSON.stringify({ success: false, errors: [error.message || String(error)] }, null, 2));
    });
}

module.exports = { resolveUrl, normalizeUrl, extractProductId, detectPlatform };