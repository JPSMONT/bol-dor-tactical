"""
Cross-race PPR analysis for Little Johnka — all 8 GPX tracks.
Methodology:
  1. Multi-race-window detection (handle multi-race days)
  2. Multi-model wind ensemble (AROME HD + ICON-D2 + ICON-CH1 where available)
  3. PPR per race window, broken down by point of sail
  4. Aggregate across races, flag wind-model agreement quality
"""
import xml.etree.ElementTree as ET
import urllib.request, urllib.error, json, math, os, glob
from datetime import datetime, timezone

# ============ ORC POLAR (BestPerf envelope) ============
P = {
  6:{'twa':[42,52,60,70,75,80,90,110,120,135,150,165,180],'btv':[4.74,5.32,5.60,5.78,5.81,5.82,5.77,5.65,5.48,4.92,4.09,3.43,3.22]},
  8:{'twa':[40.5,52,60,70,75,80,90,110,120,135,150,165,180],'btv':[5.36,6.03,6.26,6.40,6.43,6.45,6.44,6.50,6.41,6.01,5.19,4.46,4.22]},
  10:{'twa':[39.8,52,60,70,75,80,90,110,120,135,150,165,180],'btv':[5.54,6.21,6.42,6.60,6.67,6.73,6.79,6.89,6.89,6.60,6.09,5.38,5.13]},
  12:{'twa':[40.1,52,60,70,75,80,90,110,120,135,150,165,180],'btv':[5.63,6.28,6.49,6.69,6.78,6.87,7.05,7.14,7.36,7.06,6.62,6.17,5.95]},
  14:{'twa':[40.1,52,60,70,75,80,90,110,120,135,150,165,180],'btv':[5.74,6.34,6.53,6.74,6.84,6.95,7.21,7.51,7.68,7.60,7.06,6.65,6.51]},
  16:{'twa':[40.5,52,60,70,75,80,90,110,120,135,150,165,180],'btv':[5.78,6.40,6.61,6.80,6.88,6.99,7.31,7.84,7.97,8.25,7.57,7.07,6.92]},
  20:{'twa':[42.4,52,60,70,75,80,90,110,120,135,150,165,180],'btv':[5.75,6.35,6.60,6.88,7.01,7.16,7.40,8.23,8.65,9.40,8.86,8.10,7.88]}
}
TWS_KEYS = [6,8,10,12,14,16,20]

def interp_polar(tws, twa):
    if tws < 2: return None
    twa = abs(twa);  twa = 360-twa if twa > 180 else twa
    def ai(d):
        a, b = d['twa'], d['btv']
        if twa <= a[0]: return b[0]
        if twa >= a[-1]: return b[-1]
        for i in range(len(a)-1):
            if a[i] <= twa <= a[i+1]:
                f = (twa - a[i])/(a[i+1] - a[i]); return b[i] + f*(b[i+1]-b[i])
        return None
    if tws <= TWS_KEYS[0]: return ai(P[TWS_KEYS[0]]) * (tws / TWS_KEYS[0])
    if tws >= TWS_KEYS[-1]: return ai(P[TWS_KEYS[-1]])
    for i in range(len(TWS_KEYS)-1):
        if TWS_KEYS[i] <= tws <= TWS_KEYS[i+1]:
            lo, hi = TWS_KEYS[i], TWS_KEYS[i+1]
            f = (tws - lo)/(hi - lo)
            return ai(P[lo]) + f*(ai(P[hi]) - ai(P[lo]))
    return None

# ============ GEO ============
def hav_nm(la1,lo1,la2,lo2):
    R=3440.065
    p1,p2 = math.radians(la1),math.radians(la2)
    dp,dl = math.radians(la2-la1),math.radians(lo2-lo1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(a))

def brg(la1,lo1,la2,lo2):
    p1,p2 = math.radians(la1),math.radians(la2)
    dl = math.radians(lo2-lo1)
    y = math.sin(dl)*math.cos(p2)
    x = math.cos(p1)*math.sin(p2) - math.sin(p1)*math.cos(p2)*math.cos(dl)
    return (math.degrees(math.atan2(y,x)) + 360) % 360

