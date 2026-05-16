# Bol d'Or Tactical PWA

Tactical sailing companion for **Little Johnka** (CYD 27 ORC, SUI 6116) racing the **Bol d'Or Mirabaud** on Lac Léman, 6–7 June 2026. Single-file PWAs (no build step), designed for live use on phone and iPad during a 24-hour overnight race.

This is a working app, not a prototype. Eleven commits since the initial scaffolding cover the full PRD v4.0 scope plus polish.

---

## What's in the repo

| File | Purpose |
|---|---|
| `index.html` | Main PWA — 5 tabs: Dashboard, Polars, Wind, Strategy, Rivals. ~3 600 lines of inline HTML/CSS/JS. |
| `replay.html` | Standalone race-replay viewer. Leaflet + SuiviRegate KMZ + LJ ghost simulation. ~760 lines. |
| `sw.js` | Service worker — caches the shell + Open-Meteo responses for offline race-day use. |
| `manifest.json` | PWA manifest (home-screen icons, theme colour). |
| `icon-192.png` / `icon-512.png` | App icons. |
| `CLAUDE.md` | Project instructions / build order — also acts as the "README for AI assistants". |
| `docs/PRD-v4.md` | Full product requirements (May 2026 vision). The source of truth for feature scope. |
| `.gitignore` | macOS metadata + editor cruft. |
| `README.md` | This file. |

External dependencies (CDN, loaded on demand):

| Library | Used for |
|---|---|
| Leaflet 1.9.4 | Maps everywhere (Strategy tab, Rivals tab, replay) |
| JSZip 3.10.1 | KMZ extraction (Rivals tab + replay) |
| OpenSeaMap tiles | Nautical chart overlay (seamarks, buoys, lights) |

No bundler, no Node toolchain. Open `index.html` in a modern browser; it just works (modulo a few CORS/HTTPS notes below).

---

## Tab-by-tab guide (`index.html`)

### Dashboard
- Live countdown to **2026-06-06 09:00 CEST**.
- **Race-day readiness checklist** (appears once we're inside D-14). Auto-detects 5 app-readiness items (service worker, wind data, station freshness, rival KMZ cache, GPS permission) and tracks 14 manual items across Tracking phone / Tactical device / Boat + crew. Manual ticks persist in `localStorage`.
- Race-sim banner (currently a forward-looking 30-min simulation using the live forecast).
- Boat spec card (CYD 27 ORC details).
- Quick VMG calculator + current-wind summary.

### Polars
- Interactive polar diagram for all 7 ORC TWS (6, 8, 10, 12, 14, 16, 20 kn).
- VMG-targets table (Beat°, Beat VMG, Run°, Run VMG, Max kn).
- Full speed table by TWA at a chosen TWS.

### Wind
- **Race-prep phase card**: D-14 → race-day timeline with the current phase highlighted; per-phase tactical guidance from PRD §5.1. Direct link to MeteoSwiss radar.
- **MeteoSwiss live stations**: GVE / CGI / PUY / VEV / AIG / EVI, fetched every 10 min from `data.geo.admin.ch`, km/h → knots, ages flagged amber if stale.
- **Pattern read**: rule-based classifier producing one of Vaudaire / Bise / Vent / Joran / Fraidieu / Morget-Bornan / Môlan / Séchard / Calm / Mixed, with tactical commentary. Includes a **wind-shift detector** (PRD §10.1) that flags sustained shifts >10° vs the last hour.
- **48-h wind forecast** at 9 grid points × 4 models (AROME HD 1.3 km + ICON-CH1 1 km + ICON-CH2 2 km + ICON-D2 2 km), three zones (Geneva / Lausanne / Bouveret). Inter-model spread drives a confidence pill on every row.
- Static **wind pattern guide** with all PRD §11.2 thermals (Séchard, Morget, Bornan, Fraidieu, Vauderon, Môlan).

### Strategy
- **GPS Navigation** (PRD §7): live position, gold boat icon rotated by fused heading (GPS COG ≥ 3 kn; device compass otherwise — DeviceOrientation API with iOS permission flow). SOG / COG / Bearing / Distance / VMC tiles; compass rose distinguishing heading vs bearing-to-mark; **night-mode big-bearing** display (huge red digits on black); **PPR bar** (SOG vs polar target). 7-waypoint route per PRD §7.3, auto-advances at 500 m. IndexedDB track recording.
- **Race-course map** (Leaflet + OpenSeaMap on black). Lake polygon, 9-point wind grid with live mid-lake arrows, 5-waypoint route.
- **Route simulation**: synthesises a Little Johnka track from polars + a wind field. Strategy options Auto / Swiss / Mid / French. Algorithm options **Greedy VMC** (fast) and **Isochrone routing** (PRD §17 P3 — globally optimal, ~36-bucket angular pruning). Scenarios: Now (live forecast) / 2026 race day / 2025-2021 historical (KMZ rivals overlay + per-gate time-delta table). LJ ghost renders **white-with-gold-trim** so it's never confused with Pertuiset's gold rival track.
- **Bank-selection advisor**: VMG comparison across the 9 grid points + forecast-offset slider.
- **Tactical notes** card with Bol d'Or-specific reminders.

### Rivals (PRD §4)
- SuiviRegate KMZ for **BOL25 / BOPM24 / BOM23 / BOM21** (~400 boats per year, ~6 MB each), fetched with a public-CORS-proxy fallback (see *Quirks*). BOL25 auto-loads on tab open.
- **5 PRD §4.1 primary targets** highlighted by colour: Leone (red), Pertuiset (gold), Monachon (teal), Rottet (purple), Borter (blue). Tap-to-toggle visibility.
- **Sector arrival times** table: Nyon / Lausanne-out / Bouveret / Lausanne-ret / Genève-finish, with elapsed time and leader-delta per visible rival.
- **Head-to-head distance-to-Bouveret chart** (SVG): one line per rival, V-shaped around the rounding moment.
- **Bank-commitment chart**: signed cross-track distance from the GVA → BVT rhumb line. Blue band = Swiss/N, amber band = French/S.
- **Tack/gybe markers** on the map (heading-Δ > 60° in <2 min, anti-bunched).
- **Time scrubber** with Play/Pause; animates rival positions across the race window.
- **Race-day banner**: countdown / live / past states. Live button polls SuiviRegate every 60 min during the race window (stub until 2026 race code is published).
- **OSCAR link**: opens DeepRegatta's per-race page in a new tab. (DeepRegatta's "JSON API" turned out to be Firestore-backed; no programmatic integration — see `memory/deepregatta-firebase.md`.)
- **Per-rival deep dive** (PRD §10): tap "Analyse" on any target → fetches ERA5 historical wind for that year, walks the track segment-by-segment, returns avg SOG / avg PPR / point-of-sail mix / bank lean / manoeuvre count / outbound vs return VMC. Renders a PPR-over-time chart (raw + 1-h rolling mean) and a lateral-deviation trace.

