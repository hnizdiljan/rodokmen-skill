#!/usr/bin/env python3
"""Ověření čtení (např. po pomocníkovi): výřez zápisu rozdělený na dvě poloviny, každá nejvýš 1900 × 1900 px.

Použití: overit.py <snímek.jpg> x0,y0,x1,y1 <prefix> [v] [--vylepsit]
  x0..y1      oblast zápisu jako zlomky šířky a výšky celého snímku (0..1)
  v           dělit vodorovně (horní a dolní polovina); jinak se dělí svisle (levá a pravá)
  --vylepsit  vybledlý snímek: šedá, místní kontrast, doostření (jen pro čtení)
Poloviny se o 8 % oblasti překrývají, aby řádek na hranici nebyl useknutý. Uloží <prefix>_0.jpg a <prefix>_1.jpg.
"""
import os, subprocess, sys
for _s in (sys.stdout, sys.stderr):   # UTF-8 výstup i na Windows bez -X utf8 (cp1250 neumí třeba „→“)
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # -I nepřidává složku skriptu
from obraz import magick, vylepsit   # společný hledač ImageMagicku (tools/obraz.py)

PREKRYV = 0.08   # podíl oblasti, o který se poloviny překrývají


def poloviny(box, mode):
    """Dvě části oblasti (zlomky celé stránky), překryté o PREKRYV šířky (výšky) oblasti."""
    x0, y0, x1, y1 = box
    if mode == "v":
        ym, o = (y0 + y1) / 2, (y1 - y0) * PREKRYV / 2
        return [(x0, y0, x1, min(y1, ym + o)), (x0, max(y0, ym - o), x1, y1)]
    xm, o = (x0 + x1) / 2, (x1 - x0) * PREKRYV / 2
    return [(x0, y0, min(x1, xm + o), y1), (max(x0, xm - o), y0, x1, y1)]


def main():
    args = [a for a in sys.argv[1:] if a != "--vylepsit"]
    if len(args) < 3:
        sys.exit(__doc__)
    f, box, pre = args[:3]
    mode = args[3] if len(args) > 3 else "h"
    try:
        x0, y0, x1, y1 = map(float, box.split(","))
    except ValueError:
        sys.exit(f"Oblast {box} má být x0,y0,x1,y1 (zlomky 0..1).")
    if not (0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1):
        sys.exit(f"Oblast {box} musí být zlomky 0..1 (x0 < x1, y0 < y1), ne pixely.")
    MAGICK = magick()
    r = subprocess.run([MAGICK, f + "[0]", "-format", "%w %h", "info:"], capture_output=True, text=True)
    if r.returncode or len(r.stdout.split()) < 2:
        sys.exit(f"ImageMagick snímek {f} nepřečetl: {r.stderr.strip()[:300]}")
    W, H = map(int, r.stdout.split()[:2])
    extra = vylepsit(MAGICK) if "--vylepsit" in sys.argv[1:] else []
    for i, (a, b, c, d) in enumerate(poloviny((x0, y0, x1, y1), mode)):
        o = f"{pre}_{i}.jpg"
        if os.path.exists(o):
            os.remove(o)   # starý soubor by se jinak tvářil jako nový výsledek
        crop = "%dx%d+%d+%d" % (max(1, round((c - a) * W)), max(1, round((d - b) * H)), round(a * W), round(b * H))
        # 1900x1900> jen zmenší: dlouhý úzký výřez se nenafoukne (600×2400 by s 1900x vyšel 1900×7600)
        r = subprocess.run([MAGICK, f, "-crop", crop, "+repage", *extra, "-resize", "1900x1900>", o],
                           capture_output=True, text=True)
        if r.returncode or not os.path.exists(o):
            sys.exit(f"Výřez {o} se nepovedl: {r.stderr.strip()[:300]}")
        print(o)


if __name__ == "__main__":
    main()
