# Trim Coach Panel — Design Spec

**Status:** Design spec for QA round 2 Batch 4 (P1 #9). Hand to Claude Code as the brief.
**Date:** 17 May 2026
**Related:** `docs/QA-fix-round2.md` §2.3 (high-level scope), `docs/PRD-v5-addendum.md` §1 (variable `perfFactor`), `docs/performance-review-2026-05.md` (data source for the spec).

---

## 1. Purpose

A 4-person racing crew has a trimmer who constantly observes telltales, feels the boat, calls wind shifts, and tells the helm what to do. Little Johnka races with 2 core crew. The Trim Coach panel acts as the *instruments-and-observation* half of that missing trimmer — the half the app can credibly do without sensors that don't exist (telltales, sail shape, sea state are beyond reach).

Specifically, the panel surfaces four live observations derived from data the app already has (or will have after the calibration step), so the helm/tactician can act on numbers instead of guess:

1. Are we at polar speed?
2. Are we at the optimal angle for this wind?
3. Is the wind shifting on us?
4. Is a point-of-sail transition coming up?

This is not a "how to trim" manual — that lives elsewhere as static reference content if we ever build it. The Trim Coach is live observation only.

---

## 2. Placement

| Aspect | Choice | Why |
|---|---|---|
| Tab | Strategy | The race-day cockpit; this is where the crew looks during the race |
| Vertical position | Between "GPS Navigation" card (top) and "Race-course map" card | Above the fold on phone; immediately visible when entering Strategy tab on race day |
| Default state | **Collapsed in Planning mode, expanded in Live mode** | Don't crowd the screen pre-race; auto-open when GPS is on |
| Collapse persistence | localStorage key `trim_coach_collapsed_v1` | Crew preference survives reloads |

---

## 3. Modes

The panel has three modes, auto-detected, surfaced in the panel header with a small badge:

| Mode | Trigger | Data source | Behaviour |
|---|---|---|---|
| **Planning** | No GPS fix (or GPS disabled) | None | All four readouts shown as greyed-out placeholders; single overlay message: *"Enable GPS for live trim coaching."* |
| **Live** | GPS fix acquired, no Live Instruments connection | GPS for SOG/COG/heading; model wind ensemble for TWS/TWD (calibrated if Wind Calibration Mode is active) | All four readouts active. Header badge: `Model wind` (if no calibration) or `Calibrated wind` (if calibration active) |
| **Live + Instruments** | YDVR-04 WiFi connected (P2 — placeholder only for now) | gWind for TWS/TWD/AWS/AWA; DST800 for BSP; GPS for position; heading from NMEA 2000 PGN 127250 | Same readouts but using real measured TWS/TWD/BSP. Header badge: `Live instruments`. **Build the mode hook now (a stub function that returns false), wire up properly in P2** |

The header also shows a small "calibrated" pill when Wind Calibration is active (reuses the same badge style from §2.2 in QA round 2).

---

## 4. Layout

A single card with a header row and four readout rows. Mobile-first; on wider screens the four readouts can flow into two columns.

```
┌───────────────────────────────────────────────────────────────┐
│  TRIM COACH                       [ Live · Model wind ]   [▼] │   ← header
├───────────────────────────────────────────────────────────────┤
│  PERFORMANCE             0.83 ▼                               │   ← readout 1
│  vs polar target         trending -4% over 2 min              │
├───────────────────────────────────────────────────────────────┤
│  ANGLE                   78° / target 85°                     │   ← readout 2
│  TWA vs max-speed angle  bear away 7° for more speed          │
├───────────────────────────────────────────────────────────────┤
│  WIND SHIFT              +8° right / 12 min                   │   ← readout 3
│  TWD trend (last 15 min) lifted — you can head up             │
├───────────────────────────────────────────────────────────────┤
│  POINT OF SAIL           Beam reach (95°)                     │   ← readout 4
│  transition ahead        spinnaker faster from 105°           │
└───────────────────────────────────────────────────────────────┘
```

**Mobile (default phone width):** single column, big numbers (24-32px), high contrast.
**Tablet/desktop (≥768px):** 2 columns × 2 rows for the four readouts. Header spans both columns.

**Night mode:** dim ambers and greens to muted versions; reds stay vivid; greys become near-black.

---

## 5. The four readouts — specifications

Each readout is updated every **5 seconds** in Live mode. All readouts use the **calibrated wind** when Wind Calibration Mode is active (i.e., always read via the existing `calibrateWind()` function).

### 5.1 Readout 1 — Performance (PPR)

**Label:** `PERFORMANCE` (small caps, secondary colour)
**Subtitle:** `vs polar target`

**Main value:** A number — 30-second rolling-mean PPR.

**Algorithm:**
```
Every 5 seconds:
  twd = calibrateWind(model_tws, model_twd).dir
  tws = calibrateWind(model_tws, model_twd).speed
  twa = abs((heading - twd + 540) % 360 - 180)
  target_btv = interpPolar(tws, twa) * perfFactor(twa)      // uses Batch 1 fn
  ppr = SOG / target_btv
  push ppr to rolling buffer (max 24 samples = 2 min @ 5s)

mean30s = mean(buffer.last(6))                              // 6 samples = 30s
mean2m  = mean(buffer)                                      // full 24 = 2min
trend_pct = ((mean30s - mean2m) / mean2m) * 100
```

**Display:**
- Main number: `mean30s` to 2 decimal places (e.g., `0.83`)
- Trend arrow: ▲ if `trend_pct > +2`, ▼ if `< -2`, ▬ otherwise
- Sub-text: `trending +X% over 2 min` (omit if `|trend_pct| < 1`)

**Colour:**
- Green (#2dd4a8) if `mean30s >= 0.85`
- Amber (#fbbf24) if `0.70 <= mean30s < 0.85`
- Red (#ef4444) if `mean30s < 0.70`

**Empty state:** if buffer < 3 samples (i.e., panel just opened), show `—` with caption *"warming up"*.

### 5.2 Readout 2 — Angle (TWA vs max-speed)

**Label:** `ANGLE`
**Subtitle:** `TWA vs max-speed angle`

**Main value:** `current_twa° / target X°`

**Algorithm:**
```
twa = current TWA (as computed above)
twa_signed = ((heading - twd + 540) % 360 - 180)            // keep sign for L/R
pos = (twa < 60) ? 'upwind' : (twa < 130 ? 'reach' : 'downwind')

// Target angle by point of sail
if pos == 'upwind':
  target_twa = P[nearest TWS bucket].beatA
elif pos == 'downwind':
  target_twa = P[nearest TWS bucket].runA
else:  // reach — find TWA at peak BTV in this TWS row
  bucket = P[nearest TWS bucket]
  i = argmax(bucket.btv)
  target_twa = bucket.twa[i]

delta = twa - target_twa                                    // signed
```

**Display:**
- Main value: `[current]° / target [target]°`
- Sub-text:
  - If `pos == 'upwind'` and `delta > 5`: *"foot away X° for VMG"*
  - If `pos == 'upwind'` and `delta < -5`: *"pinching — head up X° for groove"*
  - If `pos == 'reach'` and `|delta| > 5`:
    - if `delta > 0`: *"bear away X° for more speed"*
    - else: *"head up X° for more speed"*
  - If `pos == 'downwind'` and `delta > 5`: *"by-the-lee — head up X°"*
  - If `pos == 'downwind'` and `delta < -5`: *"hot angle — bear away X° for VMG"*
  - If `|delta| <= 5`: *"in the groove"*

**Colour:**
- Green if `|delta| <= 5`
- Amber if `|delta| <= 15`
- Red if `|delta| > 15`

### 5.3 Readout 3 — Wind shift (TWD trend)

**Label:** `WIND SHIFT`
**Subtitle:** `TWD trend (last 15 min)`

**Main value:** `±X° [right|left] / Y min`

**Algorithm:**
```
Every 30 seconds, capture (now, twd) into a circular buffer (max 30 samples = 15 min).

current_twd = latest sample
oldest_twd = first sample (≤15 min old)
window_min = (now - oldest.ts) / 60_000

shift_signed = (current_twd - oldest_twd + 540) % 360 - 180   // -180..+180
// Positive = wind shifted right (clockwise); negative = left (anticlockwise)
```

**Display:**
- If `|shift_signed| < 3`: main value = `steady`, sub-text empty
- Else:
  - Main: `+8° right / 12 min` (or `-5° left / 14 min`)
  - Direction arrow: ↻ for right, ↺ for left
  - Sub-text — depends on current point of sail:
    - Upwind, right shift on starboard tack: *"lifted — you can head up"*
    - Upwind, right shift on port tack: *"headed — prepare to tack"*
    - Upwind, left shift: invert above
    - Reach/downwind: just *"wind shifted [direction] X°"*
    - Tack determination: `tack = (twa_signed > 0) ? 'starboard' : 'port'`

**Colour:**
- Green if `|shift_signed| < 5` (steady)
- Amber if `5 <= |shift_signed| < 15` (moderate shift, tactical interest)
- Red if `|shift_signed| >= 15` (major shift, must act)

**Empty state:** if buffer < 2 samples or `window_min < 2`, show `gathering data` with sub-text *"need 2+ min of GPS"*.

### 5.4 Readout 4 — Point of sail (transition ahead)

**Label:** `POINT OF SAIL`
**Subtitle:** `transition ahead`

**Main value:** `[POS name] ([current TWA]°)`

**Algorithm:**
```
twa = abs current TWA
pos =
  twa < 50  ? 'Close-hauled' :
  twa < 75  ? 'Close reach' :
  twa < 100 ? 'Beam reach' :
  twa < 130 ? 'Hot reach' :
  twa < 155 ? 'Broad reach' :
              'Run'

// Sail crossover from polar (jib vs spinnaker)
crossover_twa = first TWA at current TWS where P_SYM.btv > P_JIB.btv
// For TWS 6-10 this is ~100-105°; for TWS 14+ it's ~110°

// Distance to next transition
thresholds_with_labels = [
  (50, 'Close reach'),
  (75, 'Beam reach'),
  (crossover_twa, 'spinnaker faster'),
  (130, 'Broad reach'),
  (155, 'Run')
]
next = first threshold > twa
```

**Display:**
- Main: `[pos] ([twa]°)`
- Sub-text:
  - If `next exists` and `(next.twa - twa) < 10`: *"[next.label] in X°"* — e.g., *"spinnaker faster in 8°"* or *"Beam reach in 3°"*
  - If TWA is near `crossover_twa` (within ±5°) and current sail is jib: *"prepare spinnaker hoist"*
  - Otherwise: *"steady [pos]"*

**Colour:**
- Amber if within 10° of a transition (preparation prompt)
- Otherwise neutral (text colour, no fill)

---

## 6. Header — mode badge, calibration badge, collapse toggle

The header is a single row with three groups:

| Position | Content | Behaviour |
|---|---|---|
| Left | `TRIM COACH` title | Static |
| Middle | Mode badge: `Live · Model wind`, `Live · Calibrated wind`, `Live · Instruments`, or `Planning` | Reflects current data source |
| Right | Collapse toggle [▼] / [▶] | Tap to fold/unfold; persists in localStorage |

---

## 7. Data flow & integration

### 7.1 New functions to add

```javascript
// Rolling buffers
var trimCoachBuffers = {
  ppr: [],       // last 24 samples @ 5s = 2 min
  twd: []        // last 30 samples @ 30s = 15 min
};

// Main tick — bind to existing GPS update interval (already runs)
function tickTrimCoach() {
  if (!gpsLastFix) { renderTrimCoachPlanning(); return; }
  if (!ensembleData) return;  // wait for wind

  // ... compute PPR, TWA, shift, POS per algorithms above ...
  renderTrimCoach({mode, ppr, trend, twaDelta, shift, pos, transitionAhead});
}

setInterval(tickTrimCoach, 5000);

// Also seed the TWD buffer separately every 30s
setInterval(captureTwdSample, 30000);
```

### 7.2 Hooks into existing code

- **Reuse `calibrateWind()`** — already wired in from Batch 3
- **Reuse `interpPolar()`** — existing function for polar lookup
- **Reuse `perfFactor(twa)`** — added in Batch 1, must be applied to target_btv
- **Reuse `P`, `P_JIB`, `P_SYM`** tables for crossover detection
- **Hook GPS position updates** — the existing `watchPosition` callback already runs on GPS fix; add a single line to seed `gpsLastFix` for the Coach
- **Hook wind data refresh** — when `fetchWind()` completes, no action needed (the tick reads latest `ensembleData` on its own cadence)

### 7.3 Stub for Live Instruments mode

Build the mode detector now, leave it returning false:

```javascript
function isLiveInstrumentsActive() {
  return false;   // P2 — wired in when YDVR-04 lands
}

// Then in tickTrimCoach:
var mode = isLiveInstrumentsActive() ? 'instruments' :
           gpsLastFix ? 'live' : 'planning';
```

This means the P2 work (Batch 6 once YDVR-04 is installed) only needs to:
1. Replace `isLiveInstrumentsActive()` with a real check
2. Replace the data-source reads in `tickTrimCoach` with NMEA sources when instruments mode is active

No other refactor needed.

---

## 8. Acceptance criteria

Build is complete when:

1. **Trim Coach card visible** on the Strategy tab, between GPS Navigation and Race-course map cards
2. **Planning mode renders correctly** when GPS is off — single "Enable GPS for live trim coaching" message, four greyed readouts behind it
3. **Live mode activates automatically** when GPS fix is acquired
4. **PPR readout** updates every 5 seconds; shows a number between 0.0 and ~2.0; trend arrow correct vs the rolling mean; color correct vs threshold
5. **Angle readout** shows current TWA and target TWA; sub-text guidance changes based on point of sail
6. **Wind-shift readout** updates as TWD samples accumulate; shows `gathering data` for the first 2 min; shows a signed shift in degrees afterward
7. **Point-of-sail readout** correctly labels the current PoS; correctly flags upcoming transitions within 10° of a threshold
8. **Mode badge** correctly reflects model-wind / calibrated-wind / planning (instruments mode unreachable for now is fine)
9. **Collapse/expand** works and persists across reloads
10. **No console errors** during normal operation (Planning ↔ Live transitions, calibration apply/clear, page reloads)
11. **Mobile layout** — readable on iPhone in portrait; numbers ≥ 24px; one column

---

## 9. Out of scope (intentionally)

- Alert sounds / haptic feedback — race-day noise overrides anything subtle; no need to overdesign
- User-configurable thresholds — the values in §5 are baked in for v1; can be made configurable in a later iteration if the crew wants to tune
- Historical PPR chart — that lives in the future Performance Memory feature, not here
- Per-tack loss readout — needs ≥1 Hz data (Kwindoo is 0.05-0.20 Hz); deferred to YDVR-04 era
- Telltale interpretation — impossible without sensors that don't exist
- Heel-angle readout — until YDVR-04 + a heel sensor, no data source

---

## 10. Approximate sizing

- New CSS: ~80 lines (one card, four rows, two responsive breakpoints)
- New HTML: ~30 lines (header + 4 readout rows + mode badges)
- New JS: ~250 lines (tick fn, two rolling buffers, four readout computers, render fn, planning-state handler, mode stub)
- Hooks into existing code: ~5 line additions in 3 places (GPS callback, fetchWind callback, init block)

**Total estimate: ~365 lines added to `index.html`, ~2 days Claude Code time.**

---

## 11. Suggested commit message

```
QA round 2 — Fix 9: Trim Coach panel (Strategy tab)

Adds a four-readout live coaching panel on the Strategy tab:
- PPR with 30s/2min rolling trend
- TWA vs max-speed target angle
- Wind shift (last 15 min)
- Point-of-sail transition ahead

Modes: Planning (no GPS), Live (GPS+model wind, calibrated when
applicable), Live+Instruments (stubbed for P2 / YDVR-04).

Reuses calibrateWind, interpPolar, perfFactor, P/P_JIB/P_SYM.
Tick every 5s on GPS update; TWD samples every 30s for shift trend.
Mobile-first single column; 2x2 grid on ≥768px.

Spec: docs/trim-coach-design.md
```