---

## `replay.html`

Standalone Leaflet-based race replay. Year selector (2025 / 2024 / 2023 / 2021), play / pause / reset, 10× → 3600× speed selector, time slider with 10 000 steps. Full fleet renders as faint blue lines; the 5 PRD targets in canonical colours with skipper-name badges at the start.

**LJ ghost** option in the bottom controls: pick a strategy (Auto VMC / Swiss / Mid / French / **Isochrone**). The engine fetches ERA5 historical wind for the loaded year, runs the simulation, and overlays a white-with-gold-trim chevron synced to the same scrubber as the rival positions.

Click any animated dot for live readouts (SOG from local segment, HDG, distance + bearing to Bouveret, position, race time).

---

## Data sources

| Source | Used in | CORS | Notes |
|---|---|---|---|
| Open-Meteo forecast | Wind tab + sim (live) | ✅ open | 4 models, 9 grid points, hourly, 48-h horizon. |
| Open-Meteo archive (ERA5) | Sim historical + per-rival analysis | ✅ open | 25 km resolution. Covers any past date. |
| MeteoSwiss `data.geo.admin.ch` | Live stations + pattern read | ✅ open | GeoJSON in CH1903+ (EPSG:2056); filter by `id`. km/h → ÷ 1.852 for knots. |
| SuiviRegate KMZ | Rivals + replay | ❌ **closed** | `www.suiviregate.ch/sync/<RACE>/kml/data.kmz` returns no `Access-Control-Allow-Origin`. App falls back through `corsproxy.io` then `api.allorigins.win`. **Bring your own proxy before race day.** See `memory/suiviregate-cors.md`. |
| OpenSeaMap tiles | Every map | ✅ open | `tiles.openseamap.org/seamark/{z}/{x}/{y}.png` |
| DeepRegatta OSCAR | Link-out only | n/a | Firestore-backed SPA, no public JSON API despite PRD §8.2's claim. |

---

## Known quirks