# ============ GPX ============
def parse_gpx(path):
    tree = ET.parse(path); root = tree.getroot()
    ns = root.tag.split('}')[0].strip('{') if '}' in root.tag else ''
    nsd = {'g':ns} if ns else {}
    pts = root.findall('.//g:trkpt', nsd) if ns else root.findall('.//trkpt')
    out=[]
    for p in pts:
        t = p.find('g:time', nsd) if ns else p.find('time')
        if t is None or not t.text: continue
        out.append((datetime.fromisoformat(t.text.strip().replace('Z','+00:00')),
                    float(p.get('lat')), float(p.get('lon'))))
    return out

def build_segs(pts):
    s=[]
    for i in range(len(pts)-1):
        t0,la0,lo0 = pts[i]; t1,la1,lo1 = pts[i+1]
        dt = (t1-t0).total_seconds()
        if not (0 < dt <= 60): continue
        d = hav_nm(la0,lo0,la1,lo1)
        if d < 1e-6: continue
        s.append({'t': t0 + (t1-t0)/2, 'lat':(la0+la1)/2, 'lon':(lo0+lo1)/2,
                  'sog': d/(dt/3600), 'hdg': brg(la0,lo0,la1,lo1), 'dt':dt, 'dist':d})
    return s

def detect_race_windows(segs, min_dur_min=15):
    """Find ALL contiguous racing periods (smoothed SOG > 1.5 kn) lasting > min_dur_min."""
    # Smooth SOG over ~2 min window
    win = max(15, int(120 / (sum(s['dt'] for s in segs[:60])/min(60,len(segs)))))  # ~2 min worth of segments
    n = len(segs)
    smoothed = [False]*n
    for i in range(n):
        a = max(0, i-win); b = min(n, i+win+1)
        racing_frac = sum(1 for j in range(a,b) if 1.5 <= segs[j]['sog'] <= 12) / (b-a)
        smoothed[i] = racing_frac >= 0.6
    # Find runs
    windows = []
    s = None
    for i in range(n):
        if smoothed[i]:
            if s is None: s = i
        else:
            if s is not None:
                dur_s = (segs[i-1]['t'] - segs[s]['t']).total_seconds()
                if dur_s >= min_dur_min*60: windows.append((s, i))
                s = None
    if s is not None:
        dur_s = (segs[-1]['t'] - segs[s]['t']).total_seconds()
        if dur_s >= min_dur_min*60: windows.append((s, n))
    return windows

# ============ WIND ENSEMBLE ============
def try_wind(url):
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            d = json.loads(r.read())
        if 'error' in d: return None
        h = d.get('hourly', {})
        spd_k = next((k for k in h if 'wind_speed' in k), None)
        dir_k = next((k for k in h if 'wind_direction' in k), None)
        if not spd_k: return None
        times = [datetime.fromisoformat(t).replace(tzinfo=timezone.utc) for t in h.get('time',[])]
        sp = h[spd_k]; dr = h[dir_k]
        # filter nulls
        out = [(t,s,dd) for t,s,dd in zip(times,sp,dr) if s is not None and dd is not None]
        return out if out else None
    except Exception:
        return None

def fetch_ensemble(lat, lon, date_str):
    base = f'latitude={lat}&longitude={lon}&start_date={date_str}&end_date={date_str}&hourly=wind_speed_10m,wind_direction_10m&wind_speed_unit=kn&timezone=UTC'
    sources = {
        'arome': f'https://historical-forecast-api.open-meteo.com/v1/forecast?{base}&models=meteofrance_arome_france_hd',
        'icon_d2': f'https://historical-forecast-api.open-meteo.com/v1/forecast?{base}&models=icon_d2',
        'icon_ch1': f'https://historical-forecast-api.open-meteo.com/v1/forecast?{base}&models=meteoswiss_icon_ch1',
        'era5': f'https://archive-api.open-meteo.com/v1/archive?{base}',
    }
    res = {}
    for k, u in sources.items():
        d = try_wind(u)
        if d: res[k] = d
    return res

