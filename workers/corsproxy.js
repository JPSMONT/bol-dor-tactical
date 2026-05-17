// ─────────────────────────────────────────────────────────────────────────────
// CORS proxy for SuiviRegate KMZ files — Cloudflare Worker
// ─────────────────────────────────────────────────────────────────────────────
//
// Purpose
//   The PWA at https://jpsmont.github.io/bol-dor-tactical/ needs to fetch
//   race-tracking KMZ archives from www.suiviregate.ch. SuiviRegate doesn't
//   serve CORS headers, so browsers block direct fetches. The app falls back
//   through public CORS proxies (corsproxy.io, allorigins.win), but those
//   will rate-limit on race day under crew + spectator load.
//
//   This Worker is a tiny, self-hosted alternative that fronts only the
//   suiviregate.ch host, adds the right CORS headers, and uses Cloudflare's
//   edge cache so identical KMZ requests don't hammer SuiviRegate.
//
// Security
//   Restricted to www.suiviregate.ch / suiviregate.ch by host allowlist.
//   This isn't an open proxy — it can only fetch from one origin we already
//   pull from. Worst-case abuse: someone uses our quota to fetch SuiviRegate
//   data they could fetch themselves via the public proxies.
//
// Deployment
//   See workers/README.md in this repo. ~5-minute setup via the Cloudflare
//   dashboard, free tier is sufficient (100k requests/day, well above any
//   conceivable race-day load).
//
// Usage from the PWA
//   GET https://corsproxy-bol-dor.<your-subdomain>.workers.dev/?url=<encoded URL>
//
//   Example:
//     fetch('https://corsproxy-bol-dor.example.workers.dev/?url=' +
//           encodeURIComponent('https://www.suiviregate.ch/sync/BOL25/kml/data.kmz'))
//
// ─────────────────────────────────────────────────────────────────────────────

const ALLOWED_HOSTS = ['www.suiviregate.ch', 'suiviregate.ch'];
const CACHE_TTL_SECONDS = 3600;  // 1 hour — fine for race-day polling cadence

export default {
  async fetch(request) {
    // ── CORS preflight ─────────────────────────────────────────────────────
    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: corsHeaders() });
    }

    // Only allow GET and HEAD — proxy is read-only
    if (request.method !== 'GET' && request.method !== 'HEAD') {
      return error(405, 'Only GET and HEAD allowed');
    }

    // ── Parse target URL from ?url= query param ────────────────────────────
    const url = new URL(request.url);
    const target = url.searchParams.get('url');
    if (!target) return error(400, 'Missing ?url= query parameter');

    let targetUrl;
    try {
      targetUrl = new URL(target);
    } catch (_e) {
      return error(400, 'Invalid target URL');
    }

    // Only http/https
    if (!['http:', 'https:'].includes(targetUrl.protocol)) {
      return error(400, 'Only http/https targets allowed');
    }

    // Host allowlist
    if (!ALLOWED_HOSTS.includes(targetUrl.hostname)) {
      return error(403, `Host not in allowlist. Allowed: ${ALLOWED_HOSTS.join(', ')}`);
    }

    // ── Try Cloudflare edge cache first ────────────────────────────────────
    const cacheKey = new Request(targetUrl.toString(), { method: 'GET' });
    const cache = caches.default;
    let response = await cache.match(cacheKey);
    let cacheStatus = 'HIT';

    if (!response) {
      // Cache miss — fetch from upstream
      cacheStatus = 'MISS';
      try {
        const upstream = await fetch(targetUrl.toString(), {
          method: request.method,
          headers: {
            'User-Agent': 'bol-dor-tactical-pwa/1.0 (+https://jpsmont.github.io/bol-dor-tactical/)',
            'Accept': '*/*'
          },
          cf: {
            cacheTtl: CACHE_TTL_SECONDS,
            cacheEverything: true
          }
        });

        // Reconstruct the response with mutable headers
        response = new Response(upstream.body, {
          status: upstream.status,
          statusText: upstream.statusText,
          headers: new Headers(upstream.headers)
        });

        // Cache successful responses for next caller
        if (upstream.ok) {
          response.headers.set('Cache-Control', `public, max-age=${CACHE_TTL_SECONDS}`);
          await cache.put(cacheKey, response.clone());
        }
      } catch (e) {
        return error(502, `Upstream fetch failed: ${e.message}`);
      }
    } else {
      // Cache hit — re-wrap so we can mutate headers
      response = new Response(response.body, response);
    }

    // ── Add CORS + diagnostic headers and return ───────────────────────────
    for (const [k, v] of Object.entries(corsHeaders())) {
      response.headers.set(k, v);
    }
    response.headers.set('X-Proxy-Cache', cacheStatus);

    return response;
  }
};

// ─── Helpers ──────────────────────────────────────────────────────────────────

function corsHeaders() {
  return {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, HEAD, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '86400'
  };
}

function error(status, message) {
  return new Response(JSON.stringify({ error: message }), {
    status,
    headers: {
      'Content-Type': 'application/json',
      ...corsHeaders()
    }
  });
}
