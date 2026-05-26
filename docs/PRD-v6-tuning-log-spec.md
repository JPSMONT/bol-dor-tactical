# Tuning Log — Spec (PRD v6 addendum, Phase 1.6)

**Date:** 24 May 2026 · **Owner:** Joao Monteiro · **Boat:** Little Johnka (CYD 27 ORC)
**Status:** **Specced, not built.** The scoped revival of "Performance Memory" from `PRD-v5-addendum.md` §2 — narrowed from "post-race learning" to *"in-race tuning experiments, timestamped, joinable to the rest of the dataset for later analysis."*

---

## 1. The problem

Little Johnka has many independently-tunable controls (backstay, jib car, outhaul, cunningham, vang, traveller, halyards). The only way to know which combinations actually work in given wind/sea conditions is to log them. Today that knowledge lives in heads and on paper and is reinvented each season. The Tuning Log captures **setup + conditions + polar % + note** at the tap of a button, with timestamps that join to the GPS track, maneuver log, per-minute polar buckets and (post-install) the YDVR-04 SD recordings — so the crew gradually builds a real *"what worked best in X kt close-hauled"* dataset.

## 2. Where it lives

A new **Tuning log** card on the **Polars tab**, below the polar diagram. The polar diagram is the reference; the log adds the empirical evidence.

## 3. Data model

Each entry is stored in `localStorage` (`tuning_log_v1`, array of objects, ~200 B each):

```json
{
  "t": 1717182000000,
  "mode": "training" | "race",
  "venue": "boldor" | "zugersee",
  "wind": { "tws": 12.3, "twa": 42, "twd": 220, "src": "model" | "live" },
  "perf": { "sog": 5.8, "target": 6.0, "ratio": 0.97, "vmg": 4.3 },
  "settings": {
    "backstay": 6, "jib_car": 3, "outhaul": 7, "cunningham": 4,
    "vang": 5, "traveller": 0, "halyard_main": 6, "halyard_jib": 5
  },
  "sail": "jib" | "spi",
  "note": "weather helm OK, tried more BS"
}
```

