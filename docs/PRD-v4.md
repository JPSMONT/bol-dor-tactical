# BOL D'OR MIRABAUD — Tactical Race App
# Product Requirements Document & Architecture
# Version 4.0 — May 2026

Prepared for Joao Pinto — Pinto Ventures
Boat: Little Johnka — CYD 27 ORC (SUI 6116)
Race: June 5–7, 2026 — 123 km — Genève → Le Bouveret → Genève

---

## 1. Executive Summary

This document defines the product requirements for a Progressive Web App designed to give the crew of Little Johnka a competitive edge at the Bol d'Or Mirabaud. The app addresses three distinct phases: pre-race preparation (weeks before), race-day tactical support (real-time on the water), and post-race analysis (performance review and learning).

Version 4.0 represents a significant expansion driven by four research streams. First, SuiviRegate and DeepRegatta OSCAR provide real competitor GPS tracks and advanced analysis methodology. Second, a comprehensive competitor analysis (70+ boats ranked, 5 primary targets identified) enables a follow-boat strategy central to race-day execution. Third, meteorological research from ASLeman and the Skippers/Fontannaz/Wahl methodology establishes a structured weather preparation workflow from D-14 through race start. Fourth, technical research into nautical charting (Leaflet + OpenSeaMap) and device sensor APIs (GPS + compass) enables proper navigation support for a 123 km overnight race.

The core philosophy is that Little Johnka, as a first-time Bol d'Or participant, must compensate for lack of experience with superior preparation and real-time intelligence. Rather than sailing blind, the crew will study the routes of identified target competitors across multiple past editions, understand how different wind patterns rewarded different strategies, and have a structured pre-race weather preparation timeline to translate forecast data into a clear tactical plan before the gun fires.

---

## 2. Implementation Status

| Feature | Status | Priority | Notes |
|---------|--------|----------|-------|
| PWA shell & offline cache | DONE | P1 | Service worker, manifest, icons |
| Polar viewer (ORC data) | DONE | P1 | All 7 TWS, VMG targets, interactive canvas |
| Wind forecast (multi-zone) | DONE | P1 | 3 zones, 48h, Open-Meteo GFS |
| Bank selection advisor | DONE | P1 | VMG per zone, pattern-specific tactics |
| Race dashboard & countdown | DONE | P1 | Boat specs, quick VMG calculator |
| Zoomable race replay | DONE | P2 | 2021–2025, SVG pan/zoom, boat tracks |
| Hi-res wind field overlay | DONE | P2 | 16-point AROME HD 1.5km grid |
| Race simulation mode | DONE | P2 | Interactive bank/tack decisions with scoring |
| Live wind widget | DONE | P2 | Current Lac Léman conditions |
| Zugersee Wind heatmap | DONE | P2 | Wind field with arrows, station data |
| SuiviRegate KMZ integration | NEW | P1 | Real competitor GPS tracks (400+ boats/year) |
| Historical replay with real tracks | NEW | P1 | Replace simulated tracks with SuiviRegate data |
| Little Johnka route simulation | NEW | P1 | Simulate boat from polars + wind field |
| Competitor tracking (Rivals tab) | NEW | P1 | 5 target boats + secondary watchlist |
| Weather prep workflow (D-14 to D-0) | NEW | P1 | Countdown-driven weather dashboard |
| Nautical chart map (Leaflet/OpenSeaMap) | NEW | P1 | Zoomable map with buoys, lights, towns |
| GPS & compass waypoint navigation | NEW | P1 | Device sensors for bearing to next mark |
| DeepRegatta-style analysis | NEW | P2 | PPR, VMC, shift scores, sector analysis |
| Live race tracking (SuiviRegate) | NEW | P2 | Hourly KMZ poll during race day |
| Rival-aware strategy advisor | NEW | P2 | Bank scoring informed by historical rival routes |
| Simulation vs real rivals | NEW | P2 | Test strategies against actual rival tracks |
| Enhanced wind reference (ASLeman) | NEW | P2 | Additional thermal winds, Vaudaire dual nature |
| Upgrade forecasts to multi-model | PLANNED | P2 | ICON-CH1 + AROME HD + ICON-CH2 |
| Live GPS position tracking | PLANNED | P2 | iPhone geolocation API |
| Weather routing engine | PLANNED | P3 | Isochrone method with GRIB input |
| Wind shift detector | PLANNED | P3 | Real-time from GPS/instruments |
| Performance dashboard (post-race) | NEW | P3 | Speed/VMG/PPR charts, leg analysis |
| Day mode & responsive layout | PLANNED | P3 | Multi-device use, accessibility |

