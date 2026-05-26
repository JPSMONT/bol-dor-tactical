# Bol d'Or Tactical PWA — Project Instructions

## Project Overview

Tactical sailing PWA for **Little Johnka** (CYD 27 ORC, SUI 6116) racing the Bol d'Or Mirabaud on Lac Léman. The race is a ~123 km (~66 NM) round trip: starts 10:00 Saturday from Genève, rounds Le Bouveret (Haut-Lac) and returns to finish at Genève. Duration: ~18-24 hours including overnight sailing.

**Owner:** Joao Monteiro (joao@pinto.ventures)
**Club:** OSCA (Obersee Segel Club Arth)
**Crew:** 2 core + occasional guests

## Boat Data — Little Johnka CYD 27 ORC

```
LOA: 8.25m | Displacement: 1,780 kg | Yardstick: 94 | TCF: 1.029
Sails: Main 27.1 m², Jib 17.7 m², Spinnaker 47.2 m²
NO Drifter. NO Code 0. Only three sails.
```

### ORC Polar Data (BTV in knots)

```javascript
var P = {
  6:  {beatA:42, beatVMG:3.52, runA:144, runVMG:3.57, twa:[42,52,60,70,75,80,90,110,120,135,150,165,180], btv:[4.74,5.32,5.60,5.78,5.81,5.82,5.77,5.65,5.48,4.92,4.09,3.43,3.22]},
  8:  {beatA:40.5, beatVMG:4.08, runA:149, runVMG:4.49, twa:[40.5,52,60,70,75,80,90,110,120,135,150,165,180], btv:[5.36,6.03,6.26,6.40,6.43,6.45,6.44,6.50,6.41,6.01,5.19,4.46,4.22]},
  10: {beatA:39.8, beatVMG:4.26, runA:154, runVMG:5.30, twa:[39.8,52,60,70,75,80,90,110,120,135,150,165,180], btv:[5.54,6.21,6.42,6.60,6.67,6.73,6.79,6.89,6.89,6.60,6.09,5.38,5.13]},
  12: {beatA:40.1, beatVMG:4.31, runA:168, runVMG:5.96},
  14: {beatA:40.1, beatVMG:4.39, runA:180, runVMG:6.51},
  16: {beatA:40.5, beatVMG:4.40, runA:180, runVMG:6.92},
  20: {beatA:42.4, beatVMG:4.25, runA:180, runVMG:7.88}
};
```

## Current State (updated 24 May 2026)

The app at `https://jpsmont.github.io/bol-dor-tactical/` is feature-complete against PRD v4 scope, plus most of QA round 2. Authoritative status lives in `docs/QA-fix-round2.md`; this section is a snapshot for fast orientation.

### Shipped features by tab