**Auto-filled** (no manual input): `t`, `mode` (from `raceState()`), `venue` (from `ACTIVE_VENUE`), `wind` and `perf` (from the cockpit's `computePerf()` at save-time).
**Manual**: `settings` sliders (default = the last saved entry), `sail` toggle, `note`.

## 4. Settings list — Little Johnka (the Full 8)

| Key | Label | Scale | Notes |
|---|---|---|---|
| `backstay` | Backstay (BS) | 0–10 | Mast bend / forestay tension — biggest upwind dial |
| `jib_car` | Jib car (JC) | 1–10 | Fore-aft click position |
| `outhaul` | Outhaul (OH) | 0–10 | Main foot tension |
| `cunningham` | Cunningham (CU) | 0–10 | Main luff tension / draft |
| `vang` | Vang (V) | 0–10 | Twist control (heavy-air upwind / downwind) |
| `traveller` | Traveller (TR) | −5 … +5 | Centred = 0 |
| `halyard_main` | Halyard main (HM) | 0–10 | Luff tension / draft position |
| `halyard_jib` | Halyard jib (HJ) | 0–10 | Luff tension / draft position |
| `sail` | Sail | jib / spi | Two-state toggle |

Labels and scales are stored in `localStorage` (`tuning_labels_v1`) so they're rename-able / re-scalable without code changes (e.g., switch to absolute units like mm for backstay if you measure with a Loos gauge).

## 5. UX

### 5.1 Snapshot button

A single **"⊕ Log current setup"** button at the top of the Tuning Log card. One tap → modal.

### 5.2 Snapshot modal

**Auto-filled, read-only** at the top:
- *Now* — T+HH:MM:SS from race start, or absolute clock outside a race window.
- *Wind* — TWS kn, TWA°, TWD° (source tag: model / live).
- *Perf* — SOG, polar target, polar % (colour-coded).
- *Mode + venue* — small badge.

**Editable**:
- Eight settings sliders (default = last saved values; first-ever entry = 5 / 3 / 5 / 3 / 3 / 0 / 5 / 5).
- Sail toggle (Jib / Spi).
- Free-text *Note* (one line).

Buttons: **Save** · **Cancel**. Save appends to `tuning_log_v1` and re-renders the table.

### 5.3 Recent entries table

| Column | |
|---|---|
| time | relative ("−3m") if same day, else absolute |
| TWS · TWA | kn · ° |
| polar % | colour-coded (≥97% green, 90–96% amber, <90% red) |
| settings summary | `BS · JC · OH · V` |
| note | truncated |

Tap a row to expand the full 8 controls + sail + full note. Default 20 most recent; **Show all** toggle. Filters: wind band (≤6 / 6–12 / 12–18 / 18+ kt) and point of sail (TWA <90 / ≥90).

### 5.4 Best by wind band

A small stripe at the bottom of the card. For each TWS band (close-hauled by default, TWA filter applied), shows the top-1 entry by polar %, formatted as `<polar%> — BS x / JC y / OH z / V v`. Empty if no data yet for that band.

### 5.5 CSV export

**Export CSV** link at the bottom — flattens entries with one row per snapshot. Columns: `t_iso, t_ms, mode, venue, tws, twa, twd, sog, target, polar_pct, vmg, sail, backstay, jib_car, outhaul, cunningham, vang, traveller, halyard_main, halyard_jib, note`. For pasting into Excel / joining to a GPS-track CSV in a Python notebook.

## 6. Multi-device & Advisor-mode integration

- The Tuning Log is **per-device** (`localStorage`). The **Primary** device owns the log.
- On **Advisor** devices: the "Log current setup" button is hidden; the card still shows the read-only entries table so the crew can *see* the recent setups for discussion, but cannot log.
- *Future*: optional sync of entries from Primary → Advisor over WebRTC or a small server-side store (out of scope for v1).

## 7. Acceptance criteria

- A snapshot completes in ≤10 s on the boat (one tap; sliders default to the last saved values; one optional note line).
- Entries persist across reloads, and survive service-worker cache bumps (use a stable key; don't clear in `activate`).
- Filtering Recent entries by wind band returns the expected subset.
- CSV export joins cleanly to a GPS-track CSV by `t_ms`.
- Advisor devices show entries but cannot log.
- Storage stays under 1 MB after a season of logging (~5000 entries × ~200 B).

## 8. Future / stretch (v2+)

1. **Polar-diagram overlay** — render each logged entry as a dot on the polar curve at its (TWS, TWA), coloured by polar %. A visual scatter of where the boat actually performs vs the polar across the log.
2. **Voice notes** — tap-to-record a 5 s voice memo per entry (Web Audio API) → much faster than typing while sailing.
3. **YDVR Debrief join** — post-race, import the YDVR-04 SD `.DAT` (via the YDVR Converter or a custom importer), join by timestamp, and replace the model-wind / GPS-SOG fields with measured TWS / TWA / STW → instrument-grade tuning analysis.
4. **Cross-session best by band** — persistent recommendations across races/training, not just session.
5. **Trim Coach hook** — when live polar % drops, surface the most-similar recent entry as a hint: *"in 12 kn close-hauled you ran BS 8 / JC 4 / OH 9 / V 6 last time and got 102%."*
6. **Auto-snapshot on maneuvers** — emit a tuning entry at every detected tack/gybe with the live settings (or last-known) so even passive use builds the dataset. Friction-free; risk of duplicate entries — make optional.

## 9. Open questions

1. **Scales** — 0–10 sliders OK, or absolute units (backstay mm, traveller cm off-centreline)? Numbers are easier to remember, units are more reproducible across crews. Suggest 0–10 for v1, units later if useful.
2. **Wind-band thresholds** — 6 / 12 / 18 kt, or your own? Standard for Lac Léman / Zugersee planning.
3. **Storage cap** — keep last 1000 / 5000 / unlimited? Suggest unlimited with a soft warning at 5000.
4. **Auto-snapshot on tacks/gybes (v2 #6)** — yes or no? Pro: zero friction, more data. Con: noisy if settings rarely change.
5. **First-tier integration with Debrief** — show tuning entries in the post-race Debrief card alongside maneuvers? Cheap to add when v1 lands.

## 10. References

- `PRD-v5-addendum.md` §2 (Performance Memory — the original parent concept).
- `PRD-v6-ai-tactician-roadmap.md` (Phases 0 / 1.5 / 2 v1 shipped; this is Phase 1.6).
- Existing in-app analogues: cockpit `computePerf()` (Polar efficiency), maneuver log (`maneuver_log_v1`), per-minute polar buckets (`perf_buckets_v1`).
