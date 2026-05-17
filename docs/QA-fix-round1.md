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

## Fix 3: RACE SIM — COMPLETE REDESIGN AS ANIMATED VIRTUAL RACE

The race sim's current design is wrong. It calculates the entire race instantly and shows a static timeline. The PURPOSE of the sim is to let the skipper verify the whole system works end-to-end: wind data flowing → polar speed lookup → boat position advancing → strategy making sense. It must be a virtual race that plays out visually.

### 3a. Animated simulation engine
**Sim start delay:** Change from 30 minutes to **1 minute** before simulated race start (`simStartTime = new Date(Date.now() + 1 * 60000)`). This lets the user quickly verify the system works end-to-end without waiting.

When the user clicks "Race Sim", the sim should:
1. Place the boat at Genève start at T=0
2. Each tick, look up the **forecast wind** at the boat's current lat/lon and current sim time (interpolate from the 9-point ensemble grid)
3. Calculate TWA from wind direction and course to next waypoint
4. Look up boat speed from polars for that TWS/TWA — use the correct sail (Jib or Spinnaker, whichever is faster at that angle)
5. Apply performance factor (default 90%)
6. Move the boat forward along the course at that speed
7. Show the **boat icon moving on the Leaflet map** in real time
8. Auto-advance to next waypoint when within proximity
9. Continue until the boat reaches Le Bouveret finish

**No GPS is used.** The boat position is entirely theoretical — calculated from polars + wind forecast. This is a system integration test, not a live tracker.

### 3b. Speed control
Add a speed multiplier selector: 1x (real time), 5x, 10x, 30x, 60x
- At 60x, an 18-hour race completes in 18 minutes
- Default to 10x for a good balance of speed and observability
- The sim tick interval should be every 100ms, with each tick advancing (100ms × speed_multiplier) of sim time
- At 1x: 1 tick = 100ms of race time (smooth animation)
- At 60x: 1 tick = 6 seconds of race time

### 3c. Live dashboard panel during sim
While the sim is running, show a real-time info panel:
- **Race clock:** T+HH:MM:SS (elapsed sim time)
- **Speed control:** [1x] [5x] [10x] [30x] [60x] buttons
- **Current position:** leg name (e.g., "Petit Lac → Yvoire")
- **SOG:** current theoretical speed from polar lookup
- **TWS / TWA:** current wind at boat position
- **Sail:** Jib or Spinnaker (blue/green indicator)
- **Distance to next mark:** in NM
- **ETA to finish:** based on current pace
- **Performance factor slider:** 75%-100%, default 90%

### 3d. Realism penalties
- **Sail change penalty:** When switching Jib↔Spinnaker, add 4 min (hoist) or 3 min (drop) at 60% speed. Track total sail changes.
- **Tacking penalty:** Course change >30° upwind = 45 sec at 40% speed
- **Gybing penalty:** Course change >30° downwind with spinnaker = 60 sec at 50% speed; with jib = 30 sec at 60% speed
- **Sub-polar wind:** Below TWS 6 kn (lowest polar), scale linearly from the 6kn polar down to 0 at TWS 0. Do NOT extrapolate flat — a CYD 27 barely moves in 2 kn of wind.

### 3e. Track visualization
- Draw the boat's track on the Leaflet map as it moves
- Colour the track by sail type: blue = Jib, green = Spinnaker
- Show wind barbs along the track at intervals
- At the end of the sim, keep the full track visible as a review

### 3f. Sim results summary
When the boat crosses the finish:
- Show total elapsed time
- Show number of sail changes, tacks, gybes
- Show average speed, leg-by-leg breakdown
- Compare with typical Bol d'Or finishing times for TCF3 class (16-24 hours)

## Fix 5: DASHBOARD IMPROVEMENTS

