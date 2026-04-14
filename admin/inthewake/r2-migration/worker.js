/**
 * InTheWake R2 Image Worker
 *
 * Intercepts image-path requests to cruisinginthewake.com and serves them
 * from the Cloudflare R2 bucket `inthewake-media` with aggressive caching.
 * All other paths pass through to the origin (GitHub Pages).
 *
 * Deploy: wrangler deploy
 *
 * Soli Deo Gloria.
 */

const R2_IMAGE_PREFIXES = [
  '/assets/ships/',
  '/ports/img/',
  '/assets/social/',
  '/assets/images/',
  '/assets/venues/',
  '/assets/articles/',
  '/assets/brand/',
  '/assets/icons/',
  '/assets/img/',
  '/authors/img/',
  '/authors/ico/',
  '/authors/tinas-images/',
  '/solo/images/',
  '/images/',
];

const IMAGE_CACHE_CONTROL = 'public, max-age=31536000, immutable';

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;

    // Determine if this request should be served from R2
    const shouldServeFromR2 = R2_IMAGE_PREFIXES.some((prefix) =>
      path.startsWith(prefix),
    );

    if (!shouldServeFromR2) {
      // Pass through to origin (GitHub Pages)
      return fetch(request);
    }

    // Strip leading slash for R2 object key
    const objectKey = path.slice(1);

    // Check Cloudflare edge cache first
    const cacheKey = new Request(url.toString(), request);
    const cache = caches.default;
    let response = await cache.match(cacheKey);
    if (response) {
      return response;
    }

    // Fetch from R2
    const object = await env.MEDIA_BUCKET.get(objectKey);

    if (!object) {
      // Image not in R2 — fall back to origin to surface 404 naturally
      return fetch(request);
    }

    // Build response with proper headers
    const headers = new Headers();
    object.writeHttpMetadata(headers);
    headers.set('etag', object.httpEtag);
    headers.set('cache-control', IMAGE_CACHE_CONTROL);

    // Set content-type explicitly if not set by R2 metadata
    if (!headers.has('content-type')) {
      headers.set('content-type', guessContentType(objectKey));
    }

    response = new Response(object.body, { headers });

    // Cache at the edge
    ctx.waitUntil(cache.put(cacheKey, response.clone()));

    return response;
  },
};

function guessContentType(path) {
  const ext = path.split('.').pop().toLowerCase();
  const types = {
    webp: 'image/webp',
    jpg: 'image/jpeg',
    jpeg: 'image/jpeg',
    png: 'image/png',
    svg: 'image/svg+xml',
    ico: 'image/x-icon',
    gif: 'image/gif',
  };
  return types[ext] || 'application/octet-stream';
}