- **CORS proxy dependency.** SuiviRegate doesn't allow direct browser fetches. The two public proxies will rate-limit eventually. Before race week, stand up a one-line Cloudflare Worker / Vercel edge function under your own domain and replace the `CORS_PROXIES` array. Memory note: `memory/suiviregate-cors.md`.
- **Two `gh` accounts.** The keyring holds `JPSMONT` (owns this private repo) and `OberseeSegelClubArth` (sailing club). Always `gh auth switch -u JPSMONT` before pushing this repo, else `git push` fails with `Repository not found` (the org account can't see the private repo). Memory note: `memory/github-repo-bol-dor.md`.
- **HTTPS required for GPS + compass.** `navigator.geolocation` works on `file://` in Safari but Chrome refuses it. DeviceOrientation's iOS `requestPermission()` requires a secure origin (`https://` or `localhost`). For real-device testing: GitHub Pages, Netlify, Vercel, or `ngrok http <port>` are all easy.
- **MeteoSwiss station list.** PRD/CLAUDE.md listed `COY` as Cointrin and `EVI` as Évian — both wrong. Actual stations: COY is *Courtelary* (Jura, irrelevant), and EVI is *Evionnaz* (Rhône valley, useful as a Vaudaire indicator). Corrected in code.
- **Service worker caches `index.html`.** During development, a hard reload (Cmd+Shift+R) or unregistering the SW in DevTools is necessary to see changes.

---

## Local development

```bash
# Clone, then serve over a local HTTP server (for SW + GPS)
python3 -m http.server 8000
open http://localhost:8000/index.html
```

That's it. No `npm install`, no build step.

For phone testing where you need HTTPS:
```bash
# pick one
npx serve -p 8000 .          # then expose with ngrok / cloudflared
gh-pages -d .                # github actions / pages
```

---

## Deploying for race day

1. Switch `gh` to the right account: `gh auth switch -u JPSMONT`.
2. Push to a hosted HTTPS surface (GitHub Pages, Cloudflare Pages, Netlify, Vercel — all free, all work for static files).
3. Install on **both phones** as a PWA:
   - iOS: open in Safari → Share → "Add to Home Screen".
   - Android: Chrome → menu → "Install app".
4. Open the app once on race-day Wi-Fi so the service worker caches everything.
5. Grant GPS + compass permissions when the GPS Navigation card asks.
6. Tick off the Dashboard readiness checklist.

---

## Race-day operational checklist

Surfaced inside the app on the Dashboard once you're inside D-14. Highlights:

- **Tracking phone** (per PRD §12.3): MySuiviRegate installed, ACVL/SRS+PIN entered, test run done, VPN/WiFi/Bluetooth disabled, battery saver OFF, battery 100% + pack aboard.
- **Tactical device** (this app): runs on a **separate** iPad or phone from the tracking one. Brightness max, auto-dim off, app loaded once on race-day Wi-Fi for SW cache, cable aboard.
- **Boat + crew**: sails, safety gear, briefed crew, emergency contacts.

---

## Architecture notes (for future you)

- **Single-file convention.** Each PWA is one HTML file with inline CSS/JS and CDN-only deps. This makes deploy trivial but means `index.html` and `replay.html` duplicate the polar table, KMZ parser, route-simulation engine, isochrone routing, and the historical-wind adapter. If duplication grows further, factor a shared `lib.js` — the convention is self-imposed and worth breaking when the duplication tax exceeds the deploy-simplicity tax. ~600 lines are currently duplicated.
- **Memory directory** (`~/.claude/projects/.../memory/`) holds reference notes that survive across sessions:
  - `github-repo-bol-dor.md` — gh account routing for push
  - `suiviregate-cors.md` — proxy fallback rationale
  - `deepregatta-firebase.md` — why we link out rather than integrate
- **Tab indexing.** `showTab(i)` switches by index: 0 Dashboard, 1 Polars, 2 Wind, 3 Strategy, 4 Rivals. Adding more tabs gets tight on a 480 px container.
- **State that persists** between sessions:
  - Track recording in IndexedDB `bol-tactic` / `fixes`
  - Race-day checklist ticks in `localStorage` (`bol_checklist_v1`)
- **State that doesn't** (intentionally):
  - Rival KMZ caches, historical wind caches, sim results — re-fetched each session
- **Simulation engine** (`simulateLJRoute` + `isochroneRoute`) is wind-source-agnostic — it takes a `(lat, lon, ts) → {tws, twd}` adapter. We currently feed either the live ensemble or the ERA5 archive; adding GRIB or a personal weather-routing service would be a one-function change.

---

## Open backlog

All the PRD §17 P1 items are shipped. Remaining low-priority items:

- **Live SuiviRegate polling**: stubbed in the Rivals tab; activates during the 6–7 June 2026 race window. Will need the actual 2026 race code once SuiviRegate publishes it (replace the current "re-fetch loaded year as stand-in" with the real code).
- **Post-race performance dashboard for LJ's own track**: once you have a SuiviRegate KMZ of your actual race, you can re-use `computeRivalAnalysis()` directly by mapping LJ as a "target". No UI exists for that yet.
- **Self-hosted CORS proxy**: described above. ~20 lines of Cloudflare Worker code.

---

## Credit & licence

Built collaboratively by Joao Pinto da Silva (skipper, Little Johnka, SUI 6116) and Claude (Anthropic). PWA scope per `docs/PRD-v4.md`. Polars from the boat's ORC certificate. Wind data © Open-Meteo / Météo-France / MeteoSwiss / DWD. Tracks © SuiviRegate. Nautical overlay © OpenSeaMap (CC-BY-SA).

Private repo at `github.com/JPSMONT/bol-dor-tactical`.

Good luck on June 6th. May the Bise hold.