### 5a. Hide boat spec card
The "BOAT — CYD 27 ORC CECCARELLI" card with LOA, displacement, sails etc. takes up valuable dashboard space. This app is built for one specific boat — the crew doesn't need to see static specs every time. Move it to a collapsible "Boat Info" section (collapsed by default), or move it to a separate "About" section accessible from a small info icon.

### 5b. Systems Check card (NEW)
Add a "Systems Check" card to the Dashboard that shows live feed health at a glance. Each feed shows a green/amber/red indicator:

| Feed | Green | Amber | Red |
|------|-------|-------|-----|
| **Wind Forecast** (Open-Meteo) | Data loaded, <2h old | Data loaded but >2h old | Fetch failed or no data |
| **Station Obs** (MeteoSwiss) | Data <15 min old | Data 15-30 min old | No data or fetch error |
| **GPS Position** | Fix acquired, accuracy <50m | Fix acquired, accuracy >50m | No permission or no fix |
| **Competitors** (MySuiviRegate) | Connected, positions updating | Connected but stale (>5 min) | Not connected / error |
| **Device Clock** | Synced (NTP offset <5s) | Cannot verify | — |

**Implementation notes:**
- Card should be compact — one row per feed, icon + name + status dot + last-update timestamp
- Auto-refresh every 30 seconds
- The competitor feed (MySuiviRegate) is not yet implemented — show it as "Not connected" with a grey dot for now, so the card is ready when the integration comes
- The GPS check should call `navigator.geolocation.getCurrentPosition()` on card load and report the result
- Wind forecast check: verify that the ensemble grid data exists and check the timestamp of the last fetch
- Station obs check: verify at least one station has data and check `reference_ts` freshness
- Consider a "Refresh All" button that re-fetches all live data sources

This is the most important card on race morning — the crew needs to confirm all systems are go before the start.

### 5c. Race countdown → race clock transition
The countdown card should transform based on timing:
- **D-14 to D-1:** "20d 0h" countdown as now
- **Race morning (D-0, before 10:00):** Switch to minutes precision: "Starts in 2h 15m"
- **After start (10:00 CEST):** Flip to elapsed race clock: "T+03:42:15" counting up, green colour
- **After estimated finish:** "Race complete — 18h 42m" with total time

## Fix 6: WIND DATA — AUTO-LOAD & DIRECTION BUG (P1)

### 6a. Auto-load wind data on app startup
The "Current Wind — Lac Léman" card on the Dashboard is empty until the user visits the Wind tab, which is where the API fetch is triggered. This is wrong — the Dashboard is the first screen the crew sees, and it needs live wind immediately.

**Fix:** Fetch wind data (Open-Meteo ensemble + any station observations) on app load, regardless of which tab is displayed. The 10-minute auto-refresh timer should also run globally, not per-tab. The Wind tab can trigger an additional fetch when opened, but the data pipeline must be tab-independent.

### 6b. Verify wind direction convention (possible bug)
QA test on 17.05.2026: the app showed Geneva wind as **WSW (247°)** at 1 kn. At the same time:
- MeteoSwiss reported wind **from north** at 3.4 km/h (~1.8 kn)
- Windfinder (GFS model) showed roughly **ENE** flow over Petit Lac

At 1-2 kn the direction is inherently noisy, but a ~180° discrepancy suggests a possible convention bug. Check:
1. Is the Open-Meteo `wind_direction_10m` value the **meteorological convention** (direction wind comes FROM)? It should be.
2. Does the app's display code interpret this correctly? The arrow and cardinal label (WSW 247°) should mean "wind blowing FROM the WSW", i.e., heading toward ENE.
3. If the code is accidentally showing the direction wind blows TO, add 180° (mod 360).
4. Cross-check: when the forecast says 247°, does the direction arrow point toward ENE (the direction the air is moving)? Or does it point WSW? Meteorological convention: the arrow should point in the direction the wind is going (toward ENE), but the label says "from WSW".

