# Zugersee Wind & Tactical Brief — Goldschäkel Dry Run

**For:** Little Johnka, Goldschäkel Regatta (YC Immensee), Sat 30 May 2026
**Purpose:** ground the app's Zugersee tactics in the lake's real wind behaviour.
**Headline:** Zugersee is a small, light, fickle lake — average wind only **~3 kt** (gusting ~6), prevailing **WSW**. The good breezes come from **Bise (NE), West/WSW, and Föhn (S)**. Reading pressure and the local geography matters more than boat speed.

---

## 1. Geography drives everything

The wooded **Chiemen peninsula** pinches the lake to ~1 km (Chiemen ↔ Lothenbach) and splits it into two very different basins:

| Basin | Where | Character | Wind implication |
|---|---|---|---|
| **Untersee** (north) | Cham ↔ Zug, down to the narrows | Broad (up to 4.6 km), flat, **no mountains on the NW side** | Cleanest, most open wind — best for Bise and West/WSW |
| **Chiemen narrows** | ~47.11 N, mid-lake | Constriction (~1 km), wooded peninsula | Wind **accelerates** and shifts here — "good for surprises" (YCI) |
| **Obersee** (south) | Immensee ↔ Walchwil ↔ Arth | Deep, **mountain-framed**: Rigi (W/SW), Rossberg (S), Zugerberg (E) | Sheltered, shifty, gusty; **Föhn-exposed**; Rigi wind-shadow on the W shore |

**The Goldschäkel starts off Immensee** — the NW corner of the Obersee, right by the Chiemen narrows. So the race sits in the most tactically complex part of the lake: the transition between the two basins.

---

## 2. The wind systems (and where to be)

*Assumption: these are climatology- and Revier-based generalisations; on the day, always trust live obs (Cham/CHZ station + what you see on the water) over the model.*

| System | Direction | Behaviour on Zugersee | Where the pressure is |
|---|---|---|---|
| **Bise** | NE | The classic working breeze. Channels down the long NE–SW axis and **accelerates through the Chiemen narrows** into the Obersee. Steady, shifts on cycles. | Stay in the corridor down the axis; the **broad Untersee** holds the cleanest Bise; expect a lift/pressure bump at the narrows. |
| **West / WSW** | W–SW | The **prevailing** wind. Clean where it comes off the flat open NW (Cham). In the Obersee the **Rigi casts a wind shadow over the west shore (Immensee side)**. | Untersee: anywhere clean. Obersee: favour **mid-lake / east side** for pressure; avoid parking under the Rigi on the W shore. |
| **Föhn** | S / SE | Warm, strong, gusty fall-wind. **Hits the Obersee (south) first and hardest** over the Rossberg/Rigi gap toward Arth/Immensee. | The **south end (Arth/Obersee)** has the breeze; the Untersee (north) is usually lighter. Reef early; respect the gusts. |
| **Thermal / lake breeze** | variable | On sunny, light days (the most common mode given ~3 kt average) the hills heat vs. the lake and drive an afternoon breeze. | Follow the **building breeze, often mid-lake**; it strengthens through the afternoon. **Evenings fill from the Obersee** — an evening beat south from Immensee can pay (YCI). |

---

## 3. How this is wired into the app (venue = zugersee)

- **Forecast/wind zones** are now the real basins: **Untersee · Chiemen · Obersee** (was Geneva/Lausanne/Bouveret).
- **9 wind-grid points** are placed on the water along the basins (Cham NW, Untersee mid, Zug bay, the narrows ×3, Immensee W, Obersee mid, Arth S) — verified inside the real shoreline so they sit on the lake, not on land.
- **Live wind station:** Cham (CHZ) on the NW shore is the on-lake reference; Luzern/Wädenswil/Oberägeri regional; Pilatus for gradient.
- **Bank-selection advisor** now classifies Zugersee patterns (Bise / Föhn / Westwind / Thermal) and gives Zugersee-specific advice (narrows acceleration, Rigi shadow, Föhn in the Obersee, evening Obersee fill) instead of Swiss/French-bank Léman logic. Ranking beat-VMG uses the lake's long axis (~343°) as the reference course since the RC sets the actual marks.
- **Map** uses a real dark base map so the shoreline is visible; the course title and tactical notes are Zugersee-specific.

---

## 4. Caveats

- The **SI / exact course / start time aren't published yet** (manage2sail) — the clock uses a provisional 30 May 10:00; update when the SI is out.
- The pattern thresholds (e.g. Föhn ≥ 8 kn from 120–200°) are reasonable defaults, not tuned to Zugersee micro-climate — refine after the dry run with what you actually see.
- Live competitor positions depend on the RC enabling TracTrac tracking (a small club regatta may not be tracked).

---

## Sources

- [ESYS Revierinformation — Zugersee](https://www.esys.org/rev_info/Schweiz/zugersee.html) (Peter O. Walter)
- [Windfinder — Wind statistics Zug / Zugersee](https://de.windfinder.com/windstatistics/zug_zugersee) (station climatology 2012–2026)
- [Windy — Zugersee wind map](https://www.windy.com/47.158/8.484) (detailed wind map, per ESYS)
- [Yacht Club Immensee — Revier Zugersee](https://yachtclubimmensee.clubdesk.com/zugersee) (Chiemen / evening Obersee local knowledge)
- [Swiss Wind Atlas (BFE)](https://www.uvek-gis.admin.ch/BFE/storymaps/EE_Windatlas/?lang=de) (modelled mean wind, Mittelland)
- OpenStreetMap relation 540344 (Zugersee shoreline geometry)
