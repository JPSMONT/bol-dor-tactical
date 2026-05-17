# QA Fix Round 2 — Bol d'Or Build Plan

**Date:** 17 May 2026
**Race:** Bol d'Or Mirabaud, Sat 6 June 2026, 10:00 CEST
**Window:** 20 days to race start, 13 days to T5 dry run on Lac Léman (30 May)
**Status:** Active build brief — hand directly to Claude Code in terminal

This document consolidates the active build list after:
- The Round 1 QA audit (which identified the original 11-fix list — see `QA-fix-round1.md`)
- An audit of `index.html` against that list (which confirmed many items already shipped)
- The May 2026 performance review (see `performance-review-2026-05.md`)
- The PRD v5 strategic direction (see `PRD-v5-addendum.md`)
- The YDVR-04 install decision (yard installs week of 22–26 May)

**Do not implement anything from `QA-fix-round1.md` directly.** Round 1's items 1, 2, 3a-d, 4, 5b, 6a, 7c, 8, 9, 11b are already shipped (verified in code). This document supersedes that file as the canonical "what to build next" list.

---

## 1. Status of Round 1 items (verified against current code)

| Round-1 item | Status | Notes |
|---|---|---|
| 1. Polar curves render | ✅ Done | `drawCurve(P_JIB, ...)`, `drawCurve(P_SYM, ...)` |
| 2. Split Jib / Spinnaker polars | ✅ Done | `P_JIB`, `P_SYM` populated with full ORC data |
| 3a-d. Polar/sail/penalty math in route sim | ✅ Done | `QA Fix 3a/b/c/d` comments in `simulateLJRoute` |
| 3 (big — animated race sim) | ❌ Skipped | User direction: Strategy route sim covers the use case |
| 4. Blue jib / green spinnaker colours | ✅ Done | `#4a9eff` jib, `#2dd4a8` spinnaker |
| 5a. Hide boat-specs card | ❌ Outstanding | Currently hard-rendered on Dashboard |
| 5b. Systems Check / readiness card | ✅ Done | 5 app-readiness + 14 manual items |
| 5c. Countdown → race-clock transition | ❌ Outstanding | Currently just shows "RACE DAY!" |
| 6a. Wind auto-load on startup | ✅ Done | Global `fetchWind()` + 15-min interval |
| 6b. Wind direction convention | ⚠️ Verify on water | Code uses Open-Meteo value as-is (meteorological); discrepancy was likely model-vs-reality, not code bug |
| 7a. Broken radar link | ❌ Outstanding | Old MeteoSwiss URL still in line 464 |
| 7b. "Pattern Read" rename | ❌ Outstanding | Still says "Pattern read" at line 478 |
| 7c. More forecast points | ✅ Done | 9 grid points × 4 models |
| 7d. Pattern timeline in 48h forecast | ❌ Outstanding | Pattern detection only on live, not forecast |
| 8. Strategy race-day cockpit | ✅ Done | GPS, compass, PPR bar, night mode |
| 9. Map quality overhaul | ✅ Done | Leaflet + OpenSeaMap shipped |
| 10b. Tack thrashing in route sim | ❌ Outstanding | No `minTackInterval` / `hysteresis` |
| 11a. Rivals during sim | ❌ Outstanding | No sim → rival display integration |
| 11b. Sector times from GPS | ✅ Done | "Sector arrival times" table populated |
| 11c. Units confusion (`+1027m`) | ❌ Outstanding | Line 3282 emits raw `m` |
| 11d. Per-tack loss analysis | ❌ Deferred | Needs ≥1 Hz GPS — will come from YDVR-04 data, not Kwindoo |
| Favicon / home-screen icon | ❌ Outstanding | Crash trigger; never landed |

---

## 2. New items from the May 17 strategy session

### 2.1 Variable performance factor `perfFactor(twa)`

**From:** May 2026 performance review (§7.1 of `performance-review-2026-05.md`).
**Currently:** Flat `perfFactor` scalar (default 0.90) used as a multiplier on polar BTV in both `simulateLJRoute` and `isochroneRoute`.
**Change:** Replace the scalar with a function-of-TWA returning:
- TWA < 60° → 0.90 (upwind)
- 60° ≤ TWA < 130° → **0.75** (reach — evidence-based weakness)
- TWA ≥ 130° → 0.90 (downwind)

