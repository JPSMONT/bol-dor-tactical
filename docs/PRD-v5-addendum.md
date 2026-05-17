# PRD v5 Addendum — Strategic Direction

**Date:** 17 May 2026
**Owner:** Joao Pinto da Silva
**Parent doc:** `docs/PRD-v4.md` (locked, no scope changes)
**Scope of this addendum:** four strategic decisions that emerge from the May 2026 performance review (`docs/performance-review-2026-05.md`) and from the post-QA conversation about app architecture beyond the Bol d'Or.

This is a **direction document**, not a feature spec. It captures decisions and intent so future build phases (and other tools, like Claude Code) have a clear map of where the project is going. Detailed feature specs for each item below will be written when each is brought forward for implementation.

---

## 1. Update — variable performance factor in the race simulator

**Decision:** replace the flat 90% `perfFactor` in `simulateLJRoute` and `isochroneRoute` with a function `perfFactor(twa)` returning a per-point-of-sail value.

| Point of sail | TWA range | Performance factor |
|---|---|---:|
| Upwind | <60° | 0.90 |
| Reach | 60–130° | **0.75** |
| Downwind | >130° | 0.90 |

**Rationale.** The May 2026 performance review across 15 race windows (14.3 hours of racing) found a consistent pattern: reach is the lowest-PPR point of sail, roughly 25–50% below upwind and downwind on a polar-relative basis. **Important: the ORC polar used as the reference is computed for the boat's existing inventory (Main + Jib + Spinnaker — no Code 0, no Drifter), so the gap exists relative to what the boat *can already do* with the sails it owns.** The 0.75 value quantifies the realised performance below the existing-sails polar, not below an idealised polar with new sails. Closing the gap is primarily a trim/technique question, not a sail-purchase question. (Sail purchase is a separate, additive decision — see July 2025 sail-improvement memo and §6.1–6.2 of `performance-review-2026-05.md`.)

*Assumption:* values are conservative. Once on-water wind measurement is available (see §4 below), they will be refined per race, per condition, and over time.

**Implementation note.** The call sites for `perfFactor` are already centralised in the simulation engine. Changing it from scalar to function-of-twa is a small refactor — both `simulateLJRoute` and `isochroneRoute` need to accept a `twa` argument at the BTV-lookup step. Suggest making it configurable in the sim UI (a small "Performance profile" toggle that exposes the three numbers, default to the values above, advanced users can tune).

---

## 2. New feature (parked) — Performance Memory

**Status:** parked until post-Bol d'Or 2026. Not in scope for the 6 June race.

**Concept.** A "Performance" tab in the app that ingests GPX (or NMEA, or YDVR) recordings from past races, computes PPR per race window using the same pipeline as the May 2026 analysis, and maintains a longitudinal performance profile that the user can inspect and the race simulator can read.

**Sketch:**

| Layer | Function | Effort |
|---|---|---|
| GPX import | Drag-drop a Kwindoo / TracTrac / SuiviRegate GPX. App parses and stores in IndexedDB. | 0.5 day |
| Race-window detection | The auto-detection logic from `analyze_all.py`, ported from Python to JS. | 0.5 day |
| Wind ensemble fetch | Open-Meteo historical-forecast API (AROME HD + ICON-D2 + ICON-CH1) — same code path already used elsewhere in the app. | 0.5 day |
| PPR compute | Segment-by-segment SOG vs polar, time-weighted aggregation by point of sail and wind band. Same logic as `analyze_all.py`. | 0.5 day |
| Display | Overall PPR + per-POS breakdown + trend chart of PPR over season. List of races with click-to-detail. | 1 day |
| Calibration feed | When a new race is added, optionally update the simulator's `perfFactor(twa)` defaults based on rolling-average PPR. | 0.5 day |

**Total estimate:** 3–4 days Claude Code time.

**Why parked.** Race-day reliability of the existing tactical features (Strategy, Wind, Rivals, Race Sim) is the priority through 6 June. Performance Memory is a learning tool, useful between races, not during.

---

## 3. New feature (parked) — Wind Calibration Mode

**Status:** parked, but small. Could be built as P2 if there is time before 30 May dry-run.

**Concept.** On race day, the synoptic wind models are unreliable on a lake-scale basis (the entire May 2026 analysis is constrained by this). The crew always has better information — what the wind is actually doing on the boat right now. A "calibrate" interaction lets the crew teach the app what they see.

**UX sketch:**

- Strategy tab gains a "Calibrate wind" button.
- Tap: small form with two fields (speed in knots, direction in degrees or cardinal).
- App computes the delta between observed and current ensemble at the boat's lat/lon, applies that delta to the forecast for the next 60 minutes, then linearly decays back to the unadjusted model.
- The bank advisor, route simulator, and ETA calculations all use the calibrated wind during that window.
- Re-prompt every hour or on a major shift.

