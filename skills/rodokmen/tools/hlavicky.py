#!/usr/bin/env python3
"""Přehled hlaviček snímků: horní pruh z několika snímků svazku slepený pod sebe s číslem snímku (#12).

Z hlaviček (rok, měsíc, obec, oddíl) je hned vidět, kde ve svazku je hledaný rok nebo obec – místo prohlížení
celých stránek po jedné. Hodí se k půlení svazku bez rejstříku a ke knihám řazeným po obcích.

Použití (z kořene projektu):
  hlavicky.py <portál> <svazek> <snímky> <výstup.jpg> [--oblast x0,y0,x1,y1] [--vedle] [--po N] [--vylepsit]
    portál   aron        svazek = apu_id (aron_img.py), stahují se jen dlaždice pruhu v polovičním rozlišení
             mza         svazek = id knihy (mza.py), dlaždice pruhu ve čtvrtinovém rozlišení
             ebadatelna  svazek = matrikaId (ebadatelna.py; „a:<archivalieId>“ = archiválie), celý snímek jedním
                         požadavkem do cache, pruh se vyřízne z něj
             trebon      svazek = id knihy (trebon.py), náhled snímku do cache, pruh se vyřízne z něj
             soubory     svazek = vzor cesty k už staženým snímkům s {n}, např. "pracovni/kniha_{n}.jpg"
                         (jakýkoli portál; nic se nestahuje)
    snímky   10,20,30 | 10-90:10 (od-do po krocích) | kombinace „1-5,40,80-120:20“; nejvýš 40 najednou
    --oblast co vyříznout, zlomky 0..1 celé stránky; výchozí 0,0,1,0.15 = horních 15 % (hlavička); u snímku s okrajem kolem knihy posuň (0,0.08,1,0.25)
             např. 0,0,0.25,1 = levý sloupec (čísla domů, jména) – s --vedle se pak pruhy kladou vedle sebe
    --vedle  pruhy vedle sebe (úzké svislé sloupce) místo pod sebe
    --po N   kolik pruhů do jednoho obrázku (výchozí 10); víc snímků -> výstup_1.jpg, výstup_2.jpg …
    --vylepsit  vybledlé snímky: šedá, místní kontrast, doostření
Stažené snímky jdou do sdílené cache (tools/cache.py) – co už jednou bylo staženo, se znovu nestahuje.
Všechno jde přes brzdu (tools/slusne.py). Stahuj šetrně: nejdřív 5–10 snímků po velkých krocích, pak zúžit.
"""
import os, re, shutil, subprocess, sys, tempfile
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__))); import slusne  # noqa: E402,F401 – brzda proti zablokování archivem (i pro podprocesy nástrojů, tools/slusne.py)
import cache  # noqa: E402 – sdílená cache stažených snímků (tools/cache.py)
from obraz import magick, vylepsit, vyrez  # noqa: E402 – ImageMagick a výřez z obrázku na disku (tools/obraz.py)
for _s in (sys.stdout, sys.stderr):   # UTF-8 výstup i na Windows bez -X utf8 (cp1250 neumí třeba „→“)
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

TOOLS = os.path.dirname(os.path.abspath(__file__))
PORTALY = ("aron", "mza", "ebadatelna", "trebon", "soubory")
NEJVIC = 40
SIRKA = 1600   # šířka pruhu pod sebou (výška u --vedle) v px – hlavička je pak čitelná a obrázek ne moc velký


def snimky(spec):
    """„1-5,40,80-120:20“ -> [1, 2, 3, 4, 5, 40, 80, 100, 120] (bez opakování, v zadaném pořadí)."""
    out = []
    for cast in spec.split(","):
        m = re.fullmatch(r"\s*(\d+)\s*(?:-\s*(\d+)\s*(?::\s*(\d+)\s*)?)?", cast)
        if not m:
            sys.exit(f"Snímky „{spec}“: čekám čísla, rozsahy od-do nebo od-do:krok, oddělené čárkou (např. 10-90:10).")
        a, b, krok = int(m.group(1)), int(m.group(2) or m.group(1)), int(m.group(3) or 1)
        if a < 1 or b < a or krok < 1:
            sys.exit(f"Snímky „{cast.strip()}“: od ≥ 1, do ≥ od, krok ≥ 1.")
        out += range(a, b + 1, krok)
    out = list(dict.fromkeys(out))
    if len(out) > NEJVIC:
        sys.exit(f"{len(out)} snímků je moc najednou (nejvýš {NEJVIC}) – vezmi větší krok a pak zužuj (šetrně k archivu).")
    return out


def oblast(s):
    try:
        b = [float(v) for v in s.split(",")]
    except ValueError:
        b = []
    if len(b) != 4 or not (0 <= b[0] < b[2] <= 1 and 0 <= b[1] < b[3] <= 1):
        sys.exit(f"Oblast „{s}“ má být x0,y0,x1,y1 jako zlomky 0..1 (x0 < x1, y0 < y1), např. 0,0,1,0.1.")
    return b