**Also:** Consider adding MeteoSwiss station observations (Nyon, Pully, etc.) alongside the forecast data for the Dashboard "Current Wind" card. The forecast models alone are unreliable at very low wind speeds. The Zugersee app already integrates MeteoSwiss stations — port that pattern to the Bol d'Or app.

## Fix 4: POLAR DIAGRAM VISUAL IMPROVEMENTS
On the Polars tab:
- Draw Jib curves in blue, Spinnaker curves in green (matching ORC convention)
- Show crossover point with a small marker
- Add legend: "Blue = Jib 17.66 m² | Green = Spinnaker 47.18 m²"
- The existing TWS colour coding (green→red gradient) should be used for line brightness/thickness, but the Jib/Sym distinction should be clear

## Fix 7: WIND TAB IMPROVEMENTS

### 7a. Fix broken MeteoSwiss radar link (P1 Bug)
The "Radar" link on the Wind tab leads to a 404 on meteoswiss.admin.ch. MeteoSwiss restructured their site. Replace with the current working URL:
- Radar: `https://www.meteoswiss.admin.ch/weather/precipitation/nowcasting.html` (or find the latest correct URL for the precipitation/wind radar)
- Verify all other external links on the Wind tab as well

### 7b. Rename "Pattern Read" → "Current Wind Pattern"
The label "Pattern Read" is confusing. Rename to **"Current Wind Pattern"** or **"Active Pattern"**. The functionality (detecting Bise, Séchard, thermal, etc. from current wind data) is good but the UX label needs to be self-explanatory.

### 7c. Higher-granularity 48h forecast
The current 48h forecast shows only 3 zones (Geneva, Lausanne, Bouveret). This is too coarse for a 70 NM race where wind varies significantly along the course. 

**Improvements:**
1. **More forecast points:** Expand from 3 to at least 6-8 points along the course: Genève (start), Nyon, Rolle, Morges, Lausanne, Montreux, Villeneuve, Le Bouveret (finish). The AROME HD (1.3km) and ICON D2 (2km) models support this resolution — we're already querying a 9-point grid on the Strategy tab.
2. **Location indicator:** Add a small map icon or mini lake silhouette next to each forecast section showing WHERE on the lake the data applies. The crew must instantly know which part of the course they're looking at.
3. **Leg-based view:** Consider organizing the forecast by race leg (Petit Lac → Yvoire → Meillerie → Le Bouveret) rather than just geographic zones, since that's how the crew thinks during the race.

### 7d. Wind pattern timeline in forecast
Currently the pattern detection only works on live data ("what's happening now"). Extend it to the 48h forecast:

1. **Pattern forecast strip:** Below the hourly wind forecast, add a colour-coded strip showing the predicted wind pattern at each hour: e.g., "Thermal → Séchard → Calm → Bise". Use the same pattern classification logic that "Pattern Read" uses, but applied to forecast data.
2. **Pattern by zone:** Since different parts of the lake can have different patterns simultaneously (e.g., Séchard in Petit Lac but still thermal in Haut-Lac), show per-zone pattern predictions.
3. **Race window highlight:** Visually highlight the 18-24h race window (Saturday 10:00 to Sunday ~06:00) in the forecast timeline so the crew can quickly focus on what matters.
4. **Pattern confidence:** At D-7 to D-3, patterns are uncertain. At D-1, they're fairly reliable. Show a confidence indicator that increases as race day approaches.

**How to detect patterns from forecast data:**
- **Bise:** All zones NE (020°-060°), TWS > 5 kn, typically strongest in Petit Lac
- **Séchard/Vent:** SW (200°-250°), often strongest mid-lake (Morges-Lausanne)
- **Thermal:** S-SW (180°-230°), light (< 10 kn), builds in afternoon, strongest near shores
- **Lake breeze convergence:** Variable direction, light, late afternoon — look for opposing directions between north and south shore forecast points
- **Bise de nuit:** NE flow developing after sunset, common in summer, important for overnight racing

## Fix 8: STRATEGY TAB — RACE MODE & SIM INTEGRATION