**Effort:** ~½ day of Claude Code work. Low risk because it's a small layer over existing data flow.

**Race-day value:** high. This is the cheapest path from "tactical app with iffy wind data" to "tactical app that actually trusts what the crew sees."

---

## 4. Strategic direction — sister app for training & improvement

**Decision:** the next phase of the project (post-Bol d'Or 2026) will split into two complementary apps:

- **Bol d'Or Tactical (this app)** — race-day tactical companion, live and time-critical. Stays focused on the race in front of you.
- **Training & Improvement (sister app)** — between-race analysis, performance trending, polar refinement, manoeuvre coaching, debrief support. Not time-critical; richer interactions OK.

**Why split.** The two have different design priorities:

| Concern | Race-day app | Training app |
|---|---|---|
| Latency tolerance | Sub-second | Minutes-to-hours |
| Information density | Sparse, glance-friendly | Rich, exploratory |
| Mobile vs desktop | Phone in cockpit | Phone or laptop, post-race |
| Connectivity | Often offline | Always online OK |
| User attention | Divided (sailing) | Focused |
| Critical UX | Big numbers, night mode | Tables, charts, drill-down |

Trying to serve both inside one app compromises both.

**Shared infrastructure (the actual architectural opportunity).** The two apps share:
- Polar engine (the ORC table + interpolation functions)
- Wind data fetchers (Open-Meteo, MeteoSwiss stations, future YDVR feed)
- Race-window detection logic
- PPR computation
- Boat metadata (Little Johnka or any other boat)

These should live in a shared library (`shared/lib.js` or similar) that both apps import. The README already flags this: *"If duplication grows further, factor a shared lib.js — the convention is self-imposed and worth breaking when the duplication tax exceeds the deploy-simplicity tax."*

**Other regattas.** As Little Johnka campaigns other regattas (OSCA series on Zugersee, future events), each gets its own race-day tactical app sharing the same shared library and feeding into the same training app. So the architecture is:

```
                    Training & Improvement (sister app)
                              ▲          ▲          ▲
                              │          │          │
                  ┌───────────┴──────────┴──────────┴────────┐
                  │              shared library              │
                  │  (polars, wind fetchers, PPR, race-      │
                  │   window detection, calibration)         │
                  └─────────────────────────────────────────-┘
                              ▲          ▲          ▲
                              │          │          │
                    ┌─────────┴────┐ ┌──┴──────────┐ ┌─────┴────┐
                    │  Bol d'Or    │ │  Zugersee   │ │ Future   │
                    │  tactical    │ │  tactical   │ │ regatta  │
                    └──────────────┘ └─────────────┘ └──────────┘
```

The existing `bol-tactic-pwa` and the prior-session `zugersee-wind` app already partially fit this shape — they share design language and polar engine but each is a standalone HTML file. Step 1 of the sister-app phase is to extract the shared library.

---

## 5. Strategic direction — data source roadmap (updated 17 May 2026)

**Status change:** the yard is installing a Yacht Devices YDVR-04 voyage recorder on Little Johnka the week of 22–26 May 2026. This collapses what was a multi-tier roadmap into a single primary path, because the YDVR-04 provides both post-race logging and live WiFi NMEA broadcast in one device.

### 5.1 Existing instrument suite

The boat already carries a complete sensor package on a NMEA 2000 backbone:

| Instrument | Function | Data provided |
|---|---|---|
| Garmin GPSMAP 721 (N2K + WiFi) | Chartplotter | GPS position, COG, SOG |
| Garmin GMI 20 + DST800 + gWind + GND 10 | Wind + speed/depth/temperature transducers + N2K gateway/power | TWS, TWD, AWS, AWA, boat speed through water (BSP), depth, temperature |
| Garmin GNX Wind | Dedicated wind display | (Reads from gWind sensor — same data, second display) |

All sensors feed the NMEA 2000 backbone via the GND 10. The GPSMAP 721's built-in WiFi is for Garmin's own apps (BlueChart Mobile, ActiveCaptain, Helm) and does not, in stock configuration, broadcast NMEA 2000 sentences as a generic stream readable by third-party apps. Hence the need for a separate WiFi gateway — which the YDVR-04 provides.

### 5.2 YDVR-04 — dual function

The Yacht Devices YDVR-04 is plugged into a spare T-connector on the NMEA 2000 backbone and serves two purposes simultaneously:

| Function | Use case | Data path |
|---|---|---|
| **Voyage logging** to microSD | Post-race analysis, Performance Memory feature, polar refinement | Crew removes the SD card after the race, .DAT files convert to CSV/GPX via Yacht Devices' free tool, app ingests for Training app analysis |
| **Live WiFi NMEA broadcast** | Race-day live data feed for the tactical app | Phone joins the YDVR-04's WiFi access point during racing; the PWA reads NMEA sentences over TCP/UDP and updates the Strategy tab in real time |

**Yard install verification checklist** (must be confirmed before launch):

- [ ] WiFi gateway mode enabled in YDVR-04 configuration (not just logging)
- [ ] Known SSID and password set, documented for the crew
- [ ] Bench test at yard: phone connects to WiFi, NMEA sentences visible
- [ ] First on-water test: gWind, DST800, GPS all flowing into the stream
- [ ] Power, mounting, antenna placement adequate for the cockpit

### 5.3 Final data-source roadmap

The pre-install roadmap (Open-Meteo → calibration mode → portable anemometer → YDVR → live NMEA) collapses to two tiers post-install:

| Tier | Source | When used | Quality |
|---|---|---|---|
| **A. Primary — Live YDVR-04 over WiFi** | Race-day on the boat; YDVR-04 broadcasts the NMEA 2000 bus over WiFi; PWA reads in real time | Always when on the boat with instruments live | Excellent — measured wind, measured BSP, synchronised GPS |
| **B. Fallback — Open-Meteo model ensemble + Wind Calibration Mode** | When boat WiFi isn't reachable, YDVR-04 is off, or the app runs off-boat (pre-race study) | Pre-race forecast review, off-boat planning, race-day fallback if instruments fail | Modelled wind; coarse on small lakes; the Wind Calibration Mode lets the crew offset the model against observation if needed |

The roadmap simplification:
- ~~Tier 1 MeteoSwiss historical stations~~ — no longer needed for race-day; still useful for post-race wind-context in Training app
- ~~Tier 3 Portable anemometer~~ — not needed, gWind covers this
- ~~Tier 5 separate WiFi gateway~~ — not needed, YDVR-04 includes this

### 5.4 What this unlocks for the app

With the YDVR-04 stream live to the phone, the Strategy tab transforms from "model-wind tactical app" to "live-instruments tactical app":

- **Real-time TWS and TWD** from gWind → Trim Coach panel (§3 of v5 plans) gets accurate live wind, not modelled wind
- **Real BSP from DST800** → true PPR computation (BSP vs polar target), independent of current/drift effects on SOG
- **Live wind shifts** → shift detection becomes reliable, alerts the crew to lifts and headers in real time
- **Polar calibration** → Training app can compute a *measured* polar over the season and compare to ORC; refine the per-POS performance factors (§1) with real data rather than the conservative 0.90/0.75/0.90 starting point

### 5.5 Implementation timeline (race-critical)

| Date | Task | Owner |
|---|---|---|
| Week of 22 May | YDVR-04 installation by yard | Yard |
| Install + bench test | Confirm WiFi broadcast works; verify SSID/password | Yard / owner |
| Install + 1–2 days | First on-water test — drive in marina, verify all instruments in stream | Owner |
| Install + 3–5 days | App integration — Claude Code adds "Live Instruments" mode reading YDVR-04 WiFi NMEA stream | Claude Code |
| 30 May (T5 dry run) | First end-to-end test with live instruments during racing on Lac Léman | Crew |
| 4 June (dock day) | Final verification; spare YDVR-04 microSD; phone WiFi configured | Crew |
| 6 June | Race day | — |

Fallback if the live integration isn't ready in time: race day still works on the model-ensemble path (current behaviour), and the YDVR-04 silently logs the entire race for post-race analysis regardless of whether the app reads its WiFi stream. Worst case for race day = same as current state; best case = significantly better tactical app.

---

## 6. Implications for the Bol d'Or 6 June 2026 race

This addendum does **not** change the build queue for the next 20 days. The Bol d'Or app remains scoped per PRD v4 plus the outstanding QA fixes in `docs/QA-fix-round1.md` (verified-outstanding subset: 5a, 5c, 6b, 7a, 7b, 7c, 11c, favicon, CORS proxy, plus the new variable `perfFactor(twa)` from §1 above).

Everything else in this addendum is post-race.

---

## 7. Open questions for future scoping

- **YDVR-04 install decision.** Hardware purchase + installation effort + timing.
- **Sister app naming and scope boundary.** Working name "Little Johnka Performance" or similar. Exact line between "race-day" and "training" features (e.g., does post-race debrief live in the race app or the training app?).
- **Shared library mechanics.** Vanilla JS module, npm package, or simple `<script src="lib.js">` import. Affects deploy story and dev experience.
- **Multi-boat support.** If the architecture is right, the sister app could in principle serve any boat (not just Little Johnka) by parameterising the polar table. Worth keeping in mind even if Little Johnka is the only user for now.

---

*Document version: 1.0 — 17 May 2026*
*Parent: PRD-v4.md*
*Source data: performance-review-2026-05.md*