---

## 3. Boat: Little Johnka — CYD 27 ORC

Little Johnka is a CYD 27, a custom Ceccarelli 27 racing yacht. The ORC certificate (SUI 6116) provides verified performance data. This is Little Johnka's first Bol d'Or participation, which means there is no historical SuiviRegate tracking data for this boat.

| Specification | Value |
|---------------|-------|
| LOA / LWL | 8.25 m / 7.47 m |
| Beam / Draft | 2.83 m / 1.85 m |
| Displacement | 1,780 kg |
| Mast | Carbon fibre |
| Main sail | 27.13 m² |
| Jib | 17.66 m² |
| Spinnaker (symmetric) | 47.18 m² |
| Yardstick / TCF | YS 94 / TCF 1.029 |
| Designer | Ceccarelli Yacht Design |
| Registration | SUI 6116 |

### 3.1 ORC Polar Data

Complete velocity prediction data covers 7 true wind speeds (6, 8, 10, 12, 14, 16, 20 kn) with 13 true wind angles each, plus optimal beat and run VMG targets.

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

**Assumption:** Polars are based on current sail inventory (main, jib, spinnaker). NO Drifter. NO Code 0. Only three sails.

---

## 4. Competitor Tracking & Follow-Boat Strategy

As a first-time participant with no institutional knowledge of the race, Little Johnka's primary competitive advantage will come from identifying, studying, and tracking the right competitors.

### 4.1 Primary Target Boats

| Rank | Skipper | Sail No. | Boat Type | TCF | SuiviRegate Name | History | Speed vs LJ |
|------|---------|----------|-----------|-----|-------------------|---------|-------------|
| 1 | Leone | FRA 15710 | 747 One Design | 1.039 | illico Ti Vitti team | 34→31→11→3 | ~1.5% faster |
| 2 | Pertuiset | SUI 076 | Esse 850 | 1.113 | Darnetal | Won 2025 | ~9% faster |
| 3 | Monachon | SUI 9 | 6.5m SI | 0.976 | Ondine | Won 2023, 2nd 2025 | ~5% SLOWER |
| 4 | Rottet | SUI 140 | Esse 850 | 1.087 | Storm | 9→71→24→21 | ~6% faster |
| 5 | Borter | SUI 102 | Grand Surprise | 1.112 | Little Nemo II | Won 2024 | ~9% faster |

### 4.2 Why These Five