### 8a. Three operating modes
The Strategy tab should behave differently depending on context. Detect automatically and show a mode indicator at the top:

| Mode | When | Boat position source | Wind source | What to show |
|------|------|---------------------|-------------|--------------|
| **Planning** | D-14 to D-1 (before race day) | None — show waypoints only | Forecast models | Bank advisor, tactical notes, "what if" scenarios |
| **Simulation** | Race sim is active | Simulated position from race sim engine (Fix 3) | Forecast at sim time | Sim boat on map, live bank advice, sim wind overlay |
| **Race Day** | GPS enabled + race date | Real GPS position | Forecast + station observations | Full cockpit: position, speed, wind, rivals, leg advice |

### 8b. Race Day cockpit layout
On race day, the Strategy tab becomes the primary interface. Optimise for quick glances in rough conditions (big text, high contrast, minimal scrolling):

**Top strip — always visible:**
- Current leg name: e.g., "LEG 2: Yvoire → Meillerie" 
- Distance to next mark + ETA
- Current SOG / TWS / TWA (from GPS + wind data)
- Sail recommendation: Jib or Spinnaker (blue/green badge)

**Map — center of screen:**
- Boat position (GPS) with heading arrow and wake trail
- Wind barbs from forecast + station observations
- Competitors (when MySuiviRegate is connected) as labelled dots
- Colour-coded route ahead: blue = jib legs, green = spinnaker legs
- Next waypoint highlighted with distance ring

**Bottom panel — scrollable tactical cards:**
- **Bank advisor** for current leg: north shore vs south shore recommendation with reasoning
- **Wind ahead:** What the forecast shows for the next 2-3 hours at the boat's projected position
- **Pattern shift alert:** If the forecast predicts a wind pattern change in the next 1-2 hours, show a prominent alert (e.g., "Séchard dying — Bise expected in ~90 min, prepare for windward work")
- **Rival positions:** Nearest competitors with time delta (when available)

### 8c. Leg-by-leg auto-advance
The Strategy tab currently has all tactical notes visible at once. On race day, auto-filter to the CURRENT leg based on GPS proximity to waypoints:

1. **Approaching mark:** When < 0.5 NM from next waypoint, show the upcoming leg's tactical notes and bank advice prominently
2. **Morges decision point:** This is the most important tactical call of the race. When the boat reaches Morges/Rolle area (~46.51°N), trigger a special decision card: "BANK DECISION: North shore (Évian side) or South shore (Swiss side)?" with current wind data for both options
3. **Night transition:** When sunset hits (~21:30 in June), show a night-sailing card with tips: thermal dying, Bise de nuit likelihood, navigation light checks

### 8d. Simulation feeds Strategy
When the race sim (Fix 3) is running, the Strategy tab should:
- Show the simulated boat position on the map (same icon as race day, but with a "SIM" badge)
- Update bank advisor based on simulated position and sim wind data
- Show the same cockpit layout as race day, but fed by simulation data
- Allow the user to switch between the Strategy tab and the sim dashboard panel without losing sim state
- This is the key integration test: the crew can run the sim and verify that the Strategy tab gives sensible advice at each point of the course

### 8e. Offline resilience
The Bol d'Or goes through areas with poor mobile coverage (Haut-Lac, between Meillerie and St-Gingolph). The Strategy tab must work offline:
- Cache the last wind forecast in localStorage/IndexedDB
- GPS works without data connection
- Tactical notes and polar data are baked into the PWA
- Show "Last forecast update: X min ago" with a warning if data is stale (> 30 min)
- When connection returns, auto-refresh wind data silently

## Fix 9: STRATEGY MAP — QUALITY OVERHAUL (P1)

### 9a. Fix lines bleeding outside the lake
The isochrone routing lines and/or wind grid lines extend beyond the lake boundary onto land. All route calculations, wind overlays, and visualization lines must be clipped to the lake polygon. Use a GeoJSON lake boundary as a clip mask for the Leaflet overlay layer.