- **Dashboard** — **mode-aware Race cockpit** at the top (PRD v6 Phase 0: glanceable tiles — nav, polar-efficiency, wind state, tactical bias, data-source tagged) with an **in-race maneuver-loss tracker** (Phase 1.5: race-scoped start/finish auto-arm + trim, GPS tack/gybe loss in boat-lengths, running polar %, persisted for Debrief) and a post-race **Debrief card** (Phase 2 v1: summary, polar-% trend, maneuver table), race countdown with 4-state transition (pre-race / race-morning / live elapsed clock / post-finish), race-day readiness checklist (tool/device only — boat & crew items removed), Race Sim banner, Quick VMG calculator, current-wind summary
- **Polars** — ORC Speed Guide style polar diagram (AWA + TWA halves), single-TWS selector, wheel/pinch zoom + pan, dual Jib (blue) / Spinnaker (green) curves from split P_JIB / P_SYM tables, VMG-targets table, full speed table, plus a **Tuning Log card** (PRD v6 Phase 1.6) — one-tap snapshot of the 8 trim controls (backstay / jib car / outhaul / cunningham / vang / traveller / halyard main / halyard jib) + sail toggle + note, auto-stamped with TWS/TWA/TWD/SOG/polar%, "Best by wind band" stripe (close-hauled), recent-entries table (filter by wind band & point-of-sail), CSV export joinable to GPS track by `t_ms`, persisted to `tuning_log_v1` localStorage, Advisor read-only
- **Wind** — Race-prep phase card (D-14 → race-day), 6-station MeteoSwiss live observations (GVE/CGI/PUY/VEV/AIG/EVI), Current Wind Pattern classifier (Bise/Vent/Vaudaire/Joran/Séchard/Morget-Bornan/Môlan/Calm/Mixed), wind-shift detector, 48 h forecast at 9 grid points × 4 models (AROME HD + ICON-CH1 + ICON-CH2 + ICON-D2), **pattern timeline strip** colour-coding the predicted pattern per hour across 3 zones with race-window highlight, ASLeman wind reference guide, working MeteoSwiss radar link
- **Strategy** — GPS Navigation (enable/CSV/center/night), compass-fused heading, PPR bar, 7-waypoint route with 500 m auto-advance, IndexedDB track recording, Leaflet + OpenSeaMap map with lake polygon and 9-point wind grid arrows, **Wind Calibration Mode** (modal form, 60-min decay, "calibrated" badge), Bank selection advisor with forecast-offset slider, Route simulation (Auto/Swiss/Mid/French × Greedy-VMC/Isochrone × Now/Race-day/2025-2021 historical) with **variable `perfFactor(twa)`** 0.90/0.75/0.90 and **tack-thrashing fix** (5-min min interval, 5° VMG hysteresis), tactical notes
- **Rivals** — SuiviRegate KMZ for 4 archive years (auto-loads BOL25), 5 primary targets colour-highlighted (Leone/Pertuiset/Monachon/Rottet/Borter), tap-to-toggle visibility, sector arrival times table with `+X min` deltas, head-to-head distance-to-Bouveret SVG chart, bank-commitment chart, tack/gybe markers on map, time scrubber with Play/Pause, race-day banner (countdown/live/past), OSCAR link, per-rival "Analyse" deep dive (PPR, manoeuvre count, point-of-sail mix, outbound vs return VMC)
- **replay.html** — standalone Leaflet replay viewer with year selector, 10×–3600× playback, full fleet + 5 target highlights, LJ ghost (Auto VMC/Swiss/Mid/French/Isochrone), click-for-info on any boat

### Cross-cutting infrastructure