**Rationale:** the performance review on 15 race windows found reach PPR consistently 25-50% below upwind/downwind on a polar-relative basis. The 0.75 value quantifies the structural reach weakness *relative to existing-sails polar* (not relative to new sails). Flat 90% over-estimates the boat's reach capability in the simulator.

**Acceptance:**
- Both `simulateLJRoute` and `isochroneRoute` call a shared `perfFactor(twa)` function.
- Sim panel exposes a small "Performance profile" dropdown (Default / Conservative / Aggressive) with editable values; default to 0.90/0.75/0.90.
- Race-sim total time estimate visibly differs from previous flat-90 results.

### 2.2 Wind Calibration Mode (fallback path)

**From:** PRD v5 addendum §3.
**Purpose:** Crew can override the model wind with on-water observation.
**Where:** Strategy tab, small "Calibrate wind" button near the existing wind summary.
**Interaction:** Tap → small form (TWS in knots, TWD in degrees or cardinal) → app computes the delta vs current model ensemble at the boat's lat/lon → applies that delta to all wind reads for the next 60 minutes → decays linearly back to unadjusted model.
**Persist:** active calibration offset stored in `localStorage` so it survives a reload during the race.

**Acceptance:**
- After entering "8 kn from 240°", the Strategy tab's wind display, bank advisor, and race sim all use 8/240° at the current time and ~7/240° an hour later.
- A small "calibrated" badge appears on the wind display while offset is active.
- Calibration auto-clears after 60 minutes, or the crew can clear it manually.

### 2.3 Trim Coach panel

**From:** May 17 strategy session — the user's reframe from "static trim cards" to "live trim observation."
**Where:** Strategy tab, new compact panel.
**Content:** Four live readouts, computed from available data:

| Readout | Source | Display |
|---|---|---|
| **PPR** with 30 s / 2 min rolling trend | GPS SOG ÷ polar target at current TWS/TWA | Number + arrow showing trend direction |
| **TWA vs optimal** | Compare current TWA to the polar's best-VMG angle for this TWS | "Sailing at 78° / optimum is 85°" |
| **Wind shift trend** | Model TWD or calibrated TWD over last 15 min | "Right 8° in 12 min" |
| **Point-of-sail transition alert** | TWA crossing 60° / 100° / 130° thresholds | "Approaching spinnaker crossover" |

**Modes:**
- **Planning mode** (before race day, no GPS): inactive, shows "GPS needed for live coaching"
- **Live mode** (GPS on): live readouts as above
- **Live + instruments mode** (YDVR-04 connected, Phase 2 below): readouts use real TWS/TWD/BSP from boat sensors

**Acceptance:**
- Panel visible on Strategy tab; can be collapsed.
- Readouts update at least once every 5 seconds in live mode.
- PPR trend reflects actual SOG changes (verifiable by running the route sim and watching the trend).
- Wind shift detection triggers an alert when TWD changes >10° over 15 min.

### 2.4 Live Instruments mode (YDVR-04 dependent)

**From:** PRD v5 addendum §5.2.
**Depends on:** YDVR-04 install (week of 22-26 May), WiFi broadcast configured, bench-tested at yard.
**Purpose:** Replace model wind with real-time gWind + DST800 + GPS readings from the boat's NMEA 2000 backbone.

**Where:**
- New "Instruments" toggle on Strategy tab.
- When enabled, app attempts to connect to the YDVR-04's WiFi access point.
- On successful connection, listens for NMEA 2000 PGNs on the configured TCP/UDP port (verify with installer — typical default is UDP 2002).

**PGNs to consume:**
| PGN | Data | Used for |
|---|---|---|
| 129025 | GPS position (lat/lon) | Boat position on map |
| 129026 | COG, SOG | Performance display, validation |
| 127250 | Vessel heading | Compass, TWA computation |
| 130306 | Wind data (TWS, TWD, AWS, AWA) | Trim Coach, sim, bank advisor |
| 128259 | Speed through water (BSP) | True PPR computation |
| 128267 | Water depth | Information only |

**Fallback behaviour:**
- If WiFi connection fails or YDVR-04 is unreachable, app silently falls back to model ensemble + calibration.
- Crew sees a "Live instruments" badge (green) or "Model wind" badge (amber) on the Strategy tab so the data source is always clear.