### 9b. OpenSeaMap marker alignment
The pink navigation markers (buoys, anchors) from OpenSeaMap are not properly positioned relative to the coastline at various zoom levels. This is a known issue with OpenSeaMap tile registration.

**Options:**
1. **Preferred:** Use OpenSeaMap tiles only at zoom levels where alignment is acceptable (typically z12+), and hide them at lower zooms
2. **Alternative:** Replace OpenSeaMap with our own curated markers for the key navigation points along the Bol d'Or course (the race buoys, harbour entrances, and hazards that matter). This gives full control over positioning and styling
3. At minimum, add the official Bol d'Or race marks as custom Leaflet markers with correct coordinates — these are more important than generic chart symbols

### 9c. Basemap and water rendering
The current solid black water is too dark and featureless. Improve readability:

1. **Water colour:** Use a dark navy/blue instead of pure black (e.g., `#0a1628` or similar). The Zugersee app's dark water style is a good reference.
2. **Basemap:** Consider using a better tile provider for the land area. Options:
   - CartoDB Dark Matter (dark theme, cleaner than raw OSM)
   - Mapbox Dark (if API key available)
   - Or keep current tiles but increase water contrast
3. **Shore contour:** Add a subtle light line along the shoreline so the lake boundary is always visible, even when zoomed out
4. **Depth hint:** If available, add subtle depth contour shading — the deep channel in Lac Léman matters tactically (thermal effects, current)

### 9d. Route visualization — clear visual hierarchy
The current mix of solid and dashed lines is confusing. Establish a clear visual language:

| Element | Style | Colour | Purpose |
|---------|-------|--------|---------|
| **Planned route** | Solid line, 3px | White or bright cyan | The direct waypoint-to-waypoint course |
| **North bank option** | Dashed line, 2px | Orange | Alternative route via French (north) shore |
| **South bank option** | Dashed line, 2px | Yellow | Alternative route via Swiss (south) shore |
| **Isochrone optimal** | Dotted line, 2px | Green | Best route from routing algorithm |
| **Boat track (sim/race)** | Solid line, 3px | Blue (jib) / Green (spinnaker) | Where the boat has been, coloured by sail |
| **Wind barbs** | Small arrows | White, semi-transparent | Wind field overlay on the water |

Add a **legend** on the map (collapsible, bottom-left) explaining each line type.

### 9e. Waypoint markers
Improve waypoint visibility and information:
- Number each waypoint clearly: 1-START (Genève), 2-Sécheron, 3-Yvoire, 4-Thonon, 5-Meillerie, 6-Bouveret, 7-FIN
- Use larger, labelled markers with the mark name visible (not just a dot)
- Show distance between consecutive marks on the route line (e.g., "12.3 NM" label on each leg)
- Highlight the next waypoint with a pulsing ring during race/sim mode

### 9f. Map interaction
- **Pinch zoom** must be smooth on mobile (critical for race-day phone use)
- **Tap on waypoint** should show: mark name, distance from current position, bearing, estimated time to reach
- **Tap on wind barb** should show: TWS, TWD, model source, forecast time
- **Center on boat** button (already exists) should work in all three modes (planning shows whole course, sim/race centers on boat position)

## Fix 10: ROUTE SIMULATION — BROKEN (P1)

The route simulation on the Strategy tab is non-functional. Every scenario produces the same wrong result.

### 10a. Historical wind data not loading
Switching between "2024 race + rivals" and "2025 race + rivals" produces identical results (~30h, 37 NM, 1.2 kn). The sim is clearly using today's live wind (which is 1-2 kn) regardless of which historical scenario is selected.

