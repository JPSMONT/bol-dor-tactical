# Live Instruments — Architecture Spec (PRD v6, Phase 1)

**Date:** 24 May 2026 · **Owner:** Joao Monteiro · **Boat:** Little Johnka (CYD 27 ORC)
**Status:** Architecture decision spec. **Revised 24 May 2026** after re-checking the YDWG-02 Web Gauges (an earlier draft overstated that "a browser can't read the gateway" — corrected in §1).

---

## 1. The two facts that drive this

1. **The Yacht Devices YDVR-04 is a Voyage *Recorder*, not a live source for apps.** It records the NMEA 2000 bus to SD (`.DAT`/`.CAN`) for *post-race* analysis; its WiFi is for downloading recordings. Live streaming is a different product — the **YDWG-02 Wi-Fi Gateway** (NMEA 2000) or **YDWN-02** (NMEA 0183). So the PRD's "YDVR-04 WiFi bridge" is a misnomer: what we have is the recorder.

2. **A browser *can* read a Yacht Devices gateway live — just not via its raw TCP/UDP ports.** (This corrects the earlier draft.)
   - The gateway's *documented external* NMEA servers are **TCP and UDP** (and RAW/TCP for Expedition). A browser has no raw sockets, so a PWA can't use those ports.
   - **But** the YDWG-02 / YDWN-02 also serve their own **Web Gauges** — a JavaScript app that shows live STW, TWS/TWA/TWD, AWA/AWS, COG/SOG, heading, depth, etc. **in any browser, no app, no internet** (full data list in YD's Web Gauges guide). The Web Gauges receive "the same data sent to **Server #1**." For browser JS to receive a live NMEA stream, the device must expose it over a **browser-compatible transport — a WebSocket** behind the Web Gauges.
   - **Therefore a custom PWA can very likely read live data straight from the gateway** by connecting to that same WebSocket and parsing NMEA 0183 — **no Raspberry Pi / Signal K required.** *Assumption to confirm: the exact WebSocket endpoint/port is in the YDWG-02 manual §XI ("Web Gauges") / §IV ("Application Protocols"); it's the device's own feed, not a published third-party API, so it can change with firmware (YD shipped a "New Web Gauges" update Feb 2026).* 

The YDVR-04 still has a clear role: **Debrief** (high-rate instrument data from the SD card, post-race).

---

## 2. Options (cheapest → most robust)

| Option | Path to the PWA | Cost / kit | Verdict |
|---|---|---|---|
| **B1. Gateway-direct (Web-Gauge WebSocket)** | YDWG-02 → its built-in WebSocket → PWA parses NMEA 0183 | **YDWG-02 only (~€249)** | **Likely simplest & cheapest.** Reuses the device's own browser feed — no extra computer. Risk: it's an internal feed (confirm endpoint; firmware-fragile). |
| **B2. Gateway + tiny bridge** | YDWG-02 TCP → small TCP→WebSocket proxy (phone/Pi) → PWA | YDWG-02 + a device to run the proxy | Fallback if B1's feed isn't cleanly reusable. You maintain the bridge. |
| **A. Signal K** | N2K → Signal K (Pi) → documented WebSocket/REST → PWA | Pi + N2K interface (~€130–260) or feed Signal K from the gateway's TCP | **Most robust** — documented API, clean data model, auto-reconnect, multi-source, also logs for Debrief. More kit/setup. |
| **D. YDVR-04 SD** | Record → export `.DAT` → CSV/GPX → import | You already own it | **Post-race only** — this is Debrief, not live. |

---

## 3. Recommendation

1. **First, confirm the gateway's live browser feed (cheap win).** From the YDWG-02 manual §XI/§IV, find the Web-Gauge **WebSocket** endpoint (host/port/path) and the line format (NMEA 0183 sentences). If it's stable and reusable, **Option B1 is the path**: buy one YDWG-02, point the PWA's Layer-1 client at `ws://<gateway>/…`, parse the sentences, done — no Pi.
2. **If you want robustness/multi-source/logging**, use **Signal K** (Option A). It's the documented standard and a better long-term base, at the cost of a small always-on computer.
3. Either way, **keep the YDVR-04 for Debrief** (SD `.DAT` → CSV via the free YDVR Converter → import into the app's Debrief for instrument-grade post-race analysis).

**NMEA 0183 sentences → cockpit tiles** (what to parse, whichever transport):

| Sentence (NMEA 0183) | Field | Cockpit use |
|---|---|---|
| `MWV` (true) / `MWD` | TWS / TWA / TWD | measured wind state, real polar target |
| `MWV` (apparent) | AWA / AWS | apparent wind |
| `VHW` | STW (boat speed through water) | **true polar efficiency** (replaces GPS-SOG approx) |
| `VTG` | SOG / COG | speed / course over ground |
| `HDG` / `HDT` | heading | heading |
| `DBT`/`DPT` | depth | (future) |

**Integration:** add a Layer-1 module — a WebSocket client (to the gateway or Signal K), parse → normalise into the existing wind/perf globals, flip `isLiveInstrumentsActive()` true so the cockpit's polar-efficiency + wind-state tiles switch tag from "model" (amber) to "live" (green) and the maneuver tracker uses **STW instead of GPS-SOG**. **Graceful fallback:** if the socket drops, revert to the model-wind path automatically (no race-day regression); auto-reconnect.

---

## 4. Race-day reliability

The live link is an **upgrade layer, never a dependency**. Model-wind + phone-GPS stays the always-available baseline; if the gateway/Signal K/WebSocket fails, the tiles silently fall back to "model." Test the full chain at the dock first. The gateway must hold a fixed WiFi role (its own AP, or join the boat AP) and the tactical phone must be on that network.

---

## 5. Decisions for Joao

1. **Pursue live before the Bol d'Or, or treat the Bol d'Or as a Debrief/data-collection run** and add live after? (Roadmap open question #4.)
2. If yes: **Option B1 (YDWG-02 gateway-direct, cheapest)** vs **Option A (Signal K, most robust)**. The deciding input is whether the gateway's Web-Gauge WebSocket is cleanly reusable — a quick read of the YDWG-02 manual §XI settles it (and I can dig into the exact endpoint if you want).
3. Confirm what your **YDVR-04** can actually output (record-only vs any live WiFi) — you own the unit; its manual settles it in 2 minutes.

No app code is needed for live until this is decided. The **Debrief** path (Phase 2, shipped) already extracts value now and will accept YDVR SD imports later.

---

## Sources

- [Yacht Devices — Wi-Fi Gateway Web Gauges guide](https://www.yachtd.com/products/web_gauges.html) (JS app in any browser; full live-data list; "receives the same data sent to Server #1")
- [Yacht Devices — NMEA 2000 Wi-Fi Gateway YDWG-02](https://www.yachtd.com/products/wifi_gateway.html) (TCP/UDP servers; built-in web gauges) · [User Manual PDF](https://www.yachtd.com/downloads/ydwg02.pdf) (§XI Web Gauges, §IV Application Protocols, App. D NMEA 2000↔0183)
- [Yacht Devices — NMEA 0183 Wi-Fi Gateway YDWN-02](https://www.yachtd.com/products/wifi_0183_gateway.html)
- Yacht Devices YDVR-04 Voyage Recorder (records N2K to SD; WiFi for download) — per product line
- Signal K — open marine data standard (NMEA → documented WebSocket/REST)