**Acceptance:**
- Connecting to YDVR-04 WiFi populates Trim Coach with real-time TWS/TWD/BSP within 5 seconds.
- True PPR uses BSP not SOG → values are independent of current/drift.
- Disconnecting WiFi falls back to model wind without breaking the app.

### 2.5 Self-hosted CORS proxy

**From:** Repo README "Known quirks" section. Race-day risk.
**Currently:** Rivals tab and replay rely on `corsproxy.io` and `api.allorigins.win` as fallbacks to fetch SuiviRegate KMZ files. Both are public services that will rate-limit under load.
**Change:** Stand up a tiny Cloudflare Worker (or Vercel edge function) under a domain you control. ~20 lines of code. Update the `CORS_PROXIES` array in `index.html` to point to it as the first entry.

**Acceptance:**
- Worker URL like `https://corsproxy.yourdomain.workers.dev/?url=...` returns the upstream content with permissive CORS headers.
- Rivals tab loads BOL25 / BOPM24 / BOM23 / BOM21 KMZ files via the new proxy.
- Public proxies remain as second/third fallback in case the Worker fails.

---

## 3. Build queue with priorities

### P0 — trivial bug fixes (1-2 days total, can start now)

| # | Item | Files | Effort | Notes |
|---|---|---|---|---|
| 1 | **Fix 7a** — radar link | `index.html` line 464 | 2 min | Replace with `https://www.meteoswiss.admin.ch/weather/precipitation/nowcasting.html` (verify current URL on MeteoSwiss site first) |
| 2 | **Fix 7b** — "Pattern read" rename | `index.html` line 478 | 2 min | Change to "Current Wind Pattern" |
| 3 | **Fix 11c** — sector delta units | `index.html` line 3282 | 5 min | Change `+'m</span>'` to `+' min</span>'` (verify other instances) |
| 4 | **Fix 5a** — collapse boat-specs card | `index.html` ~line 384 | 30 min | Wrap card content in `<details>`/`<summary>` with summary text "Boat info" |
| 5 | **Fix 5c** — countdown → race clock | `index.html` ~line 800 (`updateCountdown`) | 1-2 hr | States: pre-D-day (current behaviour) / D-0 before gun (minutes precision) / live race (T+HH:MM elapsed, green) / finished (total time) |
| 6 | **Favicon / home-screen icon** | new `apple-touch-icon` PNG + manifest update | 30 min | Need a square icon (1024×1024). Crashed the last session because of image upload. User to provide PNG, code-side change is minimal. |

### P1 — high value, no YDVR-04 dependency (4-5 days, this week + next)

| # | Item | Files | Effort | Notes |
|---|---|---|---|---|
| 7 | **Variable `perfFactor(twa)`** (§2.1 above) | `index.html` `simulateLJRoute`, `isochroneRoute` | 0.5 day | Function returning 0.90/0.75/0.90 by TWA band; small UI to tune |
| 8 | **Wind Calibration Mode** (§2.2 above) | `index.html` Strategy tab + wind read functions | 0.5 day | localStorage persistence, 60-min decay |
| 9 | **Trim Coach panel** (§2.3 above, Live mode only — no Live Instruments mode yet) | `index.html` Strategy tab | 2 days | Four readouts, refreshing live from GPS + model wind |
| 10 | **Self-hosted CORS proxy** (§2.5 above) | New Cloudflare Worker + `index.html` `CORS_PROXIES` array | 1 day | Cloudflare Worker code + config + deploy |
| 11 | **Fix 7d** — pattern timeline in 48h forecast | `index.html` Wind tab | 1 day | Apply current pattern-detection logic to each hour of the forecast; highlight race window |
| 12 | **Fix 10b** — route sim tack thrashing | `index.html` `simulateLJRoute` greedy-VMC loop | 0.5 day | Min tack interval 5 min; hysteresis requiring >5° VMG advantage; light-air hold-course mode below TWS 3 |

### P2 — depends on YDVR-04 install (target: 27 May - 1 June, after yard returns)