**Fix:** Each historical scenario must load the actual wind data from that year's race. Either:
1. Store historical wind snapshots (the wind field during the 2024 and 2025 Bol d'Or races) as embedded JSON or fetch from Open-Meteo's historical API
2. Verify the scenario selector actually triggers a different wind data source
3. If historical wind data isn't available, the sim should clearly state "No historical wind data for this year — using current forecast" rather than silently producing garbage

### 10b. Greedy VMC oscillation bug — 1800 tacks
1800 tacks in 30 hours = 1 tack per minute. This is the greedy VMC algorithm thrashing in light air. When TWS < 3 kn, no tack angle produces meaningful VMG, so the algorithm flips between port and starboard every iteration.

**Fix:**
1. **Minimum tack interval:** Enforce a minimum time between tacks (e.g., 5 minutes). No real crew tacks every minute.
2. **Hysteresis:** Only tack if the new heading gains > 5° of VMG advantage over the current heading. Small differences should be ignored.
3. **Light air mode:** When TWS < 3 kn, the algorithm should hold current heading and accept slow progress rather than oscillating. In reality, you'd sail for the nearest wind pressure, not tack repeatedly in a calm patch.
4. **Tack count sanity cap:** Flag any result with > 50 tacks as pathological and display a warning.

### 10c. Rival gate times not calculated
The "VS Rivals" table shows dashes (—) for gates S1 through S4, with only S5 having a value. The intermediate gate comparison is not working.

**Fix:**
1. The rival historical data (from SuiviRegate) must include timing at each gate/sector mark, not just the finish
2. Map the sim's waypoints to the rival tracking gates so sector times can be compared
3. If rival intermediate data isn't available, show "N/A" with a tooltip explaining why, rather than dashes that look like a bug

### 10d. Distance should be ~70 NM, not 37 NM
The race course is approximately 70 NM (Genève → Le Bouveret via Yvoire, Meillerie, etc.). The sim showing 37 NM means the boat only covered half the course before hitting the 30h cap. This is a consequence of the light wind bug (10a), but verify that the total course distance is correctly calculated and displayed as a reference value (e.g., "37.2 / 70.0 NM completed").

### 10e. Relationship to Race Sim (Fix 3)
This route simulation and the Race Sim (Fix 3, animated virtual race on Dashboard) serve different purposes:

| Feature | Route Simulation (Strategy tab) | Race Sim (Dashboard, Fix 3) |
|---------|-------------------------------|---------------------------|
| **Purpose** | Compare routing algorithms against historical races | System integration test with live/forecast wind |
| **Wind source** | Historical data from past Bol d'Or races | Current forecast from Open-Meteo |
| **Output** | Static results table with rival comparison | Animated boat moving on map in real time |
| **When to use** | Planning phase (D-14 to D-1) — test strategies against known conditions | Pre-race and race day — verify wind→polars→position pipeline works |

Both should share the same polar lookup engine (P_JIB, P_SYM, performance factor) and penalty system (tack, gybe, sail change costs from Fix 3d). Do not duplicate the polar/penalty logic — refactor into shared functions.

## Fix 11: RIVALS TAB — DATA GAPS & MANEUVER ANALYSIS

### 11a. "Bol d'Or 2026" section — live + sim competitor display
The "Bol d'Or 2026" area is reserved for live competitor positions from MySuiviRegate during the race. Improvements:

1. **During simulation:** Populate this section with the rival boats' positions from the selected historical scenario. When running "2025 race + rivals", show Leone, Pertuiset, Monachon, Rottet, Borter moving through the course using their actual 2025 GPS tracks. This lets the user see the full fleet picture during sim, not just their own boat.
2. **Pre-race (no sim):** Show a placeholder: "Competitor positions will appear here during the race (via MySuiviRegate)" with a status indicator (connected/not connected).
3. **Race day:** Live positions from MySuiviRegate feed, updating in real time.

### 11b. Missing sector gate times
The head-to-head table shows dashes (—) for S2, S3, S4 for most boats. Only Rottet has intermediate data. This makes the sector comparison useless.

**Fix:**
1. **Calculate gates from GPS tracks:** The SuiviRegate historical track data contains full GPS traces. Calculate gate crossing times by detecting when each boat's track crosses a virtual gate line at each sector boundary (Nyon, Lausanne outbound, Le Bouveret, Lausanne return).
2. **Gate line definition:** Define each gate as a lat/lon line perpendicular to the course at the sector mark. Detect crossing with simple line-segment intersection.
3. **If no GPS tracks available:** Show "No track data" instead of dashes, and explain what data is needed.
4. **Sector delta display:** When sector times ARE available, show the delta from the leader (current format "+1027m" is confusing — does "m" mean minutes or metres? Use "min" explicitly: "+17min 07s").

### 11c. Units confusion — "m" vs "min"
In the head-to-head table, "+1027m" appears next to sector times. This is ambiguous — it could mean 1027 minutes (17+ hours, which makes no sense) or 1027 metres. Based on context it likely means minutes, but "+1027 minutes behind" at S1 Nyon would mean arriving 17 hours later, which is also wrong.

**Fix:** Clarify units. If these are minutes behind the sector leader, format as "+Xh Ym" (e.g., "+17h 07m"). If metres behind, use "m" but that's not a meaningful metric for elapsed-time comparison. Review what the raw SuiviRegate data provides and display the correct unit with clear labels.

### 11d. Maneuver performance analysis (NEW FEATURE)
Add a "Maneuver Performance" card to the Rivals tab (or a dedicated Performance sub-section) that analyses tacking and gybing efficiency from GPS track data.

**Tack analysis (from GPS/Kwindoo data):**

| Metric | How to calculate | Why it matters |
|--------|-----------------|----------------|
| **Speed before** | Avg SOG in 30s window before heading change > 60° | Baseline — were you at polar speed before the tack? |
| **Min speed** | Lowest SOG within 15s of heading change | How much speed you dump — CYD 27 is light, should recover fast |
| **Recovery time** | Seconds from min speed to reaching 90% of target polar speed at new TWA | Key differentiator between good and bad tacks |
| **VMG loss** | Integrate VMG deficit vs steady-state over the maneuver window (60s) | Total cost of the tack in metres toward the mark |
| **Distance lost** | Metres lost to windward vs a theoretical boat that didn't tack | The number the skipper cares about most |

**Gybe analysis:** Same metrics but for downwind heading changes > 60°. With spinnaker, gybe loss is typically larger and recovery slower.

**Display:**
- Show a box-whisker chart of tack loss across different TWS ranges (e.g., 6-8 kn, 8-12 kn, 12+ kn)
- Compare Little Johnka's tack loss against the rival fleet average (if rival GPS data has enough resolution)
- Track improvement over the season: "Your average tack loss in May: 0.8 kn (4.2s recovery) vs April: 1.1 kn (5.8s recovery)"
- Set target benchmarks based on the polar data: at TWS 10, a clean tack on a CYD 27 should lose ~0.5 kn with 3-4s recovery

**Data source:** This requires high-frequency GPS data (1 Hz or better). Kwindoo typically records at 1 Hz. SuiviRegate may be lower frequency (10-30s intervals), which is too coarse for maneuver analysis — note this limitation.

**Sail change performance:** Same concept but for hoist/drop timing:
- Time from bear-away to spinnaker flying and at target speed
- Time from spinnaker drop to jib trimmed and at target speed
- Compare against the penalty assumptions in the race sim (Fix 3d: 4 min hoist, 3 min drop)

## Validation
After implementing, verify:
1. Polar diagram renders with visible curves for all 7 wind speeds × 2 sails
2. At TWS 10 / TWA 42°: BTV shows 5.54 kn (Jib only at this angle)
3. At TWS 10 / TWA 135°: BTV shows 6.60 kn (Spinnaker) vs 5.80 kn (Jib)
4. Race sim with 90% performance factor and sail penalties produces estimate closer to 16-20 hours
5. VMG calculator on Dashboard still works correctly (uses BestPerf envelope)
