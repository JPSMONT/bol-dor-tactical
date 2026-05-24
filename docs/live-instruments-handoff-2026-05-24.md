# Live Instruments — Handoff / Resume Note

**Date:** 24 May 2026 · **Owner:** Joao Monteiro · **Status:** ⏸ **PARKED — resume after the yard install (week of 26 May 2026)**, once we know which device is on the boat.

This captures the live-instrument investigation so we can continue without re-doing the research. Full technical detail is in `PRD-v6-live-instruments-spec.md`; this note is the decision + resume checklist.

---

## The question
Can the Race cockpit show *measured* instrument data (boat speed through water, true wind) live, and what hardware does that require?

## What we established (24 May 2026)

1. **You can't read the data off the Garmin directly.** The GPSMAP 721's WiFi is closed — it runs ActiveCaptain (charts/community) and Helm (screen mirroring), but **does not stream NMEA to third-party apps**. A custom web app can't read live instruments from the Garmin WiFi.
2. **But your instruments are all on the NMEA 2000 bus**, so one bus-tap device unlocks everything the cockpit wants:
   - **DST800** → boat speed *through water* (the key thing GPS can't give)
   - **gWind / GNX Wind** → measured true & apparent wind
   - **GPSMAP 721** → GPS / COG / SOG
3. **Device roles** (and "YDWG-04" does not exist):
   - **YDWG-02** = NMEA 2000 Wi-Fi *Gateway* → exposes a **browser-readable WebSocket** (its Web Gauges) → the PWA can read it directly. **This is the device for LIVE.**
   - **YDVR-04** = Voyage *Recorder* → records the bus to SD; **no live output**. This is the **Debrief** source (SD → convert → import).
4. **Conclusion:** live cockpit needs a **YDWG-02** (or a Signal K server). The YDVR-04 alone gives Debrief only, not live.

## Decision depends on what gets installed next week

| Installed | Live cockpit? | Resume action |
|---|---|---|
| **YDWG-02** (gateway) | ✅ yes | Build the Layer-1 WebSocket client → read its Web-Gauge feed → tiles flip model→live. |
| **YDVR-04** only (recorder) | ❌ no live | Build the `.DAT`→import path for **Debrief**. Live would need a YDWG-02 added later. |
| **Both** | ✅ live + ✅ Debrief | The ideal setup — do both. |
| Something else / unsure | — | Send me the model + N2K wiring; I'll re-assess. |

## To resume, send me

1. **Which device(s) were installed** (exact model code on the unit/label).
2. **If a YDWG-02:** how its WiFi is set (its own access point, or joined to a boat WiFi), its IP/SSID. I'll pull the exact **Web-Gauge WebSocket endpoint** from the YDWG-02 manual §XI/§IV (host/port/path + sentence format).
3. **Confirm** STW (DST800) and true wind (gWind) actually show up on the bus (they should — they're N2K instruments).

## Then I'll build (Phase 1)

A **Layer-1 ingestion module**: a WebSocket client (to the gateway, or Signal K) → parse NMEA 0183 (`MWV`/`MWD` true wind, `VHW` STW, `VTG` SOG/COG, `HDG` heading) → normalise into the existing wind/perf globals → flip `isLiveInstrumentsActive()` to true. Effect: the cockpit's **polar-efficiency** and **wind-state** tiles switch tag from "model" (amber) to "live" (green), and the **maneuver-loss tracker uses STW instead of GPS-SOG**. Graceful fallback to the model-wind path if the link drops (no race-day regression).

## References
- `PRD-v6-live-instruments-spec.md` — full architecture, options (gateway-direct vs Signal K), NMEA→tile map, hardware list.
- `PRD-v6-ai-tactician-roadmap.md` — Phase 1 in the overall sequence.
- Boat kit: https://www.cyd27.com/handbook/instruments

*Nothing app-side is blocked by this. The cockpit, maneuver-loss tracker, and Debrief all run on GPS + model wind today — the dry run on 30 May works fully without any of this hardware. The instruments are a measured-truth upgrade layer.*
