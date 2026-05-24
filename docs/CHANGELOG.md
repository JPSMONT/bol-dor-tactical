# Changelog

All notable changes to the Bol d'Or Tactical PWA, in reverse chronological order.

Format inspired by [Keep a Changelog](https://keepachangelog.com/). Each entry references the commit hash on `main`.

---

## 2026-05-24 — Docs refresh + QA review

### Changed
- **CLAUDE.md current-state snapshot corrected** to match shipped reality (per `SESSION-HANDOFF-2026-05-23` §6): service-worker cache `v3 → v4`; repo visibility `Private → Public`; "What's outstanding" rewritten (Trim Coach is DONE `e719fb9`; outstanding is now Live SuiviRegate race-day polling, Live Instruments mode, Trim Coach live-data upgrade, on-water field test); snapshot date bumped to 24 May 2026.

### Notes
- QA review pass completed (no code changes): all inline JS / `sw.js` / `workers/corsproxy.js` syntax-valid, `manifest.json` valid, race countdown `2026-06-06T10:00:00+02:00` correct, and all live data endpoints (Open-Meteo, MeteoSwiss, Cloudflare CORS proxy → SuiviRegate KMZ) reachable. Open issues logged in `docs/QA-review-2026-05-24.md`.

---

## 2026-05-17 — QA Round 2 build day

A single afternoon's worth of work that closes most of QA round 2. P0 fully complete; P1 6 of 6 done. Waiting on YDVR-04 install (week of 22-26 May) before P2 begins.

### Added — QA round 2 Batch 4
- **Trim Coach panel** (Strategy tab) — four live readouts between GPS Navigation and the lake map: PPR with 30 s rolling mean and 2-min trend arrow; current TWA vs max-speed target angle (with point-of-sail-aware coaching sub-text); wind shift over last 15 min (TWD buffered every 30 s, tack-aware "lifted / headed" messaging); point-of-sail with transition lookahead within 10°. Three modes auto-detected (Planning / Live · Model wind / Live · Calibrated wind), plus a stubbed `isLiveInstrumentsActive()` hook for the upcoming YDVR-04 instruments mode. Collapse state persists in `localStorage` under `trim_coach_collapsed_v1`; default is mode-aware (collapsed in Planning, expanded in Live) until the crew taps the header. Reuses existing `calibrateWind`, `interpPolar`, `perfFactor`, `P/P_JIB/P_SYM`. Mobile-first single column; 2×2 grid on ≥ 768 px. — `e719fb9`
- **Service worker cache bump v3 → v4** — forces installed PWAs to pick up the Trim Coach panel. — `e719fb9`

### Added — QA round 2 Batch 3
- **Wind Calibration Mode** (Strategy tab) — crew can enter observed wind (TWS, TWD) on the water; app applies that delta to all wind reads for 60 min, then linearly decays back to model. Persists in `localStorage` under `wind_calibration_v1`. Status badge "calibrated" visible while active. Manual clear button. — `82ed1c2`
- **Pattern timeline in 48 h forecast** (Wind tab) — colour-coded strip below the hourly grid showing predicted wind pattern (Bise / Vent / Vaudaire / Joran / Séchard / Morget-Bornan / Môlan / Calm / Mixed) at each hour for each of three zones (Geneva / Lausanne / Bouveret). Race window (Sat 10:00 → Sun 06:00 CEST) highlighted with thicker border. — `75e3724`

### Added — QA round 2 Batch 2
- **Self-hosted CORS proxy via Cloudflare Worker** (`corsproxy-bol-dor.jpsmont.workers.dev`) — replaces dependence on public `corsproxy.io` / `allorigins.win` for fetching SuiviRegate KMZ archives. Host-allowlisted to `suiviregate.ch`, edge-cached 1 h. Worker source at `workers/corsproxy.js`, deploy doc at `workers/README.md`. — `389636f`
- **`replay.html` wired to the same Worker** — replay viewer's own `CORS_PROXIES` array updated to use the Worker first. — `24fc402`

### Added — QA round 2 Batch 1
- **Variable `perfFactor(twa)`** — replaces flat 90 % scalar in route simulator with per-point-of-sail values: upwind 0.90, reach 0.75, downwind 0.90. Editable in the route-sim Performance card; overrides persist in `localStorage`. Reach value (0.75) is evidence-based — quantifies the structural reach weakness identified in the May 2026 performance review. Applied in both `simulateLJRoute` and `isochroneRoute`. — `e19873e`
- **Route-sim tack-thrashing fix** — greedy-VMC algorithm previously oscillated at 1+ tack/minute in light air. Now enforces 5-min minimum interval between tacks, requires >5° VMG advantage to justify a tack, and holds heading below TWS 3. — `f266de0`
- **Service worker cache bump v2 → v3** — forces installed PWAs to refresh and pick up today's icons + features. — `d424933`

### Added — P0 round 2
- **Favicon + home-screen icon set** (Little Johnka logo) — `logo.png`, `apple-touch-icon.png`, `favicon-16.png`, `favicon-32.png`, upsized `icon-192.png` / `icon-512.png`, manifest updated. — `899e2c5`
- **Countdown card with 4 race-clock states** (Dashboard) — pre-D-day countdown → race-morning minutes precision → live race elapsed clock `T+HH:MM:SS` (green) → "Race complete" post-finish. — `9663632`
- **Boat-spec card collapsed** into `<details>` / `<summary>` on Dashboard — saves vertical space; click to expand. — `dc965b9`

### Fixed — P0 round 2 trivial
- Broken MeteoSwiss radar link (Wind tab) — was 404, now points to `precipitation/nowcasting.html` — `30ad03b`
- "Pattern read" renamed to "Current Wind Pattern" (Wind tab) — clearer label — `30ad03b`
- Rivals tab sector delta units — `+X m` → `+X min` so it doesn't read as metres — `30ad03b`

### Docs
- **PRD v5 addendum** (`docs/PRD-v5-addendum.md`) — strategic direction: variable `perfFactor` by POS, Performance Memory feature (parked), Wind Calibration Mode, sister-app vision (training & improvement post-race), data-source roadmap simplified for YDVR-04. — `30ad03b`
- **May 2026 performance review** (`docs/performance-review-2026-05.md`) — analysis of 15 race windows from 8 Kwindoo GPX exports (2024-06 to 2025-08). Key finding: reach is the structural weakness, 25–50 % below upwind/downwind on a polar-relative basis. Recommends 0.90 / 0.75 / 0.90 `perfFactor` values that landed in `e19873e`. — `30ad03b`
- **QA round 2 build brief** (`docs/QA-fix-round2.md`) — verified-outstanding list after auditing actual code state vs original round-1 list. Five batches mapped out. — `30ad03b`
- **`analyze_all.py`** — reusable Python script that produced the performance review. Will become the basis for the in-app Performance Memory feature (post-race). — `30ad03b`
- **CLAUDE.md push instruction simplified** — `gh auth setup-git` was run, so plain `git push origin main` works. Removed the obsolete `git -c credential.helper= push` workaround. — `9ccd73c`
- **Cloudflare Worker source & deploy guide** (`workers/corsproxy.js`, `workers/README.md`) — `389636f`
- **Trim Coach design spec** (`docs/trim-coach-design.md`) — full UX, algorithm, layout, acceptance criteria; built in `e719fb9`.

---

## 2026-05-16 — App reaches v4 PRD scope

Older session; commits not catalogued in this CHANGELOG retroactively. See `git log` for the build sequence — highlights include:

- Polar redesign in ORC Speed Guide style (`3a4c5f7`)
- Polar canvas zoom + pan (`d8c8265`)
- Initial QA round 1 work — polar rendering, Jib/Sym split, sim realism (`998bb97`)
- Overnight build: rival analysis, wind shift detector, race-day checklist, CSV export, comprehensive README (`89c6302`)
- Isochrone routing added to LJ sim and replay (`67afe86`, `a318fb7`)
- Race Sim vs Real Rivals with historical wind + KMZ + gate comparison (`d0beffb`)
- Little Johnka route simulation engine (`4abfd88`)
- `replay.html` rebuilt with Leaflet + real SuiviRegate tracks (`8664c38`)
- Weather Prep dashboard with MeteoSwiss stations + pattern read (`46dcd2a`)
- Rivals tab in three phases — KMZ tracks, sector ranks + head-to-head, lateral chart + time scrubber + race-day banner (`1d5dd73`, `cb8a46d`, `f57e5e5`)
- Leaflet map + GPS/compass waypoint navigation (`3bbdfae`)

Foundational PRD work: PRD v4.0 (`docs/PRD-v4.md`), CLAUDE.md baseline, initial scaffold (`82ed1c2`-era and `c98e34e`).

---

## Convention

Going forward, every functional commit should add one entry under today's date in this file, in the format:

```
- **<short feature name>** (<where in app>) — <plain-language description>, <key implementation detail or persistence note>. — `<commit hash>`
```

Sections: `### Added`, `### Changed`, `### Fixed`, `### Removed`, `### Docs` (free-standing doc-only changes).

Group related commits under a batch heading if relevant (e.g., "QA round 2 Batch 4 — Trim Coach").