- **PWA install** — service worker (cache versioned — currently v15) caches the shell + pinned Leaflet/JSZip + Open-Meteo + MeteoSwiss responses, and map tiles (OpenSeaMap/CARTO) in a capped runtime cache, for offline race-day use; manifest with Little Johnka custom favicon and home-screen icons (192/512/apple-touch)
- **Self-hosted CORS proxy** — Cloudflare Worker at `https://corsproxy-bol-dor.jpsmont.workers.dev` fronts SuiviRegate KMZ fetches with host-allowlist and 1 h edge cache; replaces public proxy fallbacks (kept as second/third entries in `CORS_PROXIES` arrays in both `index.html` and `replay.html`); source at `workers/corsproxy.js`
- **Day / Night theme toggle** (Day = high-contrast light for bright daylight on water, Night = original dark; persisted in `theme_v1` localStorage, applied pre-render so no flash); responsive at 600 / 700 / 900 / 1000 px breakpoints (tablet pass: `.app` 480 → 880 px ≥700, 1120 px ≥1000; cockpit tile values up to 48 px, countdown big up to 64 px, all card-titles / tabs / labels scaled for arm's-length reading from the helm)
- **Per-device role** — Primary (default) vs **Advisor** (read-only for race state: race controls hidden, the cockpit Enable-GPS button hidden, `sampleRacePerf()` early-returns so no maneuver/perf accumulation, visible Advisor badge). Pill toggle stacks above the venue pill; persists in `localStorage` (`device_role_v1`). For multi-device race-day setups where only one device should own the race log.

### What's outstanding

- **Live SuiviRegate race-day polling** — hourly KMZ fetch during race to show competitor positions. Parser and CORS proxy exist; needs polling loop and race-day display integration.
- **Live Instruments mode** (P2) — depends on YDVR-04 install at the yard (scheduled week of 22–26 May 2026). Reads NMEA 2000 over WiFi.
- **Trim Coach upgrade to live data + True PPR via BSP** (P2) — depend on Live Instruments mode. Stub hook `isLiveInstrumentsActive()` already in Trim Coach code.
- **On-water field test** — target T5 dry run 30 May on Lac Léman.

### Venues (multi-lake)

The app supports two venues behind a flag — the Bol d'Or default is unchanged; a Zugersee profile drives the dry run.

- **Activate Zugersee:** `?venue=zugersee` or the venue pill (bottom-right). Persists in `localStorage` (`venue_v1`). Default is `boldor`.
- **Architecture:** `ACTIVE_VENUE` / `IS_ZUG` + a `ZG` config object near the top of the inline JS. Lac Léman globals (`LAKE`, `GRID_POINTS`, `ZONE_NAMES`, `ML_STATIONS`, `WAYPOINTS`, `BOL_DOR_*`, map bounds) are left intact and only conditionally overridden when `IS_ZUG`. Venue-coupled functions (`classifyWindPattern`, `updateCountdown` labels via `VLAB`, `updateRaceDayBanner`, `toggleLiveMode`) branch to Zugersee variants. `applyVenueChrome()` swaps the title, wind-pattern guide and injects the toggle.
- **Zugersee dry run:** Goldschäkel Regatta (YC Immensee), Sat 30 May 2026 (start time provisional, SI pending). Wind obs: MeteoSwiss **Cham (CHZ)** on the NW shore (primary) + LUZ/WAE/AEG/PIL; forecast via Open-Meteo at Zugersee grid points. Live fleet tracking is **TracTrac via manage2sail** (link-out only — a small club regatta may not be tracked). Lake shoreline + 9 wind-grid points come from real OSM geometry (rel 540344); zones are Untersee/Chiemen/Obersee; the bank advisor + wind classifier use Zugersee patterns (Bise/Föhn/West/thermal). See `docs/Zugersee-wind-brief-2026-05-24.md`. The Zugersee path needs an on-device smoke test.

See `docs/QA-fix-round2.md` for full status table with commit hashes, `docs/CHANGELOG.md` for chronological commit-level log.

### Documentation conventions

- **`docs/CHANGELOG.md`** — append-only commit-level log. Every functional commit MUST add one entry under today's date.
- **`docs/QA-fix-round2.md`** — active build brief. Items are marked ✅ Done with commit hash as they ship, or ⏳ Next / 🔒 Blocked.
- **`docs/PRD-v4.md`** — original feature scope (locked, no edits).
- **`docs/PRD-v5-addendum.md`** — strategic direction (variable `perfFactor`, Performance Memory, sister-app, YDVR-04, data-source roadmap).
- **`docs/performance-review-2026-05.md`** — May 2026 analysis of 8 Kwindoo races; source of the 0.75 reach `perfFactor` value.
- **`docs/trim-coach-design.md`** — full UX/algorithm/acceptance spec for Trim Coach.
- **`docs/analyze_all.py`** — reusable PPR analysis script. Will become the basis for the in-app Performance Memory feature (post-race).
- **`workers/`** — Cloudflare Worker source + deploy guide for the CORS proxy.

When making changes, Claude Code MUST:
1. Update `docs/CHANGELOG.md` with one entry per commit
2. Update `docs/QA-fix-round2.md` to mark the relevant item ✅ Done with commit hash
3. Include both doc updates in the same commit as the code change (single commit per feature)

## API Endpoints

### Open-Meteo (Forecasts)
- **Base URL:** `https://api.open-meteo.com/v1/forecast`
- **Auth:** None. Free tier. CORS-friendly.
- **Params:** `latitude`, `longitude` (comma-separated for multi-point), `hourly=wind_speed_10m,wind_direction_10m,wind_gusts_10m`, `wind_speed_unit=kn`, `models=<model_name>`
- **Models:** `meteofrance_arome_france_hd` (1.3km), `icon_d2` (2km)
- **Quirk:** Response keys suffixed with model name (e.g., `wind_speed_10m_meteofrance_arome_france_hd`). Check both suffixed and unsuffixed keys.

### MeteoSwiss (Station Observations)
- **Wind speed:** `https://data.geo.admin.ch/ch.meteoschweiz.messwerte-windgeschwindigkeit-kmh-10min/ch.meteoschweiz.messwerte-windgeschwindigkeit-kmh-10min_en.json`
- **Wind gusts:** `https://data.geo.admin.ch/ch.meteoschweiz.messwerte-wind-boeenspitze-kmh-10min/ch.meteoschweiz.messwerte-wind-boeenspitze-kmh-10min_en.json`
- **Auth:** None. Free open data. CORS-friendly.
- **Format:** GeoJSON FeatureCollection. Coordinates in **CH1903+ (EPSG:2056)**, NOT WGS84. Filter by station `id`.
- **Speed conversion:** km/h → ÷ 1.852 = knots.
- **Relevant Lac Léman stations:** PUY (Pully), GVE (Genève-Cointrin), CGI (Nyon/Changins), AIG (Aigle), EVI (Évian area)

### DeepRegatta (Historical Race Data)
- **Base URL:** `https://oscar.deepregatta.com/`
- **Race data:** `?race=BOL25` etc.
- **Available:** Track data, rankings, sector times, wind shift analysis
- **Quality varies:** "fair" for most Bol d'Or races, "excellent" for TF35

### MySuiviRegate (Live Competitor Tracking)
- **Web URL:** `https://www.mysuiviregate.com/`
- **Protocol:** WebSocket-based real-time tracking during race
- **Fallback:** HTTP polling of public race page
- **Note:** API investigation deferred to race week — plan to reverse-engineer websocket protocol

## Lac Léman Race Course Waypoints

```javascript
// Bol d'Or course is a round trip (7 waypoints in index.html); Zugersee venue swaps its own.
const WAYPOINTS = [
  { name: "Start (Genève)",    lat: 46.2044, lon: 6.1568 },
  { name: "Nyon passage",      lat: 46.3830, lon: 6.2340 },
  { name: "Lausanne abeam",    lat: 46.5080, lon: 6.6280 },
  { name: "Montreux approach", lat: 46.4340, lon: 6.9100 },
  { name: "Le Bouveret mark",  lat: 46.3910, lon: 6.8570 },
  { name: "Return: Lausanne",  lat: 46.5080, lon: 6.6280 },
  { name: "Finish (Genève)",   lat: 46.2044, lon: 6.1568 }
];
```

## Lac Léman Wind Patterns

| Pattern | Direction | Key Characteristics |
|---------|-----------|---------------------|
| Bise | NE | Cold, dry, can persist for days. Strongest Petit Lac. |
| Vent (SW) | SW | Warm, humid, often before fronts. Good downwind sailing. |
| Séchard | N/NW | Foehn-like, dry, gusty near Jura. Rare but strong. |
| Lake Breeze | Variable | Thermal, develops afternoon, cross-lake. Key for light-air legs. |
| Joran | NW | Evening katabatic from Jura. Can surprise near north shore. |
| Vaudaire | SE | Foehn from Rhône valley, Haut-Lac specialty. Can be 25+ kn. |
| Rebat | Variable | Post-frontal thermal, afternoon, unstable. |

**Critical note:** AROME HD model underestimates mid-lake and Haut-Lac wind by 5-6 knots. Always cross-reference with station observations.

## Design Principles

- Night-vision friendly by default (dark theme with blue/teal accents)
- Day mode via toggle or system `prefers-color-scheme`
- CSS variables: `--bg`, `--bg2`, `--bg3`, `--card`, `--tx`, `--tx2`, `--tx3`, `--acc`, `--acc2`, `--warn`, `--err`
- Responsive breakpoints: 600px (phone), 900px (tablet/laptop)
- Auto-refresh every 10 minutes
- Single-file HTML architecture (inline JS/CSS, CDN dependencies only)
- PWA with service worker for offline capability

## GitHub Repository

- **Repo:** https://github.com/JPSMONT/bol-dor-tactical (Public)
- **Branch:** main
- **Push with:** `git push origin main` (credentials come from `gh auth setup-git`; ensure `gh auth status` shows JPSMONT as the active account, switch with `gh auth switch -u JPSMONT` if needed). The older `git -c credential.helper= push -u origin main` form disables the gh helper and only works for interactive token entry, so don't use it from a non-interactive shell.

## Racing Context

### Performance Baseline (Yardstick 2021-2024)
- 19 races, 1 DNF. Average rank: 6.9
- 2 wins, 9 podiums (47%), 11 top-5 (58%)
- Strong in small fleets, weak in larger ones
- Primary improvement: starts in big fleets, consistency

### Key Competitors (TCF3 class)
- Analyse via DeepRegatta historical data
- Focus on boats in TCF 0.95-1.05 rating band
