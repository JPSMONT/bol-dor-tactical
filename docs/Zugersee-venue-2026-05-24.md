# Zugersee Venue Profile — Build Summary

**Date:** 24 May 2026 · **For:** Goldschäkel Regatta dry run, **Sat 30 May 2026** (YC Immensee, Zugersee)
**Scope delivered:** Full Zugersee venue profile (the "maximal" option), behind a venue switch. The Bol d'Or (Lac Léman) default is **unchanged**.

---

## How to use it

- **Activate Zugersee:** load `…/bol-dor-tactical/?venue=zugersee`, or tap **Zugersee** on the venue pill (bottom-right corner). The choice is remembered (localStorage), so once set it sticks until you switch back to **Bol d'Or**.
- **Switch back:** tap **Bol d'Or** on the pill, or load `?venue=boldor`.

## What the Zugersee profile changes

| Area | Bol d'Or (default) | Zugersee profile |
|---|---|---|
| Map center / bounds + lake outline | Lac Léman | Zugersee (Zug → Arth, incl. Immensee arm) |
| Forecast grid | 9 pts (Geneva/Lausanne/Bouveret) | 9 pts (Zug / Walchwil / Arth) via Open-Meteo |
| Wind stations | GVE/CGI/PUY/VEV/AIG/EVI | **CHZ (Cham, on-lake)** + LUZ/WAE/AEG/PIL |
| Wind-pattern classifier + guide | Bise/Vaudaire/Joran/Séchard… | Bise / Föhn / Westwind / thermal / Chiemen |
| Course / waypoints | 7-pt Bol d'Or round trip | Provisional start off Immensee (RC sets course) |
| Race clock / countdown | 6 Jun 2026, 10:00 | **30 May 2026, 10:00 (provisional)** |
| Rivals / live tracking | SuiviRegate KMZ archives | Link-out to Goldschäkel on **TracTrac / manage2sail** |
| Live cockpit (GPS, compass, polars, PPR, Trim Coach, battery, offline) | — | **Unchanged — lake-agnostic, this is what the dry run validates** |

## What's verified

- Full inline JS syntax-valid; `sw.js` valid (cache bumped **v4 → v5**).
- **Bol d'Or path byte-identical:** Lac Léman data literals untouched; every venue branch reproduces the original value; all four countdown strings reproduce exactly.
- Zugersee config runtime-tested (16-pt lake, 9 grid pts, 5 stations, 3 waypoints; all points inside the lake bbox; clock = 30 May 10:00 CEST +8 h/+10 h).
- Zugersee wind classifier runtime-tested (NE→Bise, S+Föhn→Föhn, SW→Westwind, calm→Calm).

## Caveats / assumptions (flagged)

- **Needs an on-device smoke test** before/at the dry run: GPS-on-water on Zugersee, offline behaviour, the venue toggle, night mode. I can't run the live PWA from here.
- **Start time + course are provisional.** The SI isn't published yet (manage2sail). The clock uses 30 May 10:00 CEST as a placeholder — update once the SI is out.
- **Live TracTrac positions are link-out only.** manage2sail's "powered by TracTrac" is a platform footer, not a guarantee this 13-boat club regatta is tracked. If it is, the Rivals "Open TracTrac" button takes you to it; if not, there are simply no live positions (expected).
- **Lake polygon is approximate** (coarse outline; OpenSeaMap tiles show the true shoreline underneath).
- The Rivals tab still contains the Bol d'Or historical-KMZ controls in Zugersee mode (only the live/banner part is venue-aware) — harmless, just ignore them on the day.

## Suggested next steps

1. Smoke-test `?venue=zugersee` on the phone this week.
2. Pair it with the **service-worker offline fix** (the open QA issue) so the dry run also validates offline on Zugersee.
3. After the SI publishes, update the provisional start time (and course marks if you want them) — one-line config change in `ZG`.
