# Changelog

All notable changes to the Bol d'Or Tactical PWA, in reverse chronological order.

Format inspired by [Keep a Changelog](https://keepachangelog.com/). Each entry references the commit hash on `main`.

---

## 2026-05-26 — Rivals tab — Zugersee Cup version (Kwindoo + Yardstick)

### Added
- **Venue-aware Rivals tab.** Bol d'Or behaviour unchanged (SuiviRegate + 5 primary targets + per-rival analysis). On Zugersee, the tab now shows three cards from `docs/PRD-v6-rivals-zugersee-spec.md`:
  1. **Event header** — pill row to switch between the 4 Zugersee Cup 2026 events (Goldschäkel 30 May / Blauband 27 Jun / Rigi Anker 29 Aug / Chomer Bär 12 Sep). Auto-selects the nearest future event. Shows host club, race date, live countdown, plus action links to Manage2Sail (where the URL is known), the host club's site, and the Zugersee Cup series page.
  2. **Live tracker — Kwindoo.** An `<iframe>` embed of `kwindoo.com/tracking/<event-id>` for the active event. Joao pastes each event's Kwindoo URL once the host club publishes it; it's persisted per-event in `localStorage` (`zsc_events_v1`). URL input is validated to `kwindoo.com` only (no embedding arbitrary sites). If iframe load fails (Kwindoo CSP), a clear "Open in new tab ↗" link is always present as a fallback.
  3. **Yardstick class panel.** Editable reference table seeded with Zugersee Cup regulars (J/70, T780, Esse 850, Surprise, Ufo 22, First 25.7) plus CYD 27 = 94. Class window defaults to ±4 (90–98) and is editable. Add / remove boats persists in `localStorage` (`zsc_yardstick_v1`, `zsc_yardstick_window_v1`). Direct link out to the Swiss Sailing Yardstick Liste 2025 PDF.
- **`ZG.zscEvents` registry** — hard-coded 2026 event list with date / host / manage2sail URL where public. Easy to extend / annotate per season.
- **Advisor-aware.** Save URL, Clear, Add boat, Delete boat, Window edit — all hidden on Advisor devices. The Yardstick + Kwindoo cards still render read-only so the crew can see the active config.

### Changed
- **Service worker cache v17 → v18.**

### Notes
- Per-event Kwindoo URL is *not* auto-discoverable — Kwindoo has no public API exposing events by venue / host. Joao pastes the URL on the morning of each event once the host club sends out the NOR / member email. The friction is one paste-and-save per event, but it works for *any* future event without code changes.
- iframe `sandbox="allow-scripts allow-same-origin allow-popups allow-forms"` is the minimum permission set for Kwindoo to render and accept clicks without giving it cross-origin reach into the PWA.
- Yardstick seed values are typical for the Zugersee Cup fleet (drawn from the 2025 Goldschäkel write-up and Swiss Sailing Liste 2025). Joao can correct / add as he learns the fleet over the season.

---

## 2026-05-26 — 48h forecast resilient to upstream outages

### Fixed
- **"Wind fetch failed: Response served by service worker is an error"** on Zugersee (and intermittently on Bol d'Or) — three root causes addressed:
  1. **`Promise.all` → `Promise.allSettled`** in `fetchWind()`. The forecast queried 4 models in parallel and rejected the whole `Promise.all` on the first model error, hiding partial successes. Now each model resolves with `{model, ok, error?}` and the page renders with whichever models came back. Status pill shows "3/4 models (others unavailable)" when partial.
  2. **Venue-aware model list.** `meteofrance_arome_france_hd` is a France-only domain model and always 502s for Zugersee (Switzerland). Dropped from the Zugersee model list. Bol d'Or still uses all 4. The list is set at venue init: `IS_ZUG ? 3 Swiss/D2 models : 4 models incl. AROME-HD`.
  3. **HTTP status / content-type check before `.json()`.** Open-Meteo's nginx 502 pages have no CORS headers and HTML bodies, so they previously turned into either CORS-throws inside the SW (→ `Response.error()` → opaque error) or JSON parse errors in the page. Now `fetch().then(r => { if(!r.ok) throw new Error('HTTP '+r.status); ... })` short-circuits cleanly with a useful error.
- **Service worker no longer caches non-2xx responses.** Previously a transient 502 would be cached and served on every subsequent reload until a successful network fetch happened — poisoning the offline fallback. Now `c.put` only fires when `r.ok`, so the next reload always re-tries the network. When network fails entirely with no cached fallback, the SW returns a clearly-shaped `503` JSON `{error:true, sw_fallback:true, reason:...}` so the page can surface a real message instead of an opaque error.
- **Per-model error reporting in the UI.** When all models fail, the message lists which model returned what (e.g. "icon ch1: HTTP 502 from Open-Meteo, icon ch2: HTTP 502, ...") so the upstream cause is visible instead of hidden behind one generic line.

### Changed
- **Service worker cache v16 → v17.**

### Notes
- Open-Meteo was returning 502 across most models when this was diagnosed; the fix means the app stays usable through such outages instead of going dark. Bol d'Or race day's tactical decisions can't depend on all 4 models always being up — partial-render keeps the dashboard alive.
- Pattern Timeline is fed by the same `fetchWind` success path → it stays stuck on "Waiting on forecast…" only when all models fail, and renders normally on partial success.

---

## 2026-05-26 — Day-mode contrast + scroll fix + fonts round 3

### Fixed
- **Day-mode contrast — buttons with black text on dark accents** were unreadable. Introduced `--btn-on-fg` CSS variable (`#06121f` in Night, `#ffffff` in Day) and routed all accent-backgrounded buttons through it (`race-badge`, `polar-controls.on`, `ckpt-mode`, `sim-toggle`, `gps-btn.start`, `wp-btn.active`, `year-btn.on/loading`, `phase-step.current`, `rival-link.rival-live.on`, `cal-badge`, `cl-item.auto.checked`, plus the venue/role/theme floating pills and the Tuning Log Save button + sail toggles).
- **Polar diagram axes invisible in Day mode** — canvas grid + tick labels were drawn at white-on-anything. Now reads `--polar-axis-{strong,med,weak,faint,ghost,label}` CSS variables at every render (light shades in Night, dark shades in Day) so the diagram inverts cleanly on theme swap.
- **Strategy / Rivals map base tile** — switched from CARTO `dark_all` to CARTO `light_all` in Day mode. Initial render picks the right base from `document.documentElement.dataset.theme`; `setTheme()` calls `swapMapBaseTiles()` to swap live without a reload (removes the existing CARTO layer, adds the new one, preserves OpenSeaMap seamarks above). Map container background switched from hardcoded `#000` to `var(--bg)` so the loading skeleton matches theme.
- **Scroll not working on Dashboard / Polars (iPad)** — the floating Day/Night, Primary/Advisor, Bol d'Or/Zugersee pills were `position:fixed` and captured swipe-to-scroll touches in the bottom-right corner. Set `pointer-events:none` on the pill containers and `pointer-events:auto` on the buttons inside — taps still work, swipes pass through to the underlying scroll container. Bottom padding on `.views` raised from 80 → 140 px to clear the now-3-pill stack.

### Changed
- **Tablet typography — round 3.** Round 2 still under-read at arm's length from the helm in full daylight. Pushed another step:
  - cockpit tile values: 40 → **44** (≥700), 48 → **56** (≥1000)
  - cockpit nav values: 28 → 32 (≥700), 34 → **40** (≥1000)
  - countdown big number: 48 → 54 (≥700), 64 → **76** (≥1000)
  - metric values: 32 → 36 (≥700), 38 → **42** (≥1000)
  - header h1: 20 → 22 (≥700), 24 → **28** (≥1000)
  - tabs: 15 → 17 (≥700), 16 → **19** (≥1000)
  - .app max-width: 880 → 920 (≥700), 1120 → **1180** (≥1000)
  - Newly scaled: checklist items, refresh buttons, GPS/waypoint buttons, zone tabs, leg stats, VMG table cells (with bigger row padding at ≥1000).
  - Floating pills also enlarged for sailing-glove tap targets (font 14 / padding 7×14) and re-spaced to 10 / 60 / 110 px from the bottom.
- **Service worker cache v15 → v16.**

### Notes — open follow-ups
- 48 h forecast on Zugersee returns "Wind fetch failed: Response served by service worker is an error" — likely an SW interception of the Open-Meteo URL going wrong; pattern timeline blocked by same. Next session.
- Rivals tab on Zugersee needs a separate integration: boat list from `zugerseecup.ch`, tracking via Kwindoo (not SuiviRegate). Bigger feature — research + spec next.

---

## 2026-05-26 — Day/Night theme + larger tablet typography (round 2)

### Added
- **Day / Night theme toggle** — third floating pill above Primary/Advisor and Bol d'Or/Zugersee. **Day** is a high-contrast light theme designed for bright daylight on water (`--bg #f4f6fa`, `--tx #0a1220`, accent `#0d4ea3`, sub-accent `#006d4f`); **Night** is the original dark theme. Persisted in `theme_v1` localStorage. A tiny bootstrap script in `<head>` sets the `data-theme` attribute on `<html>` *before body renders* so day-mode users don't see a flash of dark. Switching themes re-paints the cockpit + polar diagram + tuning log immediately (canvas elements don't pick up CSS-var changes on their own).

### Changed
- **Tablet typography — round 2** — round 1 widened `.app` but left text borderline-readable at arm's length under sun. Bumped another step across the board:
  - cockpit tile values: 34 → **40** (≥700), 38 → **48** (≥1000)
  - cockpit nav values: 24 → 28 (≥700), 28 → **34** (≥1000)
  - countdown big number: 40 → **48** (≥700), 52 → **64** (≥1000)
  - metric values: 28 → 32 (≥700), 32 → **38** (≥1000)
  - header h1: 18 → 20 (≥700), 20 → **24** (≥1000)
  - tabs / card-titles / pills / strat-notes / bank cards / wind grid / leg cards / forecast / race-sim banner — all bumped 1–4 px
  - `.app` max-width: 860 → 880 (≥700), 1080 → **1120** (≥1000)
- **Service worker cache v14 → v15.**

### Notes
- Day theme tweaks the chrome (cards, text, accents, tags) only; the polar diagram and Leaflet base tiles still use their dark-tuned colors, so they may look slightly off-piece in Day mode. Tunable as a follow-up if it bothers anyone in practice.
- Tablet font bumps cascade correctly over the pre-existing 420 / 520 / 768 px rules; phones (<700 px) are unchanged.

---

## 2026-05-26 — Tablet-responsive layout (iPad)

### Changed
- **`.app` container max-width 480 → 860 px ≥700 viewport, → 1080 px ≥1000 viewport**, with proportional font scaling on the most-read elements. Tablet/iPad users were getting a 480-px-wide phone strip centred on a 1376-pt-wide screen with the dashboard text rendered at phone-sized 10–13 px — barely legible at arm's length from the helm. The widening was a single-line change; the typography pass touches the cockpit tiles (`.ckpt-tile .tv` 30 → 34 → 38 px), nav values, countdown big number (32 → 40 → 52 px), metrics, header, race-badge, tab buttons, pills, strategy notes, bank cards, VMG table, forecast rows, and the Race-Sim banner countdown. Phone behaviour below 700 px is unchanged.
- **Service worker cache v13 → v14.**

### Notes
- Two new media queries (no existing breakpoints removed). The pre-existing `@media(min-width:420px){.metric .val:24px}` is overridden by the new 700-px rule (28 px) and the 1000-px rule (32 px) in cascade order.
- `@media(max-width:520px)` still collapses the cockpit row-2 grid on phones; the iPad 3-column cockpit row is preserved.
- Knock-on benefit: the pre-existing `@media(min-width:768px){.tc-grid}` Trim-Coach 2-column rule now activates on iPad portrait too (it was previously dead code that no real device hit).

---

## 2026-05-24 — Tuning Log build (PRD v6 Phase 1.6)

### Added
- **`tuning_log_v1` localStorage log + Tuning Log card on the Polars tab**, implementing `docs/PRD-v6-tuning-log-spec.md` v1:
  - **⊕ Log current setup** button opens a modal with eight sliders (backstay 0–10, jib car 1–10, outhaul 0–10, cunningham 0–10, vang 0–10, traveller −5 … +5, halyard main 0–10, halyard jib 0–10) defaulting to the last saved entry (first-ever entry = `5/3/5/3/3/0/5/5`). Sail toggle (Jib / Spi). Single free-text Note line.
  - **Auto-captured** at save time from the live cockpit: `t`, `mode` (from `raceState()`), `venue` (from `ACTIVE_VENUE`), TWS / TWA / TWD with source tag, SOG / polar target / polar % / VMG (from `computePerf()`). No manual data entry for context.
  - **Best-by-wind-band stripe** at the top of the card — top-1 entry per band (≤6 / 6–12 / 12–18 / 18+ kt), close-hauled only (TWA <90), formatted as `<polar%> — BS x · JC y · OH z · V v`.
  - **Recent entries table** — relative-time labels (same day → "−3m"), TWS · TWA, colour-coded polar %, four-control summary, truncated note; tap a row to expand the full 8 controls + sail + note. Filters: wind band (all / ≤6 / 6–12 / 12–18 / 18+) and point of sail (upwind <90° / off-wind ≥90°). Default 20 most recent + **Show all** toggle.
  - **CSV export** flattens entries with one row per snapshot (21 columns including all 8 settings, ISO + ms timestamps) — joinable to a GPS-track CSV in a notebook by `t_ms`.
  - **Advisor-aware**: the "Log current setup" button is hidden on Advisor devices; the recent-entries table still renders read-only so the crew can see the most recent setups for discussion.
- **Service worker cache v12 → v13.**

### Notes
- Storage is per-device (`localStorage`); ~200 B per entry → well under 1 MB after a season.
- Settings labels and scales live in code for v1 (the spec parks the `tuning_labels_v1` rename overlay as a v1.1).
- Polar-diagram overlay (each entry as a dot at its TWS/TWA, coloured by polar %) is Phase 2 of the spec.

---

## 2026-05-24 — Spec: Tuning Log (PRD v6 Phase 1.6)

### Added
- **`docs/PRD-v6-tuning-log-spec.md`** — scoped revival of "Performance Memory" (PRD v5 §2). One-tap snapshot of current settings vs polar %, timestamped and joinable to GPS / maneuver log / per-minute polar buckets / future YDVR SD recordings. Specs the data model, the 8-control settings list for Little Johnka (backstay, jib car, outhaul, cunningham, vang, traveller, halyard main, halyard jib + sail toggle), the snapshot UX, recent-entries table, best-by-wind-band view, CSV export, and Advisor-mode integration (Primary device logs only). Spec only — no app code yet.
- **Roadmap**: Phase 1.6 entry + status line updated to reflect specced state.

---

## 2026-05-24 — Advisor mode (multi-device read-only)

### Added
- **Per-device role toggle** for multi-device race-day setups: **Primary** (default — owns GPS, race timer, maneuver log) vs **Advisor** (read-only for race state). On Advisor, the race-control row, Maneuver tile, and cockpit Enable-GPS button switch to a clear notice; the per-second GPS sampler is **disabled** so crew devices can't accumulate conflicting race stats. A small Role pill (Primary / Advisor) stacks above the venue pill; switching reloads the page. Persists in `localStorage` (`device_role_v1`). An **Advisor** badge appears on the cockpit head when active. Bol d'Or / Zugersee default both work as before in Primary mode.
- **Service worker cache v11 → v12.**

---

## 2026-05-24 — Service-worker offline hardening (QA #1)

### Changed
- **`sw.js` rewritten for offline resilience** (cache v10 → v11, plus a separate capped tile cache):
  - **MeteoSwiss** station data (`data.geo.admin.ch`) is now network-first + cached like Open-Meteo → last-known stations survive offline.
  - **Leaflet + JSZip** (pinned unpkg URLs) are precached → the map and replay load with no signal.
  - **Map tiles** (OpenSeaMap seamarks + CARTO dark base) are cached cache-first into a capped runtime cache (~800 tiles) → a race area loaded while online stays usable offline.
  - Hardened: GET-only, defensive fallbacks everywhere, tile cache preserved across app updates.
- Resolves QA-review issue #1 (the last open item from the 24 May review). Tip: open the map over the race area while you still have signal so the tiles cache.

---

## 2026-05-24 — Docs sync to latest state

### Changed
- **README** refreshed: venues (Bol d'Or / Zugersee) + the mode-aware cockpit, maneuver-loss tracker and Debrief; countdown corrected 09:00 → 10:00; repo-file table + line counts updated; venue-aware Wind / Strategy / bank-advisor notes; dark base map.
- **CLAUDE.md** corrected: course is a ~123 km round trip finishing at Genève (not Le Bouveret); `WAYPOINTS` snippet → the real 7-point round trip; service-worker cache note de-pinned (currently v10) and flags the offline gap.
- **PRD-v6 roadmap**: added a build-status line (Phase 0 / 1.5 / 2 v1 shipped; Phase 1 parked).
- **QA-fix-round2**: supersede note for post-17-May work; **QA-review-2026-05-24**: resolution status (#5/#6 fixed, #1 still open).
- Docs only — no code change.

---

## 2026-05-24 — Debrief (Phase 2 v1) + live-instruments architecture spec

### Added
- **In-app Debrief card** (Dashboard, shown when a race is finished): summary (duration, maneuver count, avg loss BL, avg polar %), best/worst maneuver, a polar-% trend bar chart across the race, and a maneuver table (time-into-race / type / loss / TWS). Built from the app's own GPS + maneuver logs (relative/trend); YDVR-04 SD-card import is the planned instrument-grade enhancement. **SW cache v9 → v10.**
- **`docs/PRD-v6-live-instruments-spec.md`** — live-instrument architecture decision after verifying the hardware: the **YDVR-04 is a recorder, not a live source**. A browser can't use a gateway's raw TCP/UDP ports, **but the YDWG-02's own Web Gauges prove a browser-readable WebSocket feed exists** — so a PWA can read the gateway directly (cheapest, no Pi) or via **Signal K** (robust). Includes the NMEA→tile mapping, hardware options, integration plan, and the YDVR-04's role (Debrief / SD import).

### Changed
- `docs/PRD-v6-ai-tactician-roadmap.md` Phase 1 corrected — YDVR-04 = Debrief source; live needs Signal K/gateway + WebSocket; Phase 2 marked v1-shipped in-app.

---

## 2026-05-24 — In-race maneuver-loss tracker (PRD v6 Phase 1.5)

### Added
- **Race-scoped maneuver-loss + polar-% tracker.** GPS-based (best practice: SOG/COG is more stable than wind for tack loss, and numbers are treated statistically). A race-timing control on the cockpit **auto-arms at the gun**, you confirm Start / tap Finish, and both timestamps are **trimmable** (±1m / ±10m) so pre-start tactics and the post-finish sail-down are excluded. While racing it samples each GPS fix, detects tacks/gybes (heading change + speed dip), computes **distance lost vs the pre-maneuver baseline VMG** (metres + boat-lengths), and keeps a running **race-average polar %** (per-minute buckets). The cockpit Maneuver tile shows the last maneuver coloured vs the race average, plus count, average loss, and race polar %. Every maneuver is persisted (localStorage) to seed the Phase-2 maneuver-cost database / Debrief.
- Honest framing: a relative/trend tool until the YDVR (SOG not boat-speed-through-water, model wind) — read it averaged, not per single tack.
- **Service worker cache v8 → v9.** Implements Phase 1.5 of `docs/PRD-v6-ai-tactician-roadmap.md`.

---

## 2026-05-24 — Race cockpit (PRD v6 Phase 0)

### Added
- **Mode-aware Race cockpit on the Dashboard** — a glanceable skipper display at the top of the home page. Mode pill (Planning / Race / Debrief from race-state) + venue label; tiles for Big nav (heading / SOG / next mark + DTW / VMG-to-mark from GPS), Polar efficiency (SOG vs polar target at model wind — reuses `computePerf`), Wind state (`classifyWindPattern`), and Tactical bias (model pressure gradient across the venue zones, with a confidence read), plus honest placeholders for Maneuver value (needs maneuver log) and Tactical risk (needs live fleet). Every tile tags its data source (live / model / future). Venue-aware (Bol d'Or + Zugersee), defensive (no-GPS / no-data states), refreshes on a 2 s tick and on tab switch. Existing Dashboard cards remain below it.
- Implements **Phase 0** of `docs/PRD-v6-ai-tactician-roadmap.md`; designed to upgrade to instrument truth when the YDVR-04 is live (polar-efficiency + wind-state tiles flip model → measured).
- **Service worker cache v7 → v8.**

---

## 2026-05-24 — Docs: AI tactician phased roadmap

### Added
- **`docs/PRD-v6-ai-tactician-roadmap.md`** — phased roadmap turning the AI Tactical Navigator vision into a buildable sequence. Core points: the Dashboard becomes one mode-aware screen (Planning → Race cockpit → Debrief); the critical path is the data layer (YDVR-04 live instruments + telemetry logging), not the UI; 5-tile Race cockpit with per-tile feasibility; Phase 0 (mode-aware cockpit, model/GPS) → Phase 1 (YDVR live) → Phase 2 (Debrief + maneuver cost) → Phase 3 (tactical bias + training) → Phase 4 (voice + ML). Docs only, no code.

---

## 2026-05-24 — Zugersee venue fixes (round 3): real geometry + tactical advisor

### Changed
- **Real Zugersee geometry** — lake shoreline now from OSM (rel 540344, simplified ~250 m) for the point-in-lake logic; the 9 wind-grid points are placed on the actual water and organised by the real basins **Untersee / Chiemen / Obersee** (was Geneva/Lausanne/Bouveret). Fixes markers sitting on land.
- **Bank-selection advisor rewritten for Zugersee** — classifies Bise / Föhn / Westwind / Thermal and gives lake-specific advice (Chiemen-narrows acceleration, Rigi wind-shadow on the Obersee W shore, Föhn in the south, evening Obersee fill) instead of Swiss/French-bank Léman logic. Beat-VMG ranking uses the lake long axis (~343°) since the RC sets the marks. Bank cards show real place names.
- **Zugersee forecast/dashboard tactical notes + map title** venue-aware ('Race course — Zugersee', Zugersee tactical notes).
- Grounded in research: see `docs/Zugersee-wind-brief-2026-05-24.md` (windfinder climatology ~3 kt WSW; ESYS Revier; Swiss Wind Atlas).
- **Service worker cache v6 → v7.**

---

## 2026-05-24 — Zugersee venue fixes (round 2)

### Changed
- **Venue-aware dashboard/forecast labels** — in Zugersee mode the "Current wind" card, the "Start line conditions" card, and the 48 h forecast zone tabs now read Zugersee / Immensee / Zug·Walchwil·Arth (the data was already Zugersee; only the labels were hardcoded).
- **Zugersee forecast pattern classifier + legend** — the pattern timeline classifies and labels with Zugersee patterns (Bise / Föhn / West / Thermal / Calm); Joran/Séchard removed from the legend.
- **Strategy & Rivals maps now have a dark base map** — CARTO dark layer under the OpenSeaMap seamark overlay, so the real shoreline shows (was marks-on-black). On Zugersee the coarse hand-drawn polygon is skipped in favour of the base map; on Bol d'Or the outline is kept as an accent.
- **Removed the Boat info card** and the **Boat + crew readiness section** — readiness is now tool/device-only. Both venues.
- **Service worker cache v5 → v6.**

### Notes
- CARTO base tiles aren't in the SW precache, so the map base needs network (standalone offline fix still open). Zugersee path still wants an on-device smoke test.

## 2026-05-24 — Docs refresh + QA review

### Changed
- **CLAUDE.md current-state snapshot corrected** to match shipped reality (per `SESSION-HANDOFF-2026-05-23` §6): service-worker cache `v3 → v4`; repo visibility `Private → Public`; "What's outstanding" rewritten (Trim Coach is DONE `e719fb9`; outstanding is now Live SuiviRegate race-day polling, Live Instruments mode, Trim Coach live-data upgrade, on-water field test); snapshot date bumped to 24 May 2026.

### Added — Zugersee venue profile (Goldschäkel dry run)
- **Venue switch** — two venues behind a flag: `boldor` (default, **unchanged**) and `zugersee`. Activate via `?venue=zugersee` or the venue pill (bottom-right); choice persists in `localStorage` (`venue_v1`). The Bol d'Or path is byte-identical when the venue is `boldor`.
- **Zugersee profile** — map center/bounds + lake outline; 9-point forecast grid (Zug/Walchwil/Arth); MeteoSwiss stations (CHZ Cham on-lake primary + LUZ/WAE/AEG/PIL); provisional Goldschäkel course (start off Immensee); race clock (Sat 30 May 2026, provisional 10:00 CEST, +8 h finish / +10 h live window); a Zugersee live wind-pattern classifier (Bise / Föhn / Westwind / thermal / Chiemen) + wind-pattern guide; Rivals tab links out to the Goldschäkel on TracTrac / manage2sail.
- **Service worker cache v4 → v5** — forces installed PWAs to pick up the venue feature.
- Verified: full inline JS syntax-valid; Bol d'Or default byte-identical (data literals untouched, every venue branch reproduces the original value, countdown strings identical); Zugersee config + classifier runtime-tested. **Zugersee path still needs an on-device smoke test** (GPS on water, offline). Live TracTrac positions depend on the RC enabling tracking; SI / exact course / start time pending publication.

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