def nastroj(*args):
    """Spustí nástroj z tools/ (má vlastní brzdu a cache); při chybě vrátí text chyby, jinak None."""
    r = subprocess.run([sys.executable, "-I", "-X", "utf8", os.path.join(TOOLS, args[0]), *map(str, args[1:])],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode == slusne.KOD:   # archiv je zastavený brzdou – dál nic nestahovat
        sys.stderr.write(r.stderr)
        raise slusne.Zastaveno(slusne.KOD)
    return (r.stderr.strip() or r.stdout.strip() or f"kód {r.returncode}")[-400:] if r.returncode else None


def pruh(portal, svazek, n, box, cil, tmp):
    """Vyřízne oblast box ze snímku n do souboru cil. Vrátí None, nebo text chyby."""
    box_s = ",".join(f"{v:g}" for v in box)
    if portal == "soubory":
        src = svazek.replace("{n}", str(n))
        if not os.path.exists(src):
            return f"soubor {src} neexistuje"
        vyrez(src, box, cil)
        return None
    if portal == "aron":
        v_cache = next((cache.cesta(f"aron/{svazek}/sn{n:04d}-u{u}.jpg") for u in (0, 1, 2)
                        if os.path.exists(cache.cesta(f"aron/{svazek}/sn{n:04d}-u{u}.jpg"))), None)
        if v_cache:   # celý snímek už je stažený – vyříznout z něj, nic nestahovat
            vyrez(v_cache, box, cil)
            return None
        return nastroj("aron_img.py", svazek, n, 1, cil, box_s)
    if portal == "mza":
        return nastroj("mza.py", "snimek", svazek, n, cil, "nahled", box_s)
    if portal == "ebadatelna":
        druh, xid = ("a-snimek", svazek[2:]) if svazek.startswith("a:") else ("snimek", svazek)
        return nastroj("ebadatelna.py", druh, xid, n, cil, box_s)
    if portal == "trebon":
        cely = os.path.join(tmp, f"cely_{n}.jpg")
        chyba = nastroj("trebon.py", "snimek", svazek, n, cely, "nahled")
        if chyba:
            return chyba
        vyrez(cely, box, cil)
        return None
    sys.exit(f"Neznámý portál „{portal}“ – možnosti: {', '.join(PORTALY)}.")


def slep(pruhy, out, vedle, extra):
    """Pruhy [(n, soubor)] -> jeden obrázek, každý s popiskem „sn. N“. Bez písma (macOS bez fontu) i bez popisků."""
    m = magick()
    zmena = ["-resize", f"x{SIRKA}>"] if vedle else ["-resize", f"{SIRKA}x>"]
    for popisky in (True, False):
        args = [m, "-background", "white"]
        for n, f in pruhy:
            args += ["(", f, *extra, *zmena]
            if popisky:
                args += ["-gravity", "NorthWest", "-splice", "0x44", "-fill", "#c00000", "-pointsize", "34",
                         "-annotate", "+8+4", f"sn. {n}"]
            args += ["-bordercolor", "#888888", "-border", "0x2" if not vedle else "2x0", ")"]
        r = subprocess.run(args + ["+append" if vedle else "-append", "-quality", "85", out], capture_output=True, text=True)
        if r.returncode == 0:
            if not popisky:
                print("(bez popisků – ImageMagick nenašel písmo; pořadí pruhů:", ", ".join(str(n) for n, _ in pruhy) + ")")
            return
    sys.exit(f"Slepení pruhů selhalo: {r.stderr.strip()[:300]}")


def main(argv):
    volby = {"--oblast": "0,0,1,0.15", "--po": "10"}
    prepinace = {"--vedle", "--vylepsit"}
    args, i = [], 0
    while i < len(argv):
        if argv[i] in volby:
            if i + 1 >= len(argv):
                sys.exit(f"{argv[i]} chce hodnotu.")
            volby[argv[i]] = argv[i + 1]
            i += 2
        else:
            args.append(argv[i])
            i += 1
    zapnute = {a for a in args if a in prepinace}
    args = [a for a in args if a not in prepinace]
    if len(args) != 4:
        sys.exit(__doc__)
    portal, svazek, spec, out = args
    if portal not in PORTALY:
        sys.exit(f"Neznámý portál „{portal}“ – možnosti: {', '.join(PORTALY)}.")
    if portal != "soubory" and not re.fullmatch(r"(a:)?[\w-]{1,64}", svazek):
        sys.exit(f"Svazek „{svazek}“ – čekám id svazku z nástroje portálu (číslo nebo apu_id).")
    if portal == "soubory" and "{n}" not in svazek:
        sys.exit("U „soubory“ dej vzor cesty se {n}, např. \"pracovni/kniha_{n}.jpg\".")
    if not volby["--po"].isdigit() or int(volby["--po"]) < 1:
        sys.exit("--po chce kladné číslo.")
    box, cisla, po = oblast(volby["--oblast"]), snimky(spec), int(volby["--po"])
    extra = vylepsit(magick()) if "--vylepsit" in zapnute else []
    tmp = tempfile.mkdtemp(prefix="hlavicky_")
    try:
        hotove, chyby = [], []
        for n in cisla:
            cil = os.path.join(tmp, f"pruh_{n:05d}.jpg")
            chyba = pruh(portal, svazek, n, box, cil, tmp)
            if chyba or not os.path.exists(cil):
                chyby.append(f"snímek {n}: {chyba or 'výřez nevznikl'}")
                print("nepovedlo se –", chyby[-1].splitlines()[-1], file=sys.stderr)
                continue
            hotove.append((n, cil))
            print(f"snímek {n} ✓", file=sys.stderr)
        if not hotove:
            sys.exit("Žádný snímek se nepodařilo získat:\n" + "\n".join(chyby))
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
        davky = [hotove[i:i + po] for i in range(0, len(hotove), po)]
        koren, pripona = os.path.splitext(out)
        for k, davka in enumerate(davky, 1):
            cil = out if len(davky) == 1 else f"{koren}_{k}{pripona or '.jpg'}"
            slep(davka, cil, "--vedle" in zapnute, extra)
            print(cil, "– snímky", ", ".join(str(n) for n, _ in davka))
        if chyby:
            print(f"Chybí {len(chyby)} snímků (za koncem knihy? výpadek?): " + "; ".join(c.splitlines()[0][:80] for c in chyby))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main(sys.argv[1:])
