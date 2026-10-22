#!/usr/bin/env python3
"""Genera data/track.js con el recorrido del velero Cabo de Hornos a partir del GPX del inReach.

Uso: python scripts/build_track.py "<ruta al explore.gpx>"

Depura saltos imposibles del GPS, deja fuera los paseos por tierra en Puerto Argentino
y calcula las distancias en millas náuticas. Los textos de los mensajes no se publican.
"""
import json
import math
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = timedelta(hours=-3)
MAX_KN = 14  # un velero de crucero no supera esta velocidad sostenida

# Fases de la travesía (hora argentina)
PHASES = [
    ("ida", "Rumbo al sur", datetime(2024, 1, 1), datetime(2024, 1, 19, 15, 0)),
    ("malvinas", "Malvinas", datetime(2024, 1, 19, 15, 0), datetime(2024, 1, 31, 16, 0)),
    ("regreso", "Regreso", datetime(2024, 1, 31, 16, 0), datetime(2024, 3, 1)),
]

# Paseos por tierra con el inReach encima (no son navegación)
LAND = [((-51.6919, -57.8545), datetime(2024, 1, 23, 12, 0), datetime(2024, 1, 26, 4, 0), 1.5)]

MARKERS = [
    ("Zarpada del Centro Naval Núñez", -34.5365, -58.4526, "2024-01-03"),
    ("Mar del Plata", -38.0398, -57.5247, "2024-01-05"),
    ("Base Naval Puerto Belgrano", -38.9038, -62.0991, "2024-01-08"),
    ("Bahía Cracker, golfo Nuevo", -42.9457, -64.4909, "2024-01-13"),
    ("Camarones", -44.8022, -65.7100, "2024-01-16"),
    ("Islas Jason a la vista", -50.6423, -61.2085, "2024-01-22"),
    ("Homenaje al ARA «Alférez Sobral»", -51.0664, -59.8061, "2024-01-22"),
    ("Puerto Argentino", -51.6919, -57.8545, "2024-01-23"),
    ("Garden Point", -52.1472, -59.3673, "2024-01-26"),
    ("Puerto San Julián", -49.3093, -67.7105, "2024-01-31"),
    ("Caleta Hornos", -45.0372, -65.6833, "2024-02-10"),
    ("Puerto Pirámides", -42.5881, -64.2936, "2024-02-14"),
    ("Base Naval Puerto Belgrano", -38.9609, -62.0306, "2024-02-19"),
    ("Arribo a Núñez", -34.5328, -58.4378, "2024-02-24"),
]

MESES = ["ene", "feb", "mar"]