| # | Item | Files | Effort | Notes |
|---|---|---|---|---|
| 13 | **Live Instruments mode** (§2.4 above) | New module in `index.html` + Strategy tab toggle | 1-2 days | WiFi NMEA reader, PGN parsers, fallback logic, badges |
| 14 | **Trim Coach upgrade** to use live data | Existing Trim Coach (#9) | 0.5 day | Switch data source from model wind to instrument wind when Live Instruments active |
| 15 | **True PPR using BSP** | `index.html` PPR display logic | 0.5 day | When BSP available, use it instead of SOG for performance comparison |

### Deferred / Skipped

| Item | Reason |
|---|---|
| Fix 3 big — animated race sim | User direction: route sim covers the use case; animated boat-on-map not race-critical |
| Fix 11d — per-tack loss analysis | Needs ≥1 Hz GPS; will come from YDVR-04 logged data after the season, not from Kwindoo |
| Fix 11a — rivals during sim | Dependency on Fix 3 big which is skipped; revisit post-race |
| 3+ device role-tuned profiles | User direction: ignore |
| Performance Memory feature (full) | Post-race per PRD v5 addendum §2 |
| Sister app (Training & Improvement) | Post-race per PRD v5 addendum §4 |

---

## 4. Suggested implementation order

For Claude Code, suggested sequence:

1. **Day 1** — P0 items 1-4 (trivial fixes 7a, 7b, 11c, 5a). Commit as one batch: "QA round 2 — quick fixes (radar, rename, units, boat-specs collapse)"
2. **Day 1-2** — P0 item 5 (countdown transition). Commit: "QA round 2 — countdown to race-clock transition"
3. **Day 2** — P0 item 6 (favicon). User provides PNG; code+manifest update.
4. **Day 2-3** — P1 item 7 (variable `perfFactor`). Commit: "QA round 2 — variable performance factor by point of sail"
5. **Day 3** — P1 item 8 (Wind Calibration Mode). Commit: "QA round 2 — Wind Calibration Mode"
6. **Day 4-5** — P1 item 9 (Trim Coach panel — live mode). Commit: "QA round 2 — Trim Coach panel"
7. **Day 5-6** — P1 item 10 (CORS proxy). Commit: "QA round 2 — self-hosted CORS proxy"
8. **Day 6-7** — P1 items 11, 12 (pattern timeline, tack thrashing). Commit each separately.
9. **Day 8** — Field test at home: open app on phone, run through all P0+P1 changes, fix any small issues.
10. **Day 9-10** — T5 dry run (30 May) preparation: deploy to GitHub Pages, verify on iPhone.

After YDVR-04 install (week of 22-26 May):

11. **Day 11-12** — P2 item 13 (Live Instruments mode). Bench-test on boat first.
12. **Day 13** — P2 items 14, 15 (Trim Coach upgrade, true PPR via BSP).
13. **Day 14** — Final on-water test before 4 June dock day.

---

## 5. Acceptance criteria — overall

The app is "ready for race" when:

1. **No P0 items outstanding** — all bug fixes committed and visible at `https://jpsmont.github.io/bol-dor-tactical/`.
2. **All P1 items committed** — variable performance factor, Wind Calibration Mode, Trim Coach panel (live mode), CORS proxy, pattern timeline.
3. **PWA installs cleanly** on all crew phones with custom home-screen icon.
4. **Service worker caches** the full app shell + Open-Meteo + MeteoSwiss responses for offline race-day use in the Haut-Lac dead zone.
5. **CORS proxy** verified working — Rivals tab loads at least BOL25 reliably.
6. **Optional but desirable:** P2 items (Live Instruments via YDVR-04) at least field-tested before race day, with confirmed fallback to model wind if instruments fail.

---

## 6. Out-of-scope for this round

The following are explicitly NOT to be touched in QA round 2 — they live in PRD v5 addendum's "future direction" sections:

- Performance Memory feature (post-race)
- Sister app for training/improvement (post-race)
- Multi-regatta architecture / shared library refactor (post-race)
- Per-rival deep-dive expansion beyond what's already in code
- Polar refinement / measured-polar computation (needs season of YDVR data)
- Native iOS app or App Store distribution (PWA is sufficient)

---

*Document version: 1.0 — 17 May 2026*
*Source: synthesis of QA-fix-round1.md verified audit + performance-review-2026-05.md + PRD-v5-addendum.md*
*Implementation venue: Claude Code in user's terminal, project at `~/Desktop/bol-dor-tactical/`*
