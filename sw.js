// Bol d'Or Tactical — service worker
// Offline strategy:
//   • shell + pinned Leaflet/JSZip  → precached (cache-first)
//   • Open-Meteo + MeteoSwiss data  → network-first, fall back to last-known
//   • map tiles (OpenSeaMap, CARTO) → cache-first into a capped tile cache
//     (load the map over the race area while online so tiles are there offline)
const CACHE = 'bol-tactic-v11';
const TILES = 'bol-tiles-v1';
const TILE_MAX = 800;

const SHELL = [
  './index.html', './replay.html', './manifest.json',
  './icon-192.png', './icon-512.png',
  './apple-touch-icon.png', './favicon-32.png', './favicon-16.png'
];
const LIBS = [
  'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',
  'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js',
  'https://unpkg.com/jszip@3.10.1/dist/jszip.min.js'
];

self.addEventListener('install', e => {
  e.waitUntil((async () => {
    const c = await caches.open(CACHE);
    await c.addAll(SHELL);                                // same-origin, reliable
    await Promise.allSettled(LIBS.map(async u => {        // CDN libs, best-effort
      try { const r = await fetch(u, { mode: 'cors' }); if (r && r.ok) await c.put(u, r); } catch (err) {}
    }));
  })());
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter(k => k !== CACHE && k !== TILES).map(k => caches.delete(k)));
    await self.clients.claim();
  })());
});

const isData = u => u.includes('open-meteo.com') || u.includes('data.geo.admin.ch');
const isTile = u => u.includes('tiles.openseamap.org') || u.includes('basemaps.cartocdn.com');
const isLib  = u => u.includes('unpkg.com');

async function trimTiles() {
  try {
    const c = await caches.open(TILES);
    const keys = await c.keys();
    for (let i = 0; i < keys.length - TILE_MAX; i++) await c.delete(keys[i]);
  } catch (err) {}
}

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = req.url;

  // Live data — network-first, last-known fallback
  if (isData(url)) {
    e.respondWith((async () => {
      try {
        const r = await fetch(req);
        const c = await caches.open(CACHE);
        c.put(req, r.clone());
        return r;
      } catch (err) {
        return (await caches.match(req)) || Response.error();
      }
    })());
    return;
  }

  // Map tiles — cache-first, background revalidate, capped
  if (isTile(url)) {
    e.respondWith((async () => {
      const c = await caches.open(TILES);
      const cached = await c.match(req);
      const net = fetch(req).then(r => {
        if (r && (r.ok || r.type === 'opaque')) { c.put(req, r.clone()); trimTiles(); }
        return r;
      }).catch(() => null);
      return cached || (await net) || Response.error();
    })());
    return;
  }

  // CDN libs — cache-first, fill on miss
  if (isLib(url)) {
    e.respondWith((async () => {
      const cached = await caches.match(req);
      if (cached) return cached;
      try { const r = await fetch(req); const c = await caches.open(CACHE); c.put(req, r.clone()); return r; }
      catch (err) { return Response.error(); }
    })());
    return;
  }

  // App shell / everything else — cache-first
  e.respondWith(caches.match(req).then(r => r || fetch(req)));
});