def ensemble_at(wind_sources, t):
    """Return (mean_tws, mean_twd, spread_kn) at time t across all available models."""
    speeds = []; dirs_sin = []; dirs_cos = []
    for src, hours in wind_sources.items():
        # interp
        if not hours: continue
        if t <= hours[0][0]:
            s,d = hours[0][1], hours[0][2]
        elif t >= hours[-1][0]:
            s,d = hours[-1][1], hours[-1][2]
        else:
            s,d = None,None
            for i in range(len(hours)-1):
                if hours[i][0] <= t <= hours[i+1][0]:
                    f = (t-hours[i][0]).total_seconds() / (hours[i+1][0]-hours[i][0]).total_seconds()
                    s = hours[i][1] + f*(hours[i+1][1]-hours[i][1])
                    # circular dir
                    d0, d1 = hours[i][2], hours[i+1][2]
                    diff = d1-d0
                    if diff>180: diff-=360
                    if diff<-180: diff+=360
                    d = (d0 + f*diff) % 360
                    break
        if s is None: continue
        speeds.append(s)
        dirs_sin.append(math.sin(math.radians(d)))
        dirs_cos.append(math.cos(math.radians(d)))
    if not speeds: return None
    ms = sum(speeds)/len(speeds)
    spread = max(speeds) - min(speeds) if len(speeds)>1 else 0
    md = (math.degrees(math.atan2(sum(dirs_sin)/len(dirs_sin), sum(dirs_cos)/len(dirs_cos))) + 360) % 360
    return ms, md, spread, len(speeds)

# ============ PROCESS ONE RACE WINDOW ============
def analyze_window(segs, wind, label=''):
    valid = []
    for s in segs:
        e = ensemble_at(wind, s['t'])
        if not e: continue
        tws, twd, spread, n_models = e
        twa_s = ((s['hdg'] - twd) + 540) % 360 - 180
        twa = abs(twa_s); twa = 360-twa if twa>180 else twa
        tgt = interp_polar(tws, twa)
        if tgt is None or tgt < 0.5: continue
        ppr = s['sog'] / tgt
        s2 = dict(s); s2.update({'tws':tws,'twd':twd,'twa':twa,'target':tgt,'ppr':ppr,'spread':spread,'n_models':n_models})
        s2['pos'] = 'upwind' if twa<60 else ('reach' if twa<130 else 'downwind')
        s2['band'] = 'light <8' if tws<8 else ('med 8-14' if tws<14 else 'heavy 14+')
        valid.append(s2)
    if not valid: return None
    tot_t = sum(s['dt'] for s in valid)
    weighted_ppr = sum(s['ppr']*s['dt'] for s in valid)/tot_t
    avg_tws = sum(s['tws']*s['dt'] for s in valid)/tot_t
    avg_spread = sum(s['spread']*s['dt'] for s in valid)/tot_t
    # by pos
    by_pos = {}
    for pos in ['upwind','reach','downwind']:
        ss = [s for s in valid if s['pos']==pos]
        if ss:
            wt = sum(s['dt'] for s in ss)
            by_pos[pos] = {'n':len(ss),'time_min':wt/60,'ppr':sum(s['ppr']*s['dt'] for s in ss)/wt,
                           'avg_tws':sum(s['tws']*s['dt'] for s in ss)/wt}
    return {'n':len(valid),'dur_h':tot_t/3600,'dist_nm':sum(s['dist'] for s in valid),
            'avg_sog':sum(s['sog']*s['dt'] for s in valid)/tot_t,
            'ppr':weighted_ppr,'avg_tws':avg_tws,'wind_spread':avg_spread,
            'by_pos':by_pos}

# ============ MAIN ============
RACES = [
    ('kwindoo-tracking-blauband-2024.gpx', 'Blauband 2024-06-22'),
    ('kwindoo-tracking-bisang-cup.gpx',    'Bisang Cup 2024-08-11'),
    ('rigi anker cup.gpx',                 'Rigi Anker Cup 2024-08-31 (hi-res)'),
    ('kwindoo-tracking-blauband.gpx',      'Blauband 2025-06-28'),
    ('kwindoo-tracking-race-day-1.gpx',    'OSCA race 2025-08-11 (Zug N)'),
    ('kwindoo-tracking-race-1.gpx',        'Race 2025-08-16'),
    ('kwindoo-tracking-race-1 (1).gpx',    'Race 2025-08-17'),
    ('race 1.gpx',                          'Race 2025-08-30 (hi-res, 2 races)'),
]

import sys
DL = '/sessions/cool-laughing-turing/mnt/Downloads'
results = []

