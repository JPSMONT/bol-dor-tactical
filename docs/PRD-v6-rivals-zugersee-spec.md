# Rivals Tab — Zugersee Cup version (Spec)

**Date:** 26 May 2026 · **Owner:** Joao Monteiro · **Boat:** Little Johnka (CYD 27 ORC, Yardstick **94**)
**Status:** **Specced, not built.** Replaces the SuiviRegate-based Rivals tab on the Zugersee venue. Bol d'Or Rivals tab unchanged.

---

## 1. The problem

The current Rivals tab is built around the **SuiviRegate** ecosystem (Lac Léman): KMZ track downloads, 5 hand-picked targets (Leone / Pertuiset / Monachon / Rottet / Borter), per-rival deep-dive panels. None of that maps to the Zugersee Cup, where:

- The fleet is different (Swiss Yardstick boats from YCZ / SCC / YCI / OSCA, not Lac Léman ORC big-boats)
- The tracker is **Kwindoo**, not SuiviRegate
- "Primary targets" don't exist — what matters is **which boats are in your Yardstick class** (similar handicap → direct corrected-time competitors)
- The series spans 4 events with 4 different host clubs

A venue-aware Rivals tab that renders one thing on Bol d'Or (today's behaviour) and a Kwindoo-centric Zugersee Cup view when `IS_ZUG`.

## 2. Scope

**In scope (v1):**

1. **Per-event Kwindoo viewer.** Embed Kwindoo's live + replay tracker via `<iframe>` for the active event in the Zugersee Cup series.
2. **Per-event URL configuration.** Joao pastes the Kwindoo URL once per event (YCI publishes them shortly before race day) → persisted in `localStorage`, retrievable for all 4 events of the season.
3. **Yardstick class panel.** A small reference table — Little Johnka's Yardstick (94) at the top, plus the boats in the same band (90–98, say) that Joao is likely competing against. Editable; Joao adds boats he sees in the fleet.
4. **Event-aware banner.** A short header card showing which Zugersee Cup event is "active" (Goldschäkel 30 May / Blauband 27 Jun / Rigi Anker 29 Aug / Chomer Bär 12 Sep), with countdown until start.
5. **Event registration / NOR links.** Direct links to manage2sail for entries and to each host club's announcement page.

**Out of scope (v1):**

- In-app per-rival analysis dashboards (the SuiviRegate deep-dive panel). The Kwindoo iframe is the analysis surface for now.
- KMZ track download / replay overlay on the Strategy map. Possible v2 if/when Kwindoo exposes a track export.
- Scraping Kwindoo's internal API for boat lists or live position data. No documented public API; reverse-engineering breaks on every Kwindoo release.

## 3. Data sources

| Source | What we get | How |
|---|---|---|
| **Kwindoo `tracking/<event-id>` page** | Live + replay tracker UI | `<iframe>` embed inside a Rivals-tab card |
| **manage2sail event pages** | Boat list (Entries), NOR, results | External link (open in new tab) |
| **zugerseecup.ch** | Series calendar, host clubs, Yardstick Reglement PDF, Yardstick Liste PDF | Hard-coded once (rarely changes); links from the Rivals tab |
| **Swiss Sailing Yardstick Liste 2025** | Handicap numbers per class | Hard-coded snippet for the most relevant boats; full list linked out |
| **localStorage `zsc_events_v1`** | Per-event Kwindoo URLs (and any annotations) Joao pastes in | Persisted on the Primary device |

## 4. Event registry — hard-coded

```js
ZG.zscEvents = [
  { id:'goldschaekel-26', date:'2026-05-30', name:'Goldschäkel-Regatta',
    host:'YCI Immensee',  hostUrl:'https://www.yci.ch/',
    m2sUrl:'https://www.manage2sail.com/en-US/event/a2195470-e42f-4270-bbf7-311397ab5957',
    kwindooDefault:'' /* user pastes when YCI publishes */ },
  { id:'blauband-26',     date:'2026-06-27', name:'Blauband-Regatta',
    host:'Yacht Club Zug', hostUrl:'',
    m2sUrl:'',  kwindooDefault:'' },
  { id:'rigi-anker-26',   date:'2026-08-29', name:'Rigi Anker Cup',
    host:'OSCA Obersee Club Arth', hostUrl:'http://www.osca.ch/',
    m2sUrl:'',  kwindooDefault:'' },
  { id:'chomerbar-26',    date:'2026-09-12', name:'Chomer Bär',
    host:'SCC Segel Club Cham',    hostUrl:'',
    m2sUrl:'',  kwindooDefault:'' }
];
```

The **active event** is the nearest future event (or, in the 24 h window after a race, the most recent one). Joao can override via a pill row at the top of the tab if needed.

## 5. UX — Rivals tab (Zugersee mode)

### 5.1 Event header card

```
[ Zugersee Cup 2026 ]
Active: Goldschäkel-Regatta · 30 May 2026 · YCI Immensee
↓ Countdown: 4d 18h
[ ► Manage2Sail ↗ ]  [ ► YCI ↗ ]  [ ► NOR (PDF) ↗ ]
```

A small pill row underneath lets the user switch the active event (Goldschäkel / Blauband / Rigi Anker / Chomer Bär).

### 5.2 Kwindoo tracker card

```
[ Kwindoo — Live tracker ]
[ paste URL ▾ ]   (small input + Save)
   ┌────────────────────────────────┐
   │                                │
   │     Kwindoo iframe (16:9)      │
   │                                │
   └────────────────────────────────┘
[ Open in new tab ↗ ]
```

