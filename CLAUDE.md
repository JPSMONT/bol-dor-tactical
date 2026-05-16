# Bol d'Or Tactical PWA — Project Instructions

## Project Overview

Tactical sailing PWA for **Little Johnka** (CYD 27 ORC, SUI 6116) racing the Bol d'Or Mirabaud on Lac Léman. The race is ~70 NM, starts 10h00 Saturday from Genève, finishes at Le Bouveret. Duration: ~18-24 hours including overnight sailing.

**Owner:** Joao Monteiro (joao@pinto.ventures)
**Club:** OSCA (Obersee Segel Club Arth)
**Crew:** 2 core + occasional guests

## Boat Data — Little Johnka CYD 27 ORC

```
LOA: 8.25m | Displacement: 1,780 kg | Yardstick: 94 | TCF: 1.029
Sails: Main 27.1 m², Jib 17.7 m², Spinnaker 47.2 m²
NO Drifter. NO Code 0. Only three sails.
```

### ORC Polar Data (BTV in knots)

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

## PRD v4.0 — Feature Scope

### Current State (Already Built)
The PWA currently has these tabs working:
- **Dashboard** — Wind overview with current conditions card, forecast summary
- **Polars** — Interactive polar diagram with Little Johnka's ORC data
- **Wind** — Multi-model forecast (AROME HD 1.3km + ICON D2 2km) via Open-Meteo
- **Strategy** — Bank selection advisor with leg-by-leg tactical notes (NOW UPGRADED TO LEAFLET MAP)
- **Race Sim** — Race simulation using live wind data, simulates race starting in 30 min
- **Replay** (replay.html) — Historical 2024 race replay with wind field overlay and time slider

### Build Order (What to Build Next)

#### Phase 1: Map & Navigation Foundation
**1. Leaflet + OpenSeaMap Map** ✅ DONE
- Replace canvas map with Leaflet + OpenSeaMap nautical tiles
- Full Lac Léman race course from Genève to Le Bouveret
- All existing features as Leaflet layers

**2. GPS + Compass Waypoint Navigation**
- Live GPS position on Leaflet map with boat icon
- SOG (Speed Over Ground) and COG (Course Over Ground) display
- Bearing and distance to next waypoint
- Compass-style heading indicator
- Waypoints: Genève start → Yvoire → Thonon → Évian → Le Bouveret finish
- Auto-advance to next waypoint when within proximity
- Performance vs polar: show target speed for current TWA/TWS vs actual SOG

#### Phase 2: Competitor Intelligence
**3. Rivals Tab (Competitor Tracking)**
- New "Rivals" tab showing competitor positions and performance
- Data source: MySuiviRegate (websocket-based, real-time during race)
  - Race feed URL pattern: `wss://www.mysuiviregate.com/ws/race/{raceId}`
  - Fallback: periodic HTTP polling of public race page