for fname, label in RACES:
    path = f'{DL}/{fname}'
    print(f"\n{'='*80}\n  {label}\n  {fname}\n{'='*80}", flush=True)
    try:
        pts = parse_gpx(path)
    except FileNotFoundError:
        print('  FILE NOT FOUND'); continue
    if len(pts) < 50:
        print('  too few points'); continue
    
    segs = build_segs(pts)
    windows = detect_race_windows(segs)
    if not windows:
        print('  no race window detected'); continue
    
    date_str = pts[0][0].date().isoformat()
    mid_lat = sum(p[1] for p in pts)/len(pts)
    mid_lon = sum(p[2] for p in pts)/len(pts)
    print(f'  Center: {mid_lat:.4f}°N, {mid_lon:.4f}°E', flush=True)
    print(f'  Race windows detected: {len(windows)}', flush=True)
    
    print(f'  Fetching wind ensemble for {date_str}...', flush=True)
    wind = fetch_ensemble(mid_lat, mid_lon, date_str)
    print(f'    Models with data: {", ".join(wind.keys())}', flush=True)
    if not wind:
        print('    NO WIND DATA — skipping'); continue
    
    for wi, (i0, i1) in enumerate(windows, 1):
        win_segs = segs[i0:i1]
        t0, t1 = win_segs[0]['t'], win_segs[-1]['t']
        dur = (t1-t0).total_seconds()/3600
        a = analyze_window(win_segs, wind, label=f'{label} #{wi}')
        if not a: continue
        print(f"\n  Window {wi}: {t0.strftime('%H:%M')} → {t1.strftime('%H:%M')} UTC ({dur:.2f}h, {a['dist_nm']:.1f} NM, avg SOG {a['avg_sog']:.2f}kn)")
        print(f"    Wind: avg {a['avg_tws']:.1f} kn (model spread ±{a['wind_spread']/2:.1f} kn)")
        print(f"    PPR (overall): {a['ppr']:.3f}")
        for pos in ['upwind','reach','downwind']:
            if pos in a['by_pos']:
                bp = a['by_pos'][pos]
                print(f"      {pos:10s}: PPR {bp['ppr']:.3f}  n={bp['n']:4d}  time={bp['time_min']:5.1f}min  avg TWS={bp['avg_tws']:.1f}kn")
        results.append({'race':label,'win':wi,'date':date_str,**a})

# ===== Cross-race summary =====
print('\n\n' + '='*80 + '\n  CROSS-RACE SUMMARY\n' + '='*80)
print(f"\n{'Race':<40} {'Dur':>5} {'TWS':>5} {'PPR':>6} {'Upw':>6} {'Rch':>6} {'Dnw':>6}")
print('-'*80)
for r in results:
    up = r['by_pos'].get('upwind',{}).get('ppr',float('nan'))
    rc = r['by_pos'].get('reach',{}).get('ppr',float('nan'))
    dn = r['by_pos'].get('downwind',{}).get('ppr',float('nan'))
    print(f"{(r['race']+' #'+str(r['win']))[:39]:<40} {r['dur_h']:>4.1f}h {r['avg_tws']:>4.1f}k {r['ppr']:>6.3f} {up:>6.3f} {rc:>6.3f} {dn:>6.3f}")

if results:
    # Time-weighted aggregate across all races
    tot_t = sum(r['dur_h']*60 for r in results)
    agg_ppr = sum(r['ppr']*r['dur_h']*60 for r in results)/tot_t
    print(f"\nAggregate (time-weighted across all races):")
    print(f"  Overall PPR: {agg_ppr:.3f}")
    for pos in ['upwind','reach','downwind']:
        t_pos = sum(r['by_pos'].get(pos,{}).get('time_min',0) for r in results)
        if t_pos > 0:
            w_pos = sum(r['by_pos'].get(pos,{}).get('ppr',0)*r['by_pos'].get(pos,{}).get('time_min',0) for r in results)/t_pos
            print(f"  {pos:10s}: PPR {w_pos:.3f}  total time {t_pos:.0f} min")

# Save JSON
with open('/sessions/cool-laughing-turing/mnt/outputs/perf-review/results.json','w') as f:
    json.dump([{**r,'by_pos':r['by_pos']} for r in results], f, indent=2, default=str)
print(f"\nSaved: outputs/perf-review/results.json")