If no URL configured for the active event: the iframe area shows a placeholder ("YCI publishes the Kwindoo URL in the NOR or via email — paste it above when you have it") with a friendly link to Kwindoo's events search. Saved URLs are remembered across reloads.

**Iframe robustness:** Kwindoo may set CSP headers that prevent embedding on some setups. If iframe-load fails (detected via `onerror` or timeout), fall back to a big "Open Kwindoo in new tab ↗" button — no race-day surprise.

### 5.3 Yardstick class panel

```
[ Yardstick — Little Johnka YS 94 ]
Class window: 90–98 (boats you're directly racing on corrected time)

| Yardstick | Boat                        |
|-----------|-----------------------------|
| 92        | J/70                        |
| 92        | T780                        |
| 94        | CYD 27 (Little Johnka)      | ← you
| 96        | Esse 850                    |
| 98        | Surprise                    |
| 100       | First 25.7 / Ufo 22         |

[ + Add boat ]    [ Swiss Sailing Yardstick Liste 2025 ↗ ]
```

The class window (default ±4 YS points) is editable. The list is editable — Joao can add boats he sees in the fleet with their Yardstick. Persisted in `localStorage` (`zsc_yardstick_v1`).

The seeded boats come from typical Zugersee Cup fleets (J/70, Surprise, T780, Ufo 22 etc. per the 2025 Goldschäkel write-up).

### 5.4 Bol d'Or tab — untouched

On Bol d'Or venue, the existing Rivals tab (SuiviRegate KMZ + 5 targets + per-rival analysis) renders as before. The Zugersee implementation is gated entirely on `IS_ZUG`.

## 6. Data model

```js
// localStorage keys (Primary device)
'zsc_events_v1'    = {
  active: 'goldschaekel-26',
  events: {
    'goldschaekel-26': { kwindooUrl: 'https://kwindoo.com/tracking/<id>', note: '' },
    'blauband-26':     { kwindooUrl: '',                                  note: '' },
    'rigi-anker-26':   { kwindooUrl: '',                                  note: '' },
    'chomerbar-26':    { kwindooUrl: '',                                  note: '' }
  }
}
'zsc_yardstick_v1' = [
  { ys: 92,  name: 'J/70',                self: false },
  { ys: 92,  name: 'T780',                self: false },
  { ys: 94,  name: 'CYD 27',              self: true  }, // Little Johnka
  ...
]
```

## 7. Implementation

- New helper `renderRivalsZG()` invoked by `showTab(4)` when `IS_ZUG`. The existing renderer stays as the boldor path.
- Kwindoo iframe lives in a card with `sandbox="allow-scripts allow-same-origin allow-popups allow-forms"` — the minimum for Kwindoo to render and accept clicks without giving it cross-origin reach into the PWA.
- A small `iframeLoadGuard(iframe, ms, onFail)` helper detects load failures and shows the fallback button.
- All input is **Primary-device only** (per the existing Advisor pattern). Advisor devices see the same UI read-only; "Save URL" and "Add boat" are hidden.

## 8. Service worker

Allow `kwindoo.com/tracking/*` through to the network (no caching — it's interactive). No SW changes required, since the SW only intercepts specific data hosts (`open-meteo.com`, `data.geo.admin.ch`) and tile hosts; everything else passes through.

## 9. Acceptance criteria

1. Open the Rivals tab on Zugersee venue with no Kwindoo URLs configured → placeholder + paste UI works; no console errors.
2. Paste a Kwindoo URL for Goldschäkel → it persists across reloads and renders the iframe.
3. Switch active event to Blauband (via pill) → Kwindoo card shows the placeholder again (different event, no URL yet). Yardstick panel unchanged.
4. Switch venue to Bol d'Or → existing Rivals UI renders exactly as today.
5. Advisor mode on Zugersee Rivals → Yardstick + Kwindoo cards render but "Save URL" / "+ Add boat" are hidden.

## 10. Open questions

1. **Iframe vs new-tab default.** Some Kwindoo views work well in iframe; some force a redirect. Spec assumes iframe first, new-tab on failure. Acceptable?
2. **Yardstick class window.** Default ±4 points (90–98 around CYD27 at 94). Wider window catches more boats but dilutes "direct competitors". Adjustable?
3. **Should Bol d'Or also get a Yardstick panel?** The Bol d'Or is ORC-handicap on Lac Léman, not Yardstick. So no — keep Yardstick Zugersee-only.
4. **OSCA-specific UI for Rigi Anker Cup?** That's your home regatta. Spec is generic; happy to add OSCA branding / specific banks / start area if useful.

## 11. References

- [Zugersee Cup site](https://www.zugerseecup.ch/edition-2026)
- [Goldschäkel 2026 — manage2sail](https://www.manage2sail.com/en-US/event/a2195470-e42f-4270-bbf7-311397ab5957)
- [Swiss Sailing Yardstick Reglement (PDF)](https://www.swiss-sailing.ch/_Resources/Persistent/b689aed3bd89d348e4c25fa5cab093539eeb112c/Reglement%20Yardstick_DE_2021.pdf)
- [Swiss Sailing Yardstick Liste 2025 (PDF)](https://www.swiss-sailing.ch/_Resources/Persistent/6/a/f/4/6af402cab361af6b83c43a5ddbdea32b8eb2b9d8/Yardstickzahlen%202025.pdf)
- [Kwindoo events list](https://kwindoo.com/events/list)
- [YCI Goldschäkel 2025 write-up (ClubDesk)](https://yachtclubimmensee.clubdesk.com/sport)