- TCF3 class focus — show competitors in our rating band
- For each rival: name, position, distance to us, relative gain/loss
- Pre-race: show registered competitors list with their ratings
- During race: live position dots on the Leaflet map
- Competitor data from DeepRegatta API for historical analysis:
  - `https://oscar.deepregatta.com/?race=BOL25` (2025 Bol d'Or data)
  - Available races: BOL25, BOPM24, BOM23, BOM22, BOM21, BOM19, etc.

**4. Weather Prep Dashboard**
- Pre-race weather preparation workflow
- Multi-model wind comparison: AROME HD vs ICON D2 side by side
- Station observations overlay on map (real MeteoSwiss data)
  - Wind speed: `https://data.geo.admin.ch/ch.meteoschweiz.messwerte-windgeschwindigkeit-kmh-10min/...json`
  - Wind gusts: `https://data.geo.admin.ch/ch.meteoschweiz.messwerte-wind-boeenspitze-kmh-10min/...json`
  - Format: GeoJSON, coordinates in CH1903+ (EPSG:2056), values in km/h (÷1.852 for knots)
- Wind pattern identification (Bise, Séchard, thermal, lake breeze)
- Decision timeline: key go/no-go checkpoints before race
- AROME HD underestimates mid-lake and Haut-Lac wind by 5-6 kn — flag this

#### Phase 3: Replay & Simulation
**5. Replay Enhancements**
- Upgrade replay.html to use Leaflet map (match main app)
- Add competitor ghost tracks from DeepRegatta historical data
- Speed slider (0.5x to 10x)
- Leg-by-leg performance breakdown overlay
- Wind shift markers on timeline

**6. Race Simulation vs Real Rivals**
- Extend existing Race Sim mode with competitor ghosts
- Use DeepRegatta historical data for competitor speed models
- Show projected positions of key rivals based on their historical performance
- Time-to-finish estimates for us vs competitors

## API Endpoints

### Open-Meteo (Forecasts)
- **Base URL:** `https://api.open-meteo.com/v1/forecast`
- **Auth:** None. Free tier. CORS-friendly.
- **Params:** `latitude`, `longitude` (comma-separated for multi-point), `hourly=wind_speed_10m,wind_direction_10m,wind_gusts_10m`, `wind_speed_unit=kn`, `models=<model_name>`
- **Models:** `meteofrance_arome_france_hd` (1.3km), `icon_d2` (2km)
- **Quirk:** Response keys suffixed with model name (e.g., `wind_speed_10m_meteofrance_arome_france_hd`). Check both suffixed and unsuffixed keys.

### MeteoSwiss (Station Observations)
- **Wind speed:** `https://data.geo.admin.ch/ch.meteoschweiz.messwerte-windgeschwindigkeit-kmh-10min/ch.meteoschweiz.messwerte-windgeschwindigkeit-kmh-10min_en.json`
- **Wind gusts:** `https://data.geo.admin.ch/ch.meteoschweiz.messwerte-wind-boeenspitze-kmh-10min/ch.meteoschweiz.messwerte-wind-boeenspitze-kmh-10min_en.json`
- **Auth:** None. Free open data. CORS-friendly.
- **Format:** GeoJSON FeatureCollection. Coordinates in **CH1903+ (EPSG:2056)**, NOT WGS84. Filter by station `id`.
- **Speed conversion:** km/h → ÷ 1.852 = knots.
- **Relevant Lac Léman stations:** PUY (Pully), GVE (Genève-Cointrin), CGI (Nyon/Changins), AIG (Aigle), EVI (Évian area)

### DeepRegatta (Historical Race Data)
- **Base URL:** `https://oscar.deepregatta.com/`
- **Race data:** `?race=BOL25` etc.
- **Available:** Track data, rankings, sector times, wind shift analysis
- **Quality varies:** "fair" for most Bol d'Or races, "excellent" for TF35

### MySuiviRegate (Live Competitor Tracking)
- **Web URL:** `https://www.mysuiviregate.com/`
- **Protocol:** WebSocket-based real-time tracking during race
- **Fallback:** HTTP polling of public race page
- **Note:** API investigation deferred to race week — plan to reverse-engineer websocket protocol

## Lac Léman Race Course Waypoints

```javascript
const WAYPOINTS = [
  { name: "Genève (Start)", lat: 46.2044, lon: 6.1556 },
  { name: "Yvoire", lat: 46.3710, lon: 6.3270 },
  { name: "Thonon", lat: 46.3700, lon: 6.4800 },
  { name: "Évian", lat: 46.4010, lon: 6.5890 },
  { name: "Le Bouveret (Finish)", lat: 46.3910, lon: 6.8570 }
];
```

## Lac Léman Wind Patterns

| Pattern | Direction | Key Characteristics |
|---------|-----------|---------------------|
| Bise | NE | Cold, dry, can persist for days. Strongest Petit Lac. |
| Vent (SW) | SW | Warm, humid, often before fronts. Good downwind sailing. |
| Séchard | N/NW | Foehn-like, dry, gusty near Jura. Rare but strong. |
| Lake Breeze | Variable | Thermal, develops afternoon, cross-lake. Key for light-air legs. |
| Joran | NW | Evening katabatic from Jura. Can surprise near north shore. |
| Vaudaire | SE | Foehn from Rhône valley, Haut-Lac specialty. Can be 25+ kn. |
| Rebat | Variable | Post-frontal thermal, afternoon, unstable. |

**Critical note:** AROME HD model underestimates mid-lake and Haut-Lac wind by 5-6 knots. Always cross-reference with station observations.

## Design Principles

- Night-vision friendly by default (dark theme with blue/teal accents)
- Day mode via toggle or system `prefers-color-scheme`
- CSS variables: `--bg`, `--bg2`, `--bg3`, `--card`, `--tx`, `--tx2`, `--tx3`, `--acc`, `--acc2`, `--warn`, `--err`
- Responsive breakpoints: 600px (phone), 900px (tablet/laptop)
- Auto-refresh every 10 minutes
- Single-file HTML architecture (inline JS/CSS, CDN dependencies only)
- PWA with service worker for offline capability

## GitHub Repository

- **Repo:** https://github.com/JPSMONT/bol-dor-tactical (Private)
- **Branch:** main
- **Push with:** `git -c credential.helper= push -u origin main` (use JPSMONT token)

## Racing Context

### Performance Baseline (Yardstick 2021-2024)
- 19 races, 1 DNF. Average rank: 6.9
- 2 wins, 9 podiums (47%), 11 top-5 (58%)
- Strong in small fleets, weak in larger ones
- Primary improvement: starts in big fleets, consistency

### Key Competitors (TCF3 class)
- Analyse via DeepRegatta historical data
- Focus on boats in TCF 0.95-1.05 rating band
