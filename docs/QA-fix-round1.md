# QA Fix Round 1 — Polar Data & Race Sim Accuracy

## Context
QA testing revealed the polar diagram isn't rendering, and the race sim estimates are too optimistic (13h21m for ~70 NM). Root cause: the code uses a single "BestPerf" curve per TWS but the ORC Speed Guide has TWO separate curves — Jib (headsail 17.66 m²) and Symmetric spinnaker (47.18 m²). The BestPerf envelope hides sail-change costs and transition penalties.

The ORC Excel data is at: `../mnt/uploads/ORC Speed Angles Litlle Johka Table.xls`
The ORC Speed Guide PDF is at: `../mnt/uploads/Speed Guide for Little Johnka (1).pdf`

## Fix 1: POLAR DIAGRAM NOT RENDERING (P1 Bug)
The Polars tab (v1) shows the grid and angle labels but no speed curves are drawn on the canvas. The `drawPolar()` function is called when tab 1 is shown (line 686). Debug and fix so the polar curves render correctly.

**New requirement:** Draw TWO curves per TWS — one blue (Jib) and one green (Spinnaker), matching the ORC Speed Guide colour convention. Show the crossover point where spinnaker becomes faster than jib.

## Fix 2: SPLIT POLAR DATA INTO JIB + SPINNAKER
Replace the single `var P` object with two objects: `var P_JIB` and `var P_SYM`. Keep `var P` as the BestPerf envelope for backward compatibility (VMG calculator, strategy advisor).

Here is the complete Jib data extracted from the ORC certificate:

```javascript
var P_JIB = {
  6:  {twa:[42,52,60,70,75,80,90,110,120,135,150,165,180], btv:[4.74,5.32,5.60,5.78,5.81,5.82,5.77,5.21,4.74,3.93,3.38,3.12,3.00]},
  8:  {twa:[40.5,52,60,70,75,80,90,110,120,135,150,165,180], btv:[5.36,6.03,6.26,6.40,6.43,6.45,6.44,6.11,5.73,4.94,4.39,4.09,3.95]},
  10: {twa:[39.8,52,60,70,75,80,90,110,120,135,150,165,180], btv:[5.54,6.21,6.42,6.60,6.67,6.73,6.79,6.56,6.35,5.80,5.27,4.96,4.81]},
  12: {twa:[40.1,52,60,70,75,80,90,110,120,135,150,165,180], btv:[5.63,6.28,6.49,6.69,6.78,6.87,7.05,6.90,6.71,6.37,6.04,5.76,5.60]},
  14: {twa:[40.1,52,60,70,75,80,90,110,120,135,150,165,180], btv:[5.74,6.34,6.53,6.74,6.84,6.95,7.21,7.27,7.05,6.74,6.52,6.35,6.24]},
  16: {twa:[40.5,52,60,70,75,80,90,110,120,135,150,165,180], btv:[5.78,6.40,6.61,6.80,6.88,6.99,7.31,7.67,7.45,7.11,6.89,6.74,6.65]},
  20: {twa:[42.4,52,60,70,75,80,90,110,120,135,150,165,180], btv:[5.75,6.35,6.60,6.88,7.01,7.16,7.40,8.14,8.30,8.01,7.75,7.56,7.44]}
};
```

Here is the complete Spinnaker data:

```javascript
var P_SYM = {
  6:  {twa:[60,70,75,80,90,110,120,135,150,165,180], btv:[4.10,4.85,5.13,5.35,5.64,5.65,5.48,4.92,4.09,3.43,3.22]},
  8:  {twa:[60,70,75,80,90,110,120,135,150,165,180], btv:[5.00,5.67,5.90,6.07,6.34,6.50,6.41,6.01,5.19,4.46,4.22]},
  10: {twa:[60,70,75,80,90,110,120,135,150,165,180], btv:[5.31,5.94,6.15,6.30,6.55,6.89,6.89,6.60,6.09,5.38,5.13]},
  12: {twa:[70,75,80,90,110,120,135,150,165,180], btv:[5.96,6.18,6.35,6.66,7.14,7.36,7.06,6.62,6.17,5.95]},
  14: {twa:[110,120,135,150,165,180], btv:[7.37,7.68,7.60,7.06,6.65,6.51]},
  16: {twa:[110,120,135,150,165,180], btv:[7.47,7.97,8.25,7.57,7.07,6.92]},
  20: {twa:[120,135,150,165,180], btv:[8.16,9.40,8.86,8.10,7.88]}
};
```

**Key point:** The spinnaker data starts at higher TWA angles as wind increases (at TWS 20, spinnaker only helps from 120° onwards). This is because the jib is faster at reaching angles in strong wind.

The crossover angles (where Sym becomes faster than Jib) are approximately:
- TWS 6-8: ~100°
- TWS 10-12: ~105°  
- TWS 14+: ~110°

## Fix 3: RACE SIM REALISM ADJUSTMENTS
The race sim at 13h21m is too optimistic for a 2-crew CYD 27 on a ~70 NM overnight race. Add these corrections:

### 3a. Performance factor
Add a "Performance %" slider to the sim card (default: 90%, range 75%-100%).
Multiply all BTV lookups by this factor. ORC polars assume flat water, perfect trim, optimal crew work. 90% is realistic for a good 2-person crew; 85% for night sailing or rough conditions.

### 3b. Sail change penalty  
When the sim detects a crossover from Jib→Spinnaker or Spinnaker→Jib, add a time penalty:
- Spinnaker hoist: 4 minutes (2-person crew)
- Spinnaker drop: 3 minutes
- During the change, boat speed = 60% of target

Track number of sail changes in the sim stats output.

### 3c. Tacking/gybing penalty
When the sim changes course by more than 30° in a single step:
- Tack (upwind): 45 seconds at 40% speed
- Gybe (downwind with spinnaker): 60 seconds at 50% speed
- Gybe (downwind with jib): 30 seconds at 60% speed

### 3d. Show sail type in sim
When displaying sim results or the simulated track, indicate which sail is active at each point (Jib or Spinnaker). Use blue for Jib legs and green for Spinnaker legs on the map track.

## Fix 4: POLAR DIAGRAM VISUAL IMPROVEMENTS
On the Polars tab:
- Draw Jib curves in blue, Spinnaker curves in green (matching ORC convention)
- Show crossover point with a small marker
- Add legend: "Blue = Jib 17.66 m² | Green = Spinnaker 47.18 m²"
- The existing TWS colour coding (green→red gradient) should be used for line brightness/thickness, but the Jib/Sym distinction should be clear

## Validation
After implementing, verify:
1. Polar diagram renders with visible curves for all 7 wind speeds × 2 sails
2. At TWS 10 / TWA 42°: BTV shows 5.54 kn (Jib only at this angle)
3. At TWS 10 / TWA 135°: BTV shows 6.60 kn (Spinnaker) vs 5.80 kn (Jib)
4. Race sim with 90% performance factor and sail penalties produces estimate closer to 16-20 hours
5. VMG calculator on Dashboard still works correctly (uses BestPerf envelope)
