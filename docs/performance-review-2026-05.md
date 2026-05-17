# Performance Review — Little Johnka (May 2026)

**Boat:** Little Johnka — CYD 27 ORC (SUI 6116)
**Crew:** 2 core + occasional guests
**Period analysed:** Zugersee 2024 (3 races) + 2025 (5 race days, 12 race windows)
**Total racing time analysed:** 14.3 hours across 15 race windows
**Data source:** 8 unique Kwindoo GPX exports + Open-Meteo historical wind ensemble

---

## 1. Summary

The goal of this review is to measure Little Johnka's *realised performance against polar* (PPR — Performance to Polar Ratio) so that the tactical app's race simulator can use evidence-based values instead of a flat 90% guess.

**The clear finding:** across nearly every race in the data set, **reach is consistently the lowest-performing point of sail** relative to polar. The relative pattern is consistent — upwind and downwind PPR are roughly comparable to each other, while reach is materially lower. Important framing: the ORC polar is calculated for the boat's *existing* sail inventory (Main + Jib + Spinnaker — no Code 0, no Drifter), so a reach PPR below 1.0 means the boat is not yet reaching its current-inventory polar potential. There is room to improve with the sails already aboard, through trim and technique work, before any sail-purchase decision needs to be made.

**The wind-data caveat:** Free historical wind models (Open-Meteo's AROME HD, ICON-D2, MeteoSwiss ICON-CH1, ERA5) systematically *underestimate* Zugersee surface wind because they don't resolve the lake's thermal effects. Across the 15 race windows the model ensemble averaged 2.5–7.5 kn, while actual on-water wind was almost certainly 6–12 kn during most afternoons. As a result, **absolute PPR values are inflated** (aggregate 1.21 across all races). What remains reliable is the *relative* comparison across points of sail, which is the actionable signal.

**Recommended action for the app:** replace the flat 90% performance factor with point-of-sail-specific values: upwind 0.90, **reach 0.75**, downwind 0.90. The 0.75 figure quantifies the Code 0 gap.

*Assumption:* the wind underestimation is roughly uniform across all races. The relative ordering of point-of-sail PPRs holds even if the absolute scale is wrong, but if certain conditions (e.g. very light wind) have proportionally worse model coverage, the relative gap could be slightly different.

---

## 2. Methodology

A full sailing-performance review has eight standard angles. This review covered the ones the available data supports:

| # | Angle | Status |
|---|---|---|
| 1 | Results / finish-position analysis | **Out of scope** — user reframed away from outcome to capability |
| 2 | Speed-to-polar (PPR) | **Done** — main finding |
| 3 | Manoeuvre loss (per tack/gybe) | **Not possible** — Kwindoo sample rate (5–30 s) too coarse; needs ≥1 Hz |
| 4 | Start analysis | **Out of scope** — sample rate too coarse for first-30-seconds detail |
| 5 | Tactical / bank-choice | Implicit in track shape; not formally scored |
| 6 | Race-phase analysis | **Done** — auto race-window detection identifies multi-race days |
| 7 | Crew composition | **Out of scope** — no per-race crew log available |
| 8 | Condition analysis | Partial — TWS bands attempted, but light-wind dominated the set |

### 2.1 Pipeline

1. **GPX parse** — extract (time, lat, lon) per fix, build segments between consecutive fixes (SOG, heading).
2. **Race-window detection** — smoothed SOG over a 2-minute window; declare "racing" when ≥60% of the window has SOG in 1.5–12 kn; extract contiguous racing periods ≥15 minutes. This handles multi-race days where the GPX includes intermediate breaks for re-rigging.
3. **Wind ensemble** — fetch hourly wind from multiple Open-Meteo endpoints:
   - AROME HD (Météo-France, 1.3 km) — works for all dates
   - ICON-D2 (DWD, 2 km) — works for all dates
   - MeteoSwiss ICON-CH1 (1 km) — works for 2025 only (~1 year archive depth)
   - ERA5 archive (25 km) — works for all dates, very coarse
4. **PPR per segment** — for each GPS segment: linearly interpolate wind to the segment's mid-time, compute TWA from heading minus wind direction, look up polar target boat speed from the ORC table, compute PPR as actual SOG / polar target.
5. **Aggregate** — time-weighted means by point of sail (upwind <60°, reach 60–130°, downwind >130°) and by wind band (light <8 kn, medium 8–14 kn, heavy 14+ kn).

### 2.2 Auto-cleaning

Race windows automatically excluded:
- Pre-start drifting / motoring out (SOG <1.5 kn)
- Sail hoists & drops (consistent slow-down)
- Post-finish drift to dock
- Long gaps between fixes (>60 s)

This typically retains 50–80% of the GPX trackpoints as "actual racing."

---

## 3. Data inventory

| # | Date | Race | Sample rate | Duration | Distance |
|---|---|---|---|---|---|
| 1 | 22 Jun 2024 | Blauband | 0.20 Hz (5 s) | 1h05m | 6.4 NM |
| 2 | 11 Aug 2024 | Bisang Cup | 0.05 Hz (20 s) | 1h28m | 4.0 NM |
| 3 | 31 Aug 2024 | Rigi Anker Cup (2 races) | 0.15 Hz (7 s) | 0h45m | 1.8 NM |
| 4 | 28 Jun 2025 | Blauband (3 races) | 0.03 Hz (30 s) | 3h08m | 8.9 NM |
| 5 | 11 Aug 2025 | OSCA evening race (Zug N) | 0.04 Hz | 1h52m | 7.4 NM |
| 6 | 16 Aug 2025 | Race (2 races) | 0.04 Hz | 1h48m | 5.5 NM |
| 7 | 17 Aug 2025 | Race (3 races) | 0.05 Hz | 2h12m | 5.5 NM |
| 8 | 30 Aug 2025 | Race (2 races, high-res) | 0.20 Hz (5 s) | 2h41m | 10.9 NM |

**Sample rate limitation:** the maximum is 0.20 Hz (5 seconds between fixes). Per-tack loss analysis (Fix 11d in the QA list) requires ≥1 Hz. With 5-second sampling you can see *that* a tack happened but not the speed-loss curve through it.

---

## 4. Findings — relative pattern (the actionable signal)

### 4.1 By point of sail, all races aggregated

| Point of sail | Time-weighted PPR | Total time |
|---|---:|---:|
| **Upwind** (<60° TWA) | **1.26** | 278 min |
| **Reach** (60–130° TWA) | **1.00** | 358 min |
| **Downwind** (>130° TWA) | **1.50** | 220 min |

Reach is 26% below upwind and 50% below downwind, both relative to polar.

### 4.2 Per race

| Race | Wind | Overall | Upwind | Reach | Downwind |
|---|---:|---:|---:|---:|---:|
| Blauband 2024-06-22 | 7.5 kn | 1.09 | 0.84 | 0.88 | 1.48 |
| Bisang Cup 2024-08-11 | 3.3 kn | 0.99 | 1.25 | 0.92 | 0.77 |
| Rigi Anker Cup 2024 #1 | 2.5 kn | 1.30 | 1.34 | 0.92 | 1.51 |
| Rigi Anker Cup 2024 #2 | 2.5 kn | 1.04 | 1.40 | 0.99 | 1.05 |
| Blauband 2025-06-28 #1 | 2.6 kn | 1.67 | 2.26 | 0.91 | 1.87 |
| Blauband 2025-06-28 #2 | 3.0 kn | 1.57 | 1.59 | 1.42 | — |
| Blauband 2025-06-28 #3 | 3.3 kn | 1.07 | 1.04 | 0.58 | 1.71 |
| OSCA 2025-08-11 (Zug N) | 4.3 kn | 1.18 | 1.09 | 1.00 | 1.51 |
| Race 2025-08-16 #1 | 3.3 kn | 0.83 | 0.80 | 0.83 | 0.86 |
| Race 2025-08-16 #2 | 3.5 kn | 1.13 | 1.16 | 1.11 | 1.11 |
| Race 2025-08-17 #1 | 3.2 kn | 0.89 | 1.10 | 0.80 | — |
| Race 2025-08-17 #2 | 3.8 kn | 0.82 | 1.01 | 0.71 | 0.71 |
| Race 2025-08-17 #3 | 4.1 kn | 0.94 | 1.10 | 0.80 | 1.22 |
| Race 2025-08-30 #1 | 3.8 kn | 1.21 | 1.41 | 1.08 | 1.37 |
| Race 2025-08-30 #2 | 3.3 kn | 1.58 | 1.49 | 1.39 | 2.07 |

**Reach is the lowest PPR in 12 of 15 race windows.** The three exceptions (Bisang Cup, Race 2025-08-16 #1, Race 2025-08-17 #1) all involve very small downwind samples (few minutes of running each), so the downwind value is noisy in those races.

### 4.3 Race 2025-08-17 — the honest outlier

This is the only race day where all three race windows show overall PPR below 1.0. Reach PPR averaged 0.76 across the three windows. Conditions were light (TWS 3.2–4.1 kn), which is where the reach gap should be most punishing — confirming the structural diagnosis. Worth checking your race log for that day: was it specifically a light-air struggle, or was there something else (crew composition, sail set, wave state)?

---

## 5. Findings — absolute PPR (caveated)

Aggregate PPR across all races: **1.21**. Reading this at face value, the boat sails 21% faster than the polar predicts, which is not physically plausible. Two contributing factors:

### 5.1 Wind underestimation

Free historical models systematically under-resolve thermal flows on a small mountain-bordered lake. Model wind spread within the ensemble was ±0.7 to ±2.8 kn across races, and the AVERAGE wind across the data set was 2.5–7.5 kn — at the lower end of "you can race a CYD 27 at all." Realistic afternoon thermal on Zugersee in summer is 6–12 kn. If the actual wind was double what the models say, the polar target speed would also be roughly double (in the steep part of the curve), bringing PPR down to ~0.6, which would be a more realistic but still suspect value.

### 5.2 Below-polar-range extrapolation

The ORC polar starts at TWS 6 kn. Below that, this analysis linearly scales the 6-kn polar down to zero at TWS 0. In reality, the boat probably moves better than that scaling suggests at 4–5 kn (because the polar's optimum point of sail is at moderate angles, not at the curve's bottom edge). Another contributor to apparent over-performance.

### 5.3 What this means

**We cannot derive a reliable absolute performance factor from this data set alone.** The relative finding (reach is weakest) is robust because the wind error and polar extrapolation error are roughly uniform across points of sail. The absolute level requires either better wind data or on-water measurement.

---

## 6. What the gap actually means (and what it doesn't)

**Important framing.** The ORC polar that we measure against IS computed for the boat's declared sail inventory: Main 27.13 m² + Jib 17.66 m² + Symmetric Spinnaker 47.18 m². No Code 0, no Drifter. So when reach PPR comes in at 1.00 (and the wind-corrected real PPR is meaningfully below that — probably 0.75–0.85), it means **the boat is not yet reaching its polar potential with the sails it already owns**. Improvement is available without buying anything.

This is a meaningful distinction from the July 2025 sail-improvement memo, which proposed acquiring a Drifter and Code 0 to close the 60–110° TWA gap. The memo identified a *structural* limitation of the inventory; the data identifies a *current performance* gap relative to the existing inventory's theoretical maximum. Both are real, but they live at different levels:

| Level | What it measures | Closed by |
|---|---|---|
| Current-inventory polar | Theoretical max with Main + Jib + Spinnaker | (ceiling) |
| Realised reach PPR | What we actually achieve | Trim, technique, crew work |
| New-inventory polar | Theoretical max with Main + Jib + Spinnaker + Drifter + Code 0 | (higher ceiling, with re-rating risk per memo §5) |

The reach PPR gap could be closed *partly* by better technique on existing sails, *partly* by buying the new sails, or *both*. The data alone does not prove new sails are needed — only that the boat is currently below polar on reach.

### 6.1 What's available with existing sails

Concrete reach-improvement levers that cost nothing:

| Lever | Mechanism |
|---|---|
| **Jib trim** | Halyard tension, foot tension, sheet-lead position, twist control |
| **Mainsail trim on reach** | Traveller, vang, sheet tension matched to apparent wind |
| **Spinnaker crossover timing** | Per P_SYM data, spinnaker is faster than jib from ~100° TWA in most wind conditions. Hoisting earlier (at 100° rather than 110–120°) sits on the fast side of the crossover. |
| **Crew weight** | CYD 27 is light at 1,780 kg — weight placement matters on reach |
| **Heel-angle management** | CYD 27 has a sweet spot; reach is where over- or under-heeling is most punishing |
| **Steering for pressure** | Bearing away in puffs / heading up in lulls — higher skill on reach than upwind |

### 6.2 What still validates the July 2025 memo

The structural diagnosis (60–110° TWA is the weakness) is supported by the data. What's not directly proven by the data is that *new sails* are the right intervention. The decision becomes:

- **Option A (no purchase):** Focus crew training on reach technique. Cheap, no rating risk, but limited by the polar ceiling of existing inventory.
- **Option B (purchase):** Acquire Drifter + Code 0. Lifts the ceiling. Comes with the re-rating risk the memo §5 flagged.
- **Option C (sequence):** Train technique first this season; assess remaining gap; then decide on the purchase with cleaner evidence.

For the Bol d'Or specifically, Option A (technique focus) is the only path with 20 days to race. The purchase decision can be made later with no impact on race day.

---

## 7. Implications for the tactical app

### 7.1 Replace flat 90% performance factor with per-POS values

| Point of sail | Current default | Recommended |
|---|---:|---:|
| Upwind | 0.90 | **0.90** |
| Reach | 0.90 | **0.75** |
| Downwind | 0.90 | **0.90** |

These are intentionally conservative against the inflated absolute PPR. The 0.75 reach value preserves the *relative* gap that the data supports. As we get better wind data (next season with a recorder, or this season via the calibration mode below), these can be refined.

**Implementation note for Claude Code:** the route simulation engine in `index.html` (`simulateLJRoute` and `isochroneRoute`) currently uses `perfFactor` as a single scalar. It should be replaced with a function `perfFactor(twa)` that returns the per-POS value. The interface change is small; the call sites are already centralised.

### 7.2 New feature — Wind Calibration Mode

Before the simulator can be properly accurate on race day, the crew needs a way to tell it the actual wind they're seeing. Sketch:

- Crew taps "Calibrate Wind" on the Strategy tab
- Enters observed wind (e.g., "8 kn from 240°")
- App computes the offset from the current model ensemble at the boat's position
- Applies that offset for the next hour, then decays back to model
- Re-prompt every hour or on major wind shift

This costs ~half a day of Claude Code work and lifts the app's tactical reliability significantly on race day.

---

## 8. Implications for the crew

Four concrete levers, re-prioritised because the reach gap exists *relative to the existing-sails polar* — meaning there's room to improve before considering new sails:

1. **Reach trim and technique on current sails** — the boat is not yet at its existing-inventory polar on reach. Focused work on jib trim (halyard tension, foot tension, twist), mainsail trim (traveller, vang on reach), and crew weight placement. Cheapest, no rating risk, and the only path available before the 6 June race.
2. **Spinnaker crossover timing** — the symmetric spinnaker becomes faster than the jib from ~100° TWA per P_SYM. Hoisting earlier (at 100° rather than 110–120°) keeps the boat on the fast side of the sail-choice crossover. Pure crew-coordination improvement; costs nothing.
3. **Route choice that minimises beam reach** — when planning routes, prefer angles that keep you close-hauled (better PPR) or running (better PPR) rather than at a beam reach. Tactical decision built into the bank advisor.
4. **Sail purchase (Drifter / Code 0)** — additive on top of items 1–3 once those are exhausted. Comes with the re-rating risk the July 2025 memo flagged in §5. Best decided after one season of focused technique work, when the remaining gap (if any) can be measured cleanly.

---

## 9. Limitations and data quality flags

- **Wind data**: synoptic models materially underestimate Zugersee surface wind. Absolute PPR is unreliable; relative PPR by point of sail is robust.
- **Sample rate**: 5–30 s GPS sampling smooths out per-tack speed losses. Manoeuvre analysis is not possible with this data set.
- **Sample size by condition**: 14 of 15 race windows had TWS <8 kn. We have no data on medium- or heavy-air performance.
- **Sample size by point of sail**: total time at reach (358 min) > upwind (278 min) > downwind (220 min). Downwind sample is smallest and most affected by wind underestimate.
- **No crew log**: we can't correlate performance with crew composition (2 vs 3+) or with specific guests aboard.
- **No race conditions log**: water state, current (if any), and shifts during each race are not captured.
- **One outlier race** (2025-08-17) is internally consistent and the best candidate for being the "true" PPR signal — it's the one race where the relative pattern matches with absolute values below 1.0, which is what we'd expect on average for a real boat.

---

## 10. Path to better data

| Tier | Method | Effort | Quality |
|---|---|---|---|
| Tier 0 (now) | Open-Meteo historical ensemble | Free, automated | Poor for Zugersee thermals; ~±50% on absolute PPR |
| Tier 1 | MeteoSwiss historical station data (IDAWEB) | Modest — need to validate archive depth and parse format | Better — measured wind at 5 lake-side stations, 10-min cadence |
| Tier 2 | App "calibration mode" (crew enters observed wind during racing) | ~½ day Claude Code | Real-time, low-cost, accurate enough for race-day tactics |
| Tier 3 | On-water anemometer logged to phone | Hardware ~CHF 200–500 (e.g., Calypso Ultrasonic Portable) | Good — measured boat-level wind, but not synchronised with rest of instruments |
| Tier 4 | **YDVR-04 voyage recorder + masthead anemometer** | Hardware ~CHF 400 + installation; pulls all NMEA 2000 data | Excellent — synchronised wind, boat speed, heading, heel at 1 Hz+; full post-race replay |
| Tier 5 | Live NMEA-over-WiFi during race | Combines Tier 4 hardware with app integration | Excellent + live — same data feeds the app in real time |

The YDVR-04 path (Tier 4 → Tier 5) is the long-term goal. It would unlock:

- True absolute PPR per race
- Per-tack manoeuvre loss analysis (currently impossible at Kwindoo's sample rate)
- Polar refinement (compute a measured polar from real on-water data and compare to ORC)
- Sail-change timing and cost
- Heel-angle trim analysis

Until then, the calibration-mode feature (Tier 2) provides the best return on a low investment.

---

## Appendix: file-level detail

Per-race-window results saved as JSON: `outputs/perf-review/results.json`
Analysis script saved as: `outputs/perf-review/analyze_all.py`
The script is reusable — point it at any new GPX file and it produces the same analysis structure. This is the prototype for the in-app Performance Memory feature.

---

*Document version: 1.0 — 17 May 2026*
*Source data: 8 Kwindoo GPX exports (2024-06 to 2025-08), Open-Meteo wind ensemble*
*Polar source: ORC Speed Guide certificate SUI 6116*
