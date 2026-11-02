"""Společné pomocné funkce pro práci s obrázky (hledání ImageMagicku, výřez ze snímku na disku).

Ostatní nástroje ho importují takto (`python3 -I` nepřidává složku skriptu do cesty, proto ji přidáme sami):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from obraz import magick
"""
import glob, os, shutil, subprocess, sys


def najdi_magick():
    """Cesta k ImageMagicku, nebo None. ImageMagick 7 (magick), jinak 6 (convert) – ten ale ne na Windows, kde je convert.exe jiný program."""
    return (shutil.which("magick") or next(iter(sorted(glob.glob(r"C:\Program Files\ImageMagick*\magick.exe"))), None)
            or (os.name != "nt" and shutil.which("convert")) or None)


def magick():
    """Cesta k ImageMagicku; když chybí, skončí hned (před stahováním) srozumitelnou hláškou."""
    m = najdi_magick()
    if not m:
        sys.exit("Chybí ImageMagick (příkaz magick). Nainstaluj ho (macOS: brew install imagemagick, "
                 "Windows: winget install ImageMagick.ImageMagick a restart Claude Code / Codexu / Cursoru / OMP) a spusť nástroj znovu.")
    return m


def vyrez(src, box, out):
    """Výřez x0,y0,x1,y1 (relativní souřadnice 0–1) z obrázku na disku – např. z celého snímku v cache, bez stahování.
    Vrátí rozměr výřezu v pixelech (šířka, výška)."""
    m = magick()
    w, h = (int(v) for v in subprocess.run([m, src, "-format", "%w %h", "info:"], check=True,
                                           capture_output=True, text=True).stdout.split()[:2])
    x0, y0 = int(box[0] * w), int(box[1] * h)
    ww, hh = max(1, int((box[2] - box[0]) * w)), max(1, int((box[3] - box[1]) * h))
    subprocess.run([m, src, "-crop", f"{ww}x{hh}+{x0}+{y0}", "+repage", "-quality", "88", out], check=True)
    return ww, hh
