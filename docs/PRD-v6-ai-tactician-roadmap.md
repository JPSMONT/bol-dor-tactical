# PRD v6 Addendum — AI Tactical Navigator: Phased Roadmap

**Date:** 24 May 2026 · **Owner:** Joao Monteiro (joao@pinto.ventures) · **Boat:** Little Johnka (CYD 27 ORC)
**Status:** Direction-setting roadmap. Sequences the "AI Tactical Navigator & Performance Intelligence System" vision PRD against the current app and its real dependencies. Supersedes nothing — extends `PRD-v4.md` / `PRD-v5-addendum.md`.

> **Build status (24 May 2026):** Phase 0 (Race cockpit) ✅, Phase 1.5 (in-race maneuver-loss tracker) ✅, Phase 2 v1 (in-app Debrief) ✅ — all shipped, behind the venue system. Phase 1 (live instruments) ⏸ **parked** pending hardware (`PRD-v6-live-instruments-spec.md` / `live-instruments-handoff-2026-05-24.md`). Phases 3–4 future.

> Guiding sentence from the vision: **compress complexity into actionable intent.** The skipper should not interpret data — the system interprets it for the skipper.

---

## 1. Where we are vs. where we're going

**Today (shipped):** a single-file PWA driven by *model* wind (Open-Meteo 4-model ensemble + MeteoSwiss station obs), phone GPS + compass, ORC polars (`P_JIB`/`P_SYM`), a Trim Coach (PPR / TWA-vs-target / wind-shift / point-of-sail) computed on model/calibrated wind, IndexedDB GPS-track recording, venue profiles (Bol d'Or / Zugersee), and an offline service worker.

**The vision:** an AI tactical co-pilot across three modes — **Race** (minimal, event-driven alerts), **Training** (conversational coaching + maneuver scoring), **Debrief** (replay, pattern recognition, competitor analysis).

**The gap is the data layer, not the UI.** ~70% of the vision's intelligence (polar efficiency, maneuver cost, measured wind state, performance delta, tactical bias) cannot be made *true* until two things exist that don't today:

1. **Live boat instruments** on the WiFi (measured TWS/TWA/AWA/BSP/heel/VMG). **Correction (24 May 2026):** the YDVR-04 is a *recorder*, not a live bridge — live data comes from a Wi-Fi gateway's WebSocket feed (read the **YDWG-02 gateway directly** via its Web Gauges, cheapest; or via **Signal K**). A browser can't use the gateway's raw TCP/UDP ports. See `PRD-v6-live-instruments-spec.md`.
2. **Logged race/training data** — the only fuel for the ML and maneuver-cost ambitions.

Everything below is sequenced so the UI we build now *upgrades gracefully* from model-wind approximations to instrument truth the moment those land. The `isLiveInstrumentsActive()` stub already exists for this switch.

---

## 2. Guiding principles

- **One mode-aware Dashboard, not many pages.** Planning before the gun → glanceable Race cockpit during → Debrief summary after. The app already tracks race-state (pre/live/past); the cockpit becomes its live face.
- **Trust economics rule everything.** Start the AI on *verifiable, low-stakes* metrics the crew can sanity-check (polar %, wind shifts they can feel). Earn trust, then go prescriptive. One confident-but-wrong call mid-race and the skipper switches it off for good.
- **Bulletproof cockpit, separate analysis brain.** The thing that must work at 02:00 in the Haut-Lac shares no failure mode with experimental tactical models.
- **Graceful upgrade.** Every tile declares its data source (live / model / unavailable) and improves as sources come online, rather than waiting for the full system.
- **Augment, don't override, on hard calls.** On a thermal lake, model wind is weak — so the AI supports the crew's eyes, it does not replace their judgment (see Risks).

---

## 3. The critical path: the data layer

| Enabler | What it unlocks | Status / blocker |
|---|---|---|
| **Live instruments (Layer 1)** | Real polar efficiency, measured wind state, maneuver detection, instrument-grade Trim Coach | **Linchpin.** Read a WebSocket feed — **YDWG-02 gateway-direct** (its Web Gauges, cheapest) or **Signal K** (robust); the gateway's raw TCP/UDP ports aren't browser-readable. **YDVR-04 is the Debrief source** (SD), not live. See `PRD-v6-live-instruments-spec.md` |
| **Telemetry logging from day one** | The maneuver-cost database + all ML; Debrief mode | GPS track logging exists; extend to full telemetry once YDVR is in. Log every race *and* training session |
| **Live competitor positions** | Tactical-risk (lane / dirty air / compression), competitor modeling | Only TracTrac/manage2sail link-out today; real feed needs integration + the regatta actually being tracked |

The order matters: **YDVR first** (unlocks the most, cheapest), **logging in parallel** (cheap, compounding), **competitor data last** (hardest, externally gated).

---

## 4. The Race-mode cockpit (the home display)

Five tiles, each tagged by data source. Feasibility today:

| Tile | What it truly needs | Buildable now? |
|---|---|---|
| **Polar efficiency %** | Live BSP + measured TWS/TWA | **Approx now** (GPS SOG vs polar target at model wind). Real % at Phase 1 (YDVR) |
| **Wind state** (oscillating / persistent / building) | Wind time-series | **Now** from model + stations + calibration; much better with boat-measured TWD (Phase 1) |
| **Big nav** (heading, next mark, DTW, VMG) | GPS + course | **Now** — fully buildable |
| **Tactical bias** (which side / pressure) | Live wind field or competitor positions | **Weak now** (model gradient across grid points only). Real at Phase 3. Show uncertainty explicitly |
| **Maneuver value** (tack / hold) | Maneuver-cost DB + side gain | **Crude now** (polar VMG only). Real at Phase 2 (after logging) |
| **Tactical risk** (lane / dirty air) | Live competitor positions | **Not now** — Phase 3 |

Design note: the cockpit must be glanceable in <1s — big type, high contrast, glove- and sunlight-friendly, night-vision dark, minimal chrome. Detail lives one tap down, never on the glance surface.

---

## 5. Phased roadmap (sequenced by dependency)

### Phase 0 — Mode-aware cockpit (now → 30 May dry run)
**Goal:** make the Dashboard the skipper's live display, with everything we can power today.
**Deliverables:** Planning↔Race↔Debrief mode switch on the existing race-state; Race cockpit with Big nav + Polar-efficiency (approx) + Wind state + a *humble* Tactical-bias tile (with visible confidence) + Maneuver-value (crude); extend logging scaffold; works in both venues.
**Dependencies:** none (model wind + GPS + polars).
**Exit criteria:** glanceability + readability validated on the water at the Goldschäkel (30 May); no regression to the bulletproof offline cockpit.

### Phase 1 — Live instruments (Signal K / gateway — hardware decision)
**Goal:** turn approximations into instrument truth.
**Deliverables:** Layer-1 NMEA ingestion (the PGNs above); real polar efficiency %, measured wind state, instrument-backed Trim Coach; the cockpit tiles flip from "model" (amber) to "live" (green).
**Dependencies:** Signal K server (or YDWG-02 gateway) + WebSocket — see `PRD-v6-live-instruments-spec.md`. (YDVR-04 is the Debrief source, not live.)
**Exit criteria:** instrument data stable on the water. *Assumption/risk: may not fully land before 6 June — fallback is the current model path (no regression), and the YDVR still logs to SD for post-race regardless.*

### Phase 2 — Debrief + maneuver intelligence (post-race)
**Goal:** learn from logged data.
**Deliverables:** Debrief mode — **v1 shipped in-app 24 May** (post-race summary, polar-% trend, maneuver table from the app's own logs). Next: YDVR-04 SD-card import (`.DAT`→CSV) for instrument-grade data + a maneuver-cost database by wind strength (vision §9).
**Dependencies:** logged telemetry from Phases 0–1.
**Exit criteria:** a real per-crew maneuver-cost profile that the Race-mode Maneuver-value tile can consume.

### Phase 3 — Tactical bias + training coaching
**Goal:** prescriptive tactics + crew development.
**Deliverables:** tactical-bias engine (needs a live competitor feed — TracTrac/AIS — and/or much better on-water wind sensing); Training mode coaching (live maneuver scoring, crew-sync feedback).
**Dependencies:** competitor data source; trustworthy Phase-1/2 foundations.
**Exit criteria:** bias calls validated against actual race outcomes before they're ever spoken.

### Phase 4 — Voice + personalized ML
**Goal:** lowest-cognitive-load delivery + lake-specific learning.
**Deliverables:** AI audio assistant (alerts only when expected value > cognitive cost); personalized/lake-specific tactical model ("right shore gains after 15:00 under this thermal structure").
**Dependencies:** everything above proven. Voice is a *trust amplifier* — it ships last, not first.

---

## 6. Architecture evolution

- **Real-time cockpit stays the PWA.** It must remain offline-resilient and dependency-light. No experimental code in the race-day path.
- **In-app data-fusion layer** stays thin: normalize/smooth GPS + (later) NMEA + model wind into one "truth" object the tiles read.
- **Logging → IndexedDB now**, with an export path. The race-day app writes logs; it does not analyze them.
- **Analysis/ML lives offline** in the `analyze_all.py` lineage (Python), not in the cockpit. If a hosted history/ML service is ever needed, it's a separate component the PWA reads from when online — never a race-day dependency.

---

## 7. Risks & mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Model wind weak on thermal lakes (AROME under-reads 5–6 kt) | Tactical-bias tile misleads | Show confidence; lean on the calibration tool + crew eyes; don't speak bias until instrument/fleet-backed |
| YDVR-04 install slips | Phase 1 stalls | Cockpit works on the model path regardless; YDVR logs to SD for post-race either way |
| Trust erosion from a wrong call | Skipper stops using it | Verifiable metrics first; prescriptive + voice only once validated against outcomes |
| AI scope destabilizes the cockpit | Race-day failure | Keep ML/debrief offline + separate; cockpit changes gated on no-regression to offline reliability |
| Competitor feed unavailable | Tactical-risk tile empty | Graceful "needs live fleet" state; never a hard dependency |

---

## 8. Success metrics (how we'll actually measure)

Tie the vision's §13 to the logging layer: **polar efficiency %** trend across races; **maneuver loss** (sec / boat-lengths) by wind band, trending down; **lane/positioning quality** in Debrief; and the cognitive metric — does the skipper *trust and use* the cockpit at night, in breeze. Without logging (Phase 0+), none of these are measurable — which is why logging is non-negotiable from day one.

---

## 9. Open decisions (need Joao's input)

1. **Architecture:** keep evolving the single-file PWA, or modularize before Phase 2? (Recommendation: stay single-file through Phase 1; reassess for Debrief/ML.)
2. **History/ML home:** purely local (IndexedDB + offline Python) vs. a small hosted service later for cross-race learning.
3. **Competitor data:** how hard to pursue a live TracTrac/AIS feed vs. accept link-out until it proves reliable.
4. **Pre- vs post-Bol d'Or investment:** how much cockpit work to attempt before 6 June vs. treat the Bol d'Or as a data-collection run and build the intelligence after.
5. **Voice provider / on-device vs cloud** — deferred to Phase 4, but affects offline behaviour.