def nm(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * 3440.065 * math.asin(math.sqrt(h))


def load(path):
    text = Path(path).read_text(encoding="utf-8")
    pts = []
    for lat, lon, tm in re.findall(r'<trkpt lat="([-\d.]+)" lon="([-\d.]+)">.*?<time>([^<]+)', text, re.S):
        t = datetime.strptime(tm[:19], "%Y-%m-%dT%H:%M:%S") + ART
        pts.append((float(lat), float(lon), t))
    pts.sort(key=lambda p: p[2])
    return pts


def clean(pts):
    """Quita paseos por tierra y posiciones que implican velocidades imposibles."""
    out = []
    for p in pts:
        if any(a <= p[2] <= b and nm(c, p) > r for c, a, b, r in LAND):
            continue
        out.append(p)
    changed = True
    while changed:
        changed = False
        keep = [out[0]]
        for i in range(1, len(out)):
            prev, cur = keep[-1], out[i]
            hours = max((cur[2] - prev[2]).total_seconds() / 3600, 1 / 60)
            if nm(prev, cur) / hours > MAX_KN and nm(prev, cur) > 1:
                changed = True
                continue
            keep.append(cur)
        out = keep
    return out


def distance(pts):
    """Distancia navegada: ignora el bailoteo del GPS fondeado o amarrado."""
    total, last = 0.0, pts[0]
    for p in pts[1:]:
        d = nm(last, p)
        if d > 0.15:
            total += d
            last = p
    return total


def simplify(pts, tol_nm=0.05):
    """Douglas-Peucker aproximado en millas, para aligerar el mapa."""
    if len(pts) < 3:
        return pts
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        best, idx = 0.0, None
        for i in range(a + 1, b):
            dab = nm(pts[a], pts[b]) or 1e-9
            # área del triángulo por Herón aproximada con distancias
            x, y = nm(pts[a], pts[i]), nm(pts[i], pts[b])
            s = (x + y + dab) / 2
            area = math.sqrt(max(s * (s - x) * (s - y) * (s - dab), 0))
            h = 2 * area / dab
            if h > best:
                best, idx = h, i
        if idx is not None and best > tol_nm:
            keep[idx] = True
            stack += [(a, idx), (idx, b)]
    return [p for p, k in zip(pts, keep) if k]


def port_name(p):
    """Nombre del puerto o fondeadero más cercano a una posición."""
    m = min(MARKERS, key=lambda m: nm((m[1], m[2]), p))
    return "Centro Naval Núñez" if "Núñez" in m[0] else m[0]


def legs(pts, hours=5, radius=1.0):
    """Tramos entre puertos: una escala es quedarse 5 h a menos de 1 MN, o un hueco de 5 h sin posiciones."""
    stops, i = [], 0
    while i < len(pts):
        j = i
        while j + 1 < len(pts) and nm(pts[i], pts[j + 1]) < radius:
            j += 1
        if (pts[j][2] - pts[i][2]).total_seconds() >= hours * 3600:
            stops.append((i, j))
            i = j + 1
        elif i + 1 < len(pts) and (pts[i + 1][2] - pts[i][2]).total_seconds() >= hours * 3600:
            stops.append((i, i + 1))
            i += 1
        else:
            i += 1
    out = []
    for (_, a), (b, _) in zip(stops, stops[1:]):
        seg = pts[a:b + 1]
        d = distance(seg)
        if d < 3:  # cambios de amarra dentro del mismo puerto
            continue
        h = (seg[-1][2] - seg[0][2]).total_seconds() / 3600
        out.append({"from": port_name(seg[0]), "to": port_name(seg[-1]), "start": seg[0][2].isoformat(),
                    "end": seg[-1][2].isoformat(), "nm": round(d, 1), "hours": round(h, 1)})
    return out


def best_day(pts):
    """Mayor distancia navegada en 24 horas corridas."""
    best, when, e = 0.0, None, 0
    for k in range(len(pts)):
        e = max(e, k)
        while e + 1 < len(pts) and (pts[e + 1][2] - pts[k][2]).total_seconds() <= 86400:
            e += 1
        d = distance(pts[k:e + 1])
        if d > best:
            best, when = d, pts[k][2]
    return {"nm": round(best, 1), "start": when.isoformat()}


def phase_of(t):
    return next(key for key, _, a, b in PHASES if a <= t < b)


def label(d):
    return f"{d.day} {MESES[d.month - 1]}"


def main():
    raw = load(sys.argv[1])
    pts = clean(raw)
    by_phase = {key: [p for p in pts if phase_of(p[2]) == key] for key, *_ in PHASES}
    phase_nm = {key: distance(v) for key, v in by_phase.items() if v}
    days = []
    day = pts[0][2].date()
    while day <= pts[-1][2].date():
        chunk = [p for p in pts if p[2].date() == day]
        # une el día con la última posición del anterior para que no queden huecos
        prev = [p for p in pts if p[2].date() < day][-1:] if days else []
        line = simplify(prev + chunk)
        phase = phase_of(datetime.combine(day, datetime.min.time()) + timedelta(hours=12))
        days.append({
            "date": day.isoformat(),
            "label": label(day),
            "phase": phase,
            "count": len(chunk),
            "nm": round(distance(prev + chunk), 1) if chunk else 0,
            "points": [[round(p[0], 5), round(p[1], 5)] for p in line],
        })
        day += timedelta(days=1)
    data = {
        "source": "Garmin inReach del velero Cabo de Hornos (exportación Explore)",
        "summary": {
            "rawPoints": len(raw),
            "cleanedPoints": len(pts),
            "start": pts[0][2].isoformat(),
            "end": pts[-1][2].isoformat(),
            "days": len(days),
            "totalNm": round(sum(phase_nm.values()), 1),
            "phases": [{"key": k, "name": n, "nm": round(phase_nm.get(k, 0), 1)} for k, n, *_ in PHASES],
            "southmost": min(p[0] for p in pts),
            "legs": legs(pts),
            "bestDay": best_day(pts),
        },
        "markers": [{"name": n, "lat": la, "lon": lo, "date": d} for n, la, lo, d in MARKERS],
        "days": days,
    }
    out = ROOT / "data" / "track.js"
    out.parent.mkdir(exist_ok=True)
    out.write_text("window.TRACK = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    s = data["summary"]
    print(f"{s['rawPoints']} puntos -> {s['cleanedPoints']} depurados · {s['days']} días · {s['totalNm']} MN")
    for ph in s["phases"]:
        print(f"  {ph['name']}: {ph['nm']} MN")
    print(f"  {out} ({out.stat().st_size // 1024} KB, {sum(len(d['points']) for d in days)} vértices)")


if __name__ == "__main__":
    main()