**Leone (FRA 15710):** Closest in raw speed (TCF 1.039 vs LJ's 1.029, just 1% gap). 747 One Design is a comparable boat size. Massive improvement trajectory from 34th to 3rd. Best proxy for where Little Johnka could realistically aim.

**Pertuiset / Darnetal (SUI 076):** 2025 winner. Esse 850 is faster (~9%) but is the benchmark for the entire class. The "ceiling reference."

**Monachon / Ondine (SUI 9):** TCF 0.976 means Ondine is ~5% SLOWER than Little Johnka, yet Monachon won on corrected time in 2023 and finished 2nd in 2025. Proves superior strategy can overcome a meaningful speed deficit. Ondine's routes show WHERE gains are made.

**Rottet / Storm (SUI 140):** Consistent finisher providing a realistic mid-fleet reference. Route data reveals which conditions and decisions matter most.

**Borter / Little Nemo II (SUI 102):** 2024 winner. Described as a legend in the fleet. Long-term perspective on how the best boats approach the race.

### 4.3 Secondary Watchlist

| Skipper | Sail No. | Boat | Rationale |
|---------|----------|------|-----------|
| Rousselle | SUI 131 | Grand Surprise | Consistent top-5 (7th, 5th, 15th) |
| Lanz | SUI 671 | Esse 850 | Improving trajectory |
| Bichelmeier | SUI 132 | Grand Surprise | Experienced, statistical coverage |

### 4.4 Rivals Tab — App Feature Specification

**Pre-Race Study View**
- Card for each of the 5 primary targets: boat photo/silhouette, sail number, boat type, TCF, historical finishes as sparkline, crew details
- Route overlay: select any rival and year to see their GPS track on the Leaflet map, colour-coded by speed
- Head-to-head comparison: overlay two or more rivals on the same race to see where they diverged
- Strategy extraction: annotate key decision points (bank choice, tack timing, Le Bouveret rounding, overnight strategy)
- Leg-by-leg rival ranking table across all available years

**Race-Day Tracker View**
- Live positions of 5 primary + 3 secondary targets from SuiviRegate KMZ, highlighted on map
- Distance delta: distance ahead/behind each rival along the course axis (not straight-line), updated hourly
- Relative performance: when both own GPS and rival positions available, compute gaining/losing
- Alert system: notify when a rival makes a major strategic move (crosses to opposite bank, begins major tack sequence, deviates >2 km from rhumb line)
- "Follow mode": overlay a rival's heading and speed on the compass display as reference bearing

**Post-Race Comparison View**
- Side-by-side track replay of Little Johnka vs each rival
- Sector-by-sector rank comparison table
- Speed/VMC timeline charts with rival overlay
- Key divergence moments: automated detection with distance gained/lost annotation

**Assumption:** Rival identification in SuiviRegate data relies on boat name matching. The app stores a configurable name→sail number mapping.

---

## 5. Structured Weather Preparation Workflow

Research from Lionel Fontannaz (MeteoSwiss) and Christophe Wahl reveals that weather preparation for the Bol d'Or is a structured multi-week process.

### 5.1 The D-14 to D-0 Timeline

| Phase | Timing | Activity | App Support |
|-------|--------|----------|-------------|
| Synoptic | D-14 to D-7 | Observe large-scale pattern (blocking high? frontal sequence? Bise setup?). | Dashboard card showing synoptic overview from Open-Meteo GFS. Link to MeteoSwiss pressure charts. |
| Model Comparison | D-7 to D-5 | Compare ICON-CH1, AROME HD, ICON-CH2, ICON-D2. Watch for convergence or divergence. | Side-by-side multi-model comparison widget. Flag when models agree vs diverge. |
| Pattern Settlement | D-5 to D-3 | Models should converge on wind direction. Key question: Bise, Vent, thermal, or transition? | Confidence indicator: green/amber/red. Pattern classification label. |
| Detailed Timing | D-2 to D-1 | Nail down wind timing: when does Bise weaken, when does thermal kick in, overnight transition? | Hour-by-hour wind timeline. Highlight transition moments. Link model run to bank scoring. |
| Final Check | D-0 (morning) | Last model run. Check MeteoSwiss radar. Confirm or update tactical plan. | Final forecast dashboard with radar overlay. Pre-race checklist. Go/no-go for each strategic option. |
| Real-Time | Race day | Monitor station observations vs forecast. Detect deviations. Adapt. | Live station data widget. Deviation alerts when obs differ from forecast by >5 kn or >30°. |

### 5.2 Key Reference Stations

**La Dôle (1670m):** Altitude wind reference. Shows upper-level flow that will mix down to the lake surface. If La Dôle shows persistent NE flow, a Bise event is likely within 12–24 hours.

**Rhône Valley stations:** Key indicator for Vaudaire (S/SE wind via Rhône corridor). When valley stations show acceleration of southerly flow, a Vaudaire event is building in the Haut-Lac.

**MeteoSwiss Radar:** Compulsory check for convective activity. Thunderstorms produce extreme gusts >60 km/h. The app provides a direct link to MeteoSwiss radar.

### 5.3 Weather Dashboard Specification

- Countdown clock to race start with current preparation phase highlighted
- Phase-specific content surfaces automatically based on days remaining
- Multi-model comparison widget: side-by-side wind roses or direction/speed timelines
- Model confidence indicator (green/amber/red) based on inter-model agreement
- Pattern classifier: automatic labelling as Bise, Vent, Thermal, Vaudaire, Transition, or Mixed
- Hour-by-hour wind timeline spanning full race duration (18–24 hours)
- Reference station live data: La Dôle altitude wind + Rhône valley readings
- Direct link to MeteoSwiss radar
- Pre-race tactical plan builder: structured template for crew's strategic decisions

---

## 6. Navigation & Charting

### 6.1 Map Upgrade: Leaflet + OpenSeaMap

**Leaflet.js (v1.9+)**
- Lightweight (~42 KB gzipped), mobile-optimised, touch-friendly
- Supports multiple tile layers, overlays, markers, and polylines
- Built-in smooth pinch-to-zoom, pan, and geolocation support

**OpenSeaMap Seamark Overlay**
- Free nautical chart overlay with buoys, navigation lights, beacons, seamarks
- Tile URL: https://tiles.openseamap.org/seamark/{z}/{x}/{y}.png
- Transparent PNG tiles overlaid on base map
- Licensed CC-BY-SA, no API key required
- Seamark data from zoom level 9+, full detail at zoom 14+

**Base Map Options**

| Layer | Tile URL | Best For |
|-------|----------|----------|
| OpenStreetMap | tile.openstreetmap.org/{z}/{x}/{y}.png | Town names, roads, landmarks |
| OpenSeaMap | tiles.openseamap.org/seamark/{z}/{x}/{y}.png | Overlay: buoys, lights, seamarks |
| Stamen Toner Lite | stamen-tiles.a.ssl.fastly.net/toner-lite/{z}/{x}/{y}.png | Clean background for data overlays |
| Satellite (ESRI) | server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/... | Terrain context, shore detail |

### 6.2 Map Integration Architecture

The Leaflet map becomes the shared foundation for multiple app views:
- Replay: historical boat tracks as Leaflet polylines
- Rivals: target boat routes with colour-coding
- Race day: own GPS + fleet positions + wind arrows
- Navigation: compass bearing line to next waypoint with distance/ETA
- Strategy: bank scoring overlay (Swiss/French/mid-lake zones) as semi-transparent polygons
- Wind: forecast/station data as Leaflet markers with rotation

All views share a single Leaflet map instance with togglable layer groups.

---

## 7. GPS & Compass Integration

### 7.1 GPS Position (Geolocation API)

**API:** `navigator.geolocation.watchPosition()` with `enableHighAccuracy: true`
- Returns latitude, longitude, altitude, speed, heading, accuracy at ~1 Hz
- `position.coords.heading` provides GPS-derived course over ground (requires movement >3 kn)
- iPhone accuracy typically 3–10 metres on the water
- Requires HTTPS and user permission grant

**Position Data Usage**
- Own position on Leaflet map with gold boat icon
- SOG displayed prominently, compared to polar target in real time
- VMG calculated continuously: SOG × cos(angle between heading and bearing to mark)
- Track recording in IndexedDB for post-race analysis
- Distance and ETA to Le Bouveret (outbound) or Genève finish (return)

### 7.2 Compass Heading (DeviceOrientation API)

**iOS:** `DeviceOrientationEvent.requestPermission()` (must be triggered by user gesture). `event.webkitCompassHeading` provides magnetic heading 0–360°.

**Android:** Uses `deviceorientationabsolute` event. Compass heading derived from `event.alpha` with screen orientation compensation.

### 7.3 Waypoint Navigation

| # | Waypoint | Latitude | Longitude | Notes |
|---|----------|----------|-----------|-------|
| 1 | Start line (Genève) | 46.2044°N | 6.1568°E | SNG start area |
| 2 | Nyon passage | 46.3830°N | 6.2340°E | Petit Lac exit |
| 3 | Lausanne abeam | 46.5080°N | 6.6280°E | Grand Lac midpoint |
| 4 | Montreux approach | 46.4340°N | 6.9100°E | Haut-Lac entry |
| 5 | Le Bouveret mark | 46.3910°N | 6.8570°E | Turn mark (mandatory rounding) |
| 6 | Return: Lausanne | 46.5080°N | 6.6280°E | Grand Lac return |
| 7 | Finish (Genève) | 46.2044°N | 6.1568°E | SNG finish line |

**Features:**
- Bearing to next waypoint on map and as compass heading number
- Compass rose overlay with boat heading (device compass) and bearing to mark distinguished
- Auto-advance: within 500m of waypoint, switch to next
- Manual waypoint selection for skipping ahead or returning
- Night mode: high-contrast bearing display (large digits, red-on-black)

---

## 8. Data Sources & Architecture

### 8.1 SuiviRegate — Official Race Tracking

KMZ archive access:

| Year | Race Code | Boats | URL Pattern |
|------|-----------|-------|-------------|
| 2025 | BOL25 | 402 | suiviregate.ch/sync/BOL25/kml/data.kmz |
| 2024 | BOPM24 | 449 | suiviregate.ch/sync/BOPM24/kml/data.kmz |
| 2023 | BOM23 | 412 | suiviregate.ch/sync/BOM23/kml/data.kmz |
| 2021 | BOM21 | 444 | suiviregate.ch/sync/BOM21/kml/data.kmz |

- Client-side parsing via JSZip (no server required)
- KMZ files publicly accessible, no authentication
- CORS headers allow direct fetch
- During live race: KML NetworkLink refreshes hourly

### 8.2 DeepRegatta OSCAR

Static JSON API at oscar.deepregatta.com/data/ with per-race analysis including PPR, VMC, Dreher Score, lateral deviation, manoeuvre detection, sector analysis. Race IDs: BOL25, BOPM24, BOM23, BOM22, BOM21, BOM19, BOM15, BOM14, BOM13, BOM12.

### 8.3 Complete Data Source Matrix

| Data | Source | Frequency | Status |
|------|--------|-----------|--------|
| Wind forecast | Open-Meteo (multi-model) | 1–3h | Live |
| Historical wind | Open-Meteo AROME HD | Static | Live |
| Boat polars | ORC certificate (embedded) | Static | Embedded |
| Lake polygon | OpenStreetMap (122 pts) | Static | Embedded |
| Competitor tracks | SuiviRegate KMZ | Static | NEW |
| Live fleet positions | SuiviRegate KMZ poll | Hourly | NEW |
| Race analysis ref. | DeepRegatta OSCAR JSON | Static | NEW |
| Rival boat mapping | Embedded config | Static | NEW |
| Nautical chart tiles | OpenSeaMap tiles | Static | NEW |
| Compass heading | DeviceOrientationEvent | ~60 Hz | NEW |
| GPS position | Geolocation API | 1 Hz | NEW |
| Reference stations | MeteoSwiss open data | 10 min | NEW |
| Altitude wind (La Dôle) | MeteoSwiss open data | 10 min | NEW |

### 8.4 Weather Models

| Model | Resolution | Horizon | Provider | Notes |
|-------|-----------|---------|----------|-------|
| ICON-CH1 | 1 km | 33h | MeteoSwiss | Highest resolution, Swiss optimised |
| AROME HD | 1.5 km | 48h | Météo-France | Best historical data (2023+) |
| ICON-CH2 | 2 km | 5 days | MeteoSwiss | Longer horizon for planning |
| ICON-D2 | 2 km | 48h | DWD | Good Lac Léman coverage |

---

## 9. Historical Race Replay with Little Johnka Simulation

### 9.1 Concept

Combines three data layers: (1) real GPS tracks from SuiviRegate for 400+ competitors, (2) historical wind fields from AROME HD at 1.5 km resolution, and (3) a simulated Little Johnka route computed from CYD 27 polars applied to prevailing wind.

### 9.2 Rival Highlighting

- Each rival gets unique colour and labelled icon
- "Follow Rival" mode: centre map on their position during playback
- Divergence markers when rival and Little Johnka take different paths
- Remaining 395+ boats as subtle dots

### 9.3 Little Johnka Route Simulation Engine

**Auto-routing mode:** Optimal VMG heading at each timestep based on polars and wind. Performance ceiling benchmark.

**Manual strategy mode:** Crew selects bank preference, simulation follows that strategy. Enables "what if" scenarios.

Constraints: tacking angle limits from polars, configurable tack penalty (default: 5 seconds), course boundaries from lake polygon. Boat at 90–95% of polar speed.

### 9.4 Replay Interface (Upgraded)

- Leaflet map with OpenSeaMap overlay (replacing SVG)
- 400+ real boat tracks as Leaflet polylines
- 5 rival boats highlighted with labels, colours, larger icons
- Little Johnka simulated track in gold/amber
- Wind field arrows from AROME HD, updating with time slider
- Time slider (18–24 hours) with play/pause and speed controls
- Year selector 2021–2025
- Click any boat for name, speed, heading, distance to mark
- Fleet density heatmap toggle
- Bank selection overlay showing which zone is faster

---

## 10. Performance Analysis (DeepRegatta-Inspired)

### 10.1 Analysis Metrics

| Metric | Computation | Priority |
|--------|-------------|----------|
| SOG | Distance between GPS fixes / time delta | P1 |
| VMC | SOG × cos(heading − bearing to mark) | P1 |
| PPR (Perf. to Polar Ratio) | Actual SOG / polar speed at current TWA/TWS | P2 |
| Tack/Gybe Detection | Heading change >60° in <2 min | P2 |
| Tack Cost | Speed loss 30s before to 30s after tack | P2 |
| Bank Commitment Score | Avg lateral deviation from rhumb line per leg | P2 |
| Wind Shift Detection | Direction change >10° sustained >5 min | P3 |
| Shift Exploitation Score | % of shifts where boat tacked within 3 min | P3 |
| Sector Performance | Rank within fleet at each sector boundary | P3 |

### 10.2 Rival-Enhanced Analysis

- Head-to-head VMC comparison vs each rival on same timeline
- Relative position chart: distance ahead/behind over time
- Divergence analysis: automated identification of gap changes with cause annotation
- Strategy scoring: did following rival X's historical route outperform your simulation?

---

## 11. Lac Léman Wind Patterns (Enhanced)

### 11.1 Synoptic Winds

| Wind | Direction | Characteristics | Tactical Impact |
|------|-----------|-----------------|-----------------|
| Bise | NE | Cold, dry, up to 80 km/h. 3/6/9-day cycles. Strongest Petit Lac. | Favours Swiss bank outbound. Consistent = fast leg to Le Bouveret. |
| Vent (SW) | SW | Warm, humid, 10–70 km/h. Highly variable. | Complex shifts in Grand Lac. Mid-lake can be best. |
| Vaudaire | S/SE | DUAL NATURE: (1) Foehn via Rhône valley — warm, sustained. (2) Thunderstorm outflow — violent gusts >50 km/h. Must distinguish. | Dominates Haut-Lac. Foehn = strategic asset; thunderstorm = survival mode. |
| Joran | NW | Descends from Jura. Often with thunderstorms. Rapid onset. | Fast, powerful, dominates Petit Lac. Can reverse race dynamics. |

### 11.2 Local Thermal Winds

| Wind | Direction | Description | Race Relevance |
|------|-----------|-------------|----------------|
| Séchard | NE | Light thermal, land to lake. Most common morning breeze. | Fills in early morning. Can set return leg strategy. |
| Morget | S | Afternoon thermal near Morges/Lausanne. Reliable in summer. | Predictable, localised. Exploit with Morges positioning. |
| Bornan | S | Thermal from Savoyard Alps on French shore. | Favours French bank in Grand Lac transit. |
| Fraidieu | NW | Cold thermal from Jura (distinct from Joran). Lighter, no storms. | Gentle night breeze in Petit Lac. |
| Vauderon | Variable | Complex thermal in Vaud region. | Localised, unpredictable but can provide wind in calm. |
| Môlan | S/SE | Southern thermal in Haut-Lac area. | Relevant for Le Bouveret approach and return. |

---

## 12. Live Race Day Architecture

### 12.1 Data Streams

| Stream | Source | Update Rate | Purpose |
|--------|--------|-------------|---------|
| Own position + speed | Geolocation API (GPS) | 1 Hz | Position, SOG, heading, VMG, progress |
| Compass heading | DeviceOrientationEvent | ~60 Hz | Heading at low speed, waypoint bearing |
| Fleet positions | SuiviRegate KMZ | ~60 min | Competitor awareness, rival tracking |
| Wind forecast | Open-Meteo multi-model | 1–3 hours | Tactical wind intel, bank scoring |
| Station observations | MeteoSwiss open data | 10 min | Ground truth wind validation |
| La Dôle wind | MeteoSwiss open data | 10 min | Upper-level flow indicator |

### 12.2 Race Day Dashboard

- Leaflet map: own position (gold), 5 rivals (coloured), fleet dots, wind arrows
- Compass rose with boat heading and bearing to next waypoint
- SOG vs polar target (% bar) and VMG
- Distance and ETA to Le Bouveret (outbound) or Genève (return)
- Bank scoring overlay
- Rival distance deltas along course axis
- Wind trend arrows (last 3 hours)
- Forecast vs observation deviation alert (>5 kn or >30°)
- Night mode toggle

### 12.3 MySuiviRegate Setup

- Install MySuiviRegate app on tracking phone
- Enter ACVL/SRS registration number + PIN + phone number
- Disable VPN, WiFi, Bluetooth during race
- Battery saver OFF
- Tactical app runs on SECOND device (iPad or second phone)

---

## 13. Strategy Tab (Rival-Aware Enhancement)

### 13.1 Rival-Informed Bank Scoring

- Wind-based score (existing): VMG comparison across zones from forecast
- Historical rival score (new): which bank did winning rivals choose in similar conditions?
- Composite recommendation with confidence level

### 13.2 Strategy Plan Builder

- Outbound strategy: preferred bank, decision points, change triggers
- Le Bouveret rounding: wide/tight, approach angle, expected wind
- Overnight transition plan: positioning when wind drops, drift strategy
- Return strategy: preferred bank, morning thermal expectations
- Follow-boat targets: which rivals to track visually

---

## 14. Race Simulation Mode (Enhanced)

Crew selects historical year (2021–2025) and plays through race making bank/tack decisions. Actual GPS tracks of the 5 target rivals play back in real time. The crew sees whether their decisions gain or lose positions against Leone, Ondine, Darnetal, Storm, and Little Nemo II.

---

## 15. Key Algorithms

- Polar interpolation: linear between TWS keys and TWA angles
- VMG/VMC calculator: real-time from TWS, TWA, bearing to mark
- Bank scoring: weighted VMG comparison + historical rival route overlay
- Wind direction interpolation: circular handling 0°/360° boundary
- KMZ parser: JSZip extraction + XML DOM parsing for gx:Track elements
- Route simulation: timestep-based position integration using polars + wind field
- Tack/gybe detection: heading change threshold with speed loss quantification
- Waypoint navigation: great-circle bearing + distance using Haversine formula
- Compass heading fusion: GPS heading (moving) + device compass (stationary)
- Rival identification: configurable name→sail number mapping table

---

## 16. Deliverable Files

| File | Description |
|------|-------------|
| index.html | Main PWA: Dashboard, Polars, Wind, Strategy, Rivals tabs |
| replay.html | Historical replay with SuiviRegate + rival highlighting + Leaflet |
| sim.html | Simulation mode with real rival data |
| analysis.html | Performance analysis dashboard |
| nav.html | GPS + compass waypoint navigation |
| weather-prep.html | D-14 to D-0 weather preparation workflow |
| sw.js | Service worker |
| manifest.json | PWA manifest |
| icon-192.png | Home screen icon |
| icon-512.png | Splash screen icon |

---

## 17. Roadmap

### Phase 1: Pre-Race Critical (Before June 5)
1. Integrate SuiviRegate KMZ data with real competitor GPS tracks
2. Build Little Johnka route simulation engine
3. Implement Rivals tab with 5 primary targets
4. Replace SVG map with Leaflet + OpenSeaMap ✅ DONE
5. Add GPS position tracking and compass waypoint navigation
6. Build weather preparation workflow dashboard (D-14 to D-0)
7. Upgrade wind forecasts to multi-model
8. Enhance wind reference with ASLeman thermal winds
9. Install MySuiviRegate on tracking phone
10. Deploy to HTTPS and field-test on Lac Léman

### Phase 2: Race Day Ready (June 5–7)
1. Enable live SuiviRegate KMZ polling
2. Activate race day dashboard
3. Run D-0 weather preparation final check
4. Test connectivity, offline resilience, battery management

### Phase 3: Post-Race Analysis (After June 7)
1. Download Little Johnka's actual SuiviRegate track
2. Build performance analysis
3. Run head-to-head comparison vs rivals
4. Compare actual vs simulation to calibrate model

---

## 18. Key Assumptions & Limitations

1. Polar accuracy: ORC polars represent optimistic performance. Real-world at 90–95% of polar speed.
2. Rival identification: relies on matching SuiviRegate boat names.
3. TCF comparisons assume stable handicaps year-to-year.
4. Weather models: limited historical coverage (2023+ for AROME HD).
5. OpenSeaMap tiles are community-maintained.
6. Compass accuracy ±10–15° on iPhone, degraded by nearby electronics.
7. GPS heading requires movement (>3 kn); compass fills in at low speed.
8. Simulation doesn't model fleet interaction (dirty air, right-of-way).
9. Bol d'Or is fundamentally different from Zugersee racing.
