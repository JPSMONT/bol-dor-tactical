# Cloudflare Worker — CORS proxy for SuiviRegate

This Worker fronts `www.suiviregate.ch` so the PWA can fetch race-tracking KMZ files without hitting public CORS proxies that rate-limit. Free tier is fine — Cloudflare allows 100,000 requests/day on the free plan, well above any conceivable race-day load.

## What you're deploying

`corsproxy.js` — ~120 lines, one fetch handler, no dependencies. The Worker:

- Accepts `GET ?url=<encoded URL>` requests
- Allows ONLY `www.suiviregate.ch` / `suiviregate.ch` as fetch targets (host allowlist)
- Adds `Access-Control-Allow-Origin: *` headers so browsers accept the response
- Caches at Cloudflare's edge for 1 hour to reduce load on SuiviRegate

## Deployment via Cloudflare dashboard (recommended — 5 minutes)

This path doesn't require Node.js, npm, or wrangler. Use the web UI.

### Step 1 — Cloudflare account

1. Sign up at https://dash.cloudflare.com/sign-up (free, no credit card)
2. Confirm your email

### Step 2 — Create the Worker

1. From the Cloudflare dashboard sidebar, click **Workers & Pages**
2. Click **Create application** → **Create Worker**
3. Name it `corsproxy-bol-dor` (or anything you prefer — note the full URL it gives you)
4. Click **Deploy** to create the placeholder
5. Click **Edit code** on the freshly-deployed Worker

### Step 3 — Paste the Worker code

1. In the editor, delete the placeholder code completely
2. Open `workers/corsproxy.js` from this repo, copy the entire file
3. Paste into the Cloudflare editor
4. Click **Save and deploy**

### Step 4 — Test the deployed Worker

Open this URL in a browser (replace `<your-subdomain>` with your Cloudflare workers.dev subdomain — it's shown at the top of the Worker page):

```
https://corsproxy-bol-dor.<your-subdomain>.workers.dev/?url=https%3A%2F%2Fwww.suiviregate.ch%2Fsync%2FBOL25%2Fkml%2Fdata.kmz
```

Expected behaviour: a ~6 MB KMZ file downloads. Open the file in DevTools Network panel — you should see `Access-Control-Allow-Origin: *` in the response headers, and `X-Proxy-Cache: MISS` on first call / `HIT` on subsequent calls.

Negative test — disallowed host should 403:

```
https://corsproxy-bol-dor.<your-subdomain>.workers.dev/?url=https%3A%2F%2Fwww.google.com
```

Expected: `403 Forbidden` with JSON body `{"error": "Host not in allowlist..."}`.

### Step 5 — Wire into the PWA

Edit `index.html`. Find the `CORS_PROXIES` array (around line 3058):

```javascript
var CORS_PROXIES = [
  function(u){ return 'https://corsproxy.io/?' + encodeURIComponent(u); },
  function(u){ return 'https://api.allorigins.win/raw?url=' + encodeURIComponent(u); }
];
```

Replace with:

```javascript
var CORS_PROXIES = [
  // Self-hosted Cloudflare Worker — primary, no rate limits
  function(u){ return 'https://corsproxy-bol-dor.<your-subdomain>.workers.dev/?url=' + encodeURIComponent(u); },
  // Public fallbacks — kept in case the Worker is down
  function(u){ return 'https://corsproxy.io/?' + encodeURIComponent(u); },
  function(u){ return 'https://api.allorigins.win/raw?url=' + encodeURIComponent(u); }
];
```

Substitute your actual workers.dev URL.

### Step 6 — Verify the Rivals tab works

1. Commit the `index.html` change and push to `main`
2. Wait 1-2 minutes for GitHub Pages to redeploy
3. Open https://jpsmont.github.io/bol-dor-tactical/ on your phone (hard refresh)
4. Go to the Rivals tab — it should auto-load BOL25
5. In Cloudflare dashboard → Workers & Pages → your Worker → **Metrics**, you should see request count climbing as KMZ fetches go through
6. Try the year selector buttons (2024, 2023, 2021). All four should load via the Worker

## Alternative deployment via Wrangler CLI

If you prefer the CLI:

```bash
npm install -g wrangler
wrangler login        # opens browser for Cloudflare auth

# In the workers/ directory:
wrangler init --yes --no-deploy
# When prompted, choose JavaScript and accept defaults

# Replace the auto-generated worker source with corsproxy.js
cp corsproxy.js src/index.js

# Deploy
wrangler deploy
```

The URL is printed at the end of the deploy.

## Operational notes

### Cache TTL

`CACHE_TTL_SECONDS = 3600` (1 hour) at the top of the Worker. KMZ files for past races (BOL25, BOPM24, etc.) are static — they never change after the race finishes. The 1-hour cache is mostly for race-day live polling cadence. If you want longer cache for past races, increase to `86400` (24 h) or even `604800` (1 week).

### Allowlist

`ALLOWED_HOSTS` only lets the Worker fetch from suiviregate.ch. If you ever need to proxy a different host (e.g., a new race-tracking system), add it to the array and redeploy.

### Monitoring

Cloudflare dashboard → Workers & Pages → your Worker → **Logs** (real-time) or **Metrics** (graphs).

Free-tier limits:
- 100,000 requests/day
- 10 ms CPU time per request

A Bol d'Or race day with a small crew is likely under 1,000 requests total. Free tier is comfortable.

### Rolling back

If something goes wrong with the Worker, the PWA still has the two public proxies as fallbacks (corsproxy.io and allorigins.win). The Rivals tab will degrade gracefully and slow down rather than fail.

## File inventory

- `corsproxy.js` — the Worker source code
- `README.md` — this file
