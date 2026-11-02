#!/usr/bin/env python3
"""Matriky SOA Třeboň (digi.ceskearchivy.cz) bez prohlížeče.

Použití (z kořene projektu):
  trebon.py misto "Obec"                 -> id místa a jeho název (diakritiku a mezery nástroj odstraní sám; portál vybere
                                            jedno místo – VŽDY zkontroluj vypsaný název a okres, u stejnojmenných obcí
                                            a měst vrací i okres nebo synagogu; pak použij id přímo)
  trebon.py svazky <id_mista|"Obec">     -> seznam matrik: id_knihy | kniha | druh | roky | obce
  trebon.py rejstrik <id_knihy> <písmeno> -> jmenný rejstřík (dobrovolnický): příjmení | jméno | místo | rok | snímek
                                            (ne každá kniha ho má; prázdný výsledek = rejstřík chybí, ne „osoba tam není“)
  trebon.py snimek <id_knihy> <snímek> <vystup.jpg> [nahled]
                                         -> stáhne snímek v plném rozlišení (slepí dlaždice); "nahled" = 1/4 rozlišení
  trebon.py svazek <id_knihy>            -> zapíše svazek do data/svazky.json (klíč trebon_<id_knihy>; popis = obce svazku)
  trebon.py strom [<kód> ["Obec"]]       -> strom archiválií (co `svazky` neukáže): 1U urbáře, 1q pozemkové knihy,
                                            1s sčítání lidu, 1k kroniky, 1t vrchnostenská registra (soupisy poddaných);
                                            vypíše podsložky (kód | název) a svazky (id_knihy | popis). Bez kódu kořen.
                                            S "Obec" jen svazky, které obec obsahují (1 dotaz na svazek – pomalé, brzda)
  trebon.py obce <id_knihy>              -> obce, které svazek obsahuje
Snímky svazků ze stromu stahuje `snimek` stejně jako matriky. Za koncem knihy portál vrací pořád poslední snímek –
nástroj na to upozorní, když je snímek stejný jako předchozí (z cache).
Trvalý odkaz na snímek: https://digi.ceskearchivy.cz/<id_knihy>/<snímek>
Ber ohled na server: stahuj jen snímky, které čteš. Stažené snímky jsou ve sdílené cache (tools/cache.py).
"""
import glob, hashlib, html, json, os, re, shutil, subprocess, sys, tempfile, unicodedata, urllib.parse, urllib.request, http.cookiejar
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__))); import slusne  # noqa: E402 – brzda proti zablokování archivem (společný limit dotazů, tools/slusne.py)
import cache  # noqa: E402 – sdílená cache stažených snímků (tools/cache.py)
for _s in (sys.stdout, sys.stderr):   # UTF-8 výstup i na Windows bez -X utf8 (cp1250 neumí třeba „→“)
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

BASE = "https://digi.ceskearchivy.cz"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # -I nepřidává složku skriptu
from obraz import magick   # společný hledač ImageMagicku (tools/obraz.py)
_cj = http.cookiejar.CookieJar()
_op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(_cj))
_op.addheaders = [("User-Agent", "Mozilla/5.0 (rodokmen)")]


def get(path, referer=None, binary=False):
    url = path if path.startswith("http") else BASE + path
    req = urllib.request.Request(url)
    if referer:
        req.add_header("Referer", referer)
    for attempt in range(4):
        try:
            with _op.open(req, timeout=90) as r:
                data = r.read()
                return (data, r.geturl()) if binary else (data.decode("utf-8", "replace"), r.geturl())
        except OSError:
            if attempt == 3:
                raise


def text(s):
    return html.unescape(re.sub(r"<[^>]+>", " ", s)).replace("\xa0", " ").strip()


def misto(nazev):
    # portál zná jen tvar bez diakritiky a mezer (Ratibořské Hory → RatiborskeHory), jinak vrací 404
    holy = "".join(c for c in unicodedata.normalize("NFKD", nazev) if not unicodedata.combining(c)).replace(" ", "")
    _, url = get("/" + urllib.parse.quote(holy))
    m = re.search(r"[?&]id=(\d+)", url) or re.search(r"/(\d+)-", url)
    if not m:
        sys.exit(f"místo „{nazev}“ nenalezeno – portál ho jako místo nezná (malé osady chybějí). Zkus farní nebo sousední obec\n"
                 f"(Malá Chyška → Chyšky) a v popisu jejích knih najdi tuto osadu; id knihy jinak najdi na portálu v prohlížeči.")
    pid = m.group(1)
    page, _ = get(f"/pages/klicova/rejinfo.php?typ=&id={pid}&l=&bookid=")
    t = re.search(r"document\.title=\"([^\"]*)\"", page)
    if not t:
        page, _ = get(f"/description.php?id={pid}&menu=4")
        t = re.search(r"document\.title=\"([^\"]*)\"", page)
    return pid, (t.group(1).strip() if t else "")


def svazky(arg):
    pid = arg if arg.isdigit() else misto(arg)[0]
    page, _ = get(f"/pages/klicova/klicmaterial1.php?typ=2&id={pid}&pomid={pid}&l=&bookid=")
    out = []
    for m in re.finditer(r"<tr[^>]*onclick=\"otevri\('menu=3&id=(\d+)'\)\">(.*?)</tr>", page, re.S):
        bid, row = m.group(1), m.group(2)
        cells = [text(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)]
        cells = [re.sub(r"\s+", " ", c) for c in cells]
        out.append((bid, cells))
    return out


def rejstrik(bid, pis):
    page, _ = get(f"/pages/indexes.php?druh=1&menu2=0&pis={urllib.parse.quote(pis)}&id={bid}&page=")
    rows = []
    for m in re.finditer(r"<tr id='\d+' onclick=\"otevri2\('[^']*page=(\d+)[^']*'\)\">(.*?)</tr>", page, re.S):
        cells = [text(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", m.group(2), re.S)]
        rows.append(cells + [m.group(1)])
    return rows


def _print_rejstrik(rows):
    if not rows:
        print("Rejstřík nic nevrátil; prázdný výsledek není důkaz, že jméno chybí.")
    for row in rows:
        print(" | ".join(row[:2] + row[3:]))


def _compose_tiles(tile_rows, out, tmp, magick_cmd):
    rows = []
    for y, tiles in enumerate(tile_rows):
        row_path = os.path.join(tmp, f"row_{y}.png")
        subprocess.run([magick_cmd, *tiles, "-gravity", "northwest", "+append", row_path], check=True)
        rows.append(row_path)
    subprocess.run([magick_cmd, *rows, "-gravity", "northwest", "-append", out], check=True)


def snimek(bid, n, out, nahled=False):
    MAGICK = magick()
    ref = f"{BASE}/{bid}/{n}"
    klic = f"trebon/{bid}/sn{int(n):04d}{'-nahled' if nahled else ''}.jpg"
    cache.soubor(klic, out, lambda cil: stahni(bid, n, cil, nahled, MAGICK, ref))
    r = subprocess.run([MAGICK, out + "[0]", "-format", "%wx%h", "info:"], capture_output=True, text=True)
    print(out, r.stdout, "odkaz:", ref)
    if za_koncem(bid, int(n), nahled):
        print(f"POZOR: snímek {n} je stejný jako snímek {int(n) - 1} – nejspíš jsi za koncem knihy (portál pak vrací "
              "pořád poslední snímek, zadní desku); poslední skutečný snímek je dřív.")


def za_koncem(bid, n, nahled=False):
    """Snímek n je bajtově stejný jako n-1 v cache (portál za koncem knihy opakuje poslední snímek)."""
    if n < 2:
        return False
    a, b = (cache.cesta(f"trebon/{bid}/sn{k:04d}{'-nahled' if nahled else ''}.jpg") for k in (n - 1, n))
    if not (os.path.exists(a) and os.path.exists(b)):
        return False
    h = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()
    return h(a) == h(b)


def stahni(bid, n, out, nahled, MAGICK, ref):
    get(ref)
    page, _ = get(f"/view.php?menu=3&id={bid}&page={n}&r=0", referer=ref)
    m = re.search(r'showImage\("[^"]*","([^"]+)"', page)
    if not m:
        sys.exit("token obrázku nenalezen (snímek neexistuje?)")
    src = f"{BASE}/cgi-bin/isrv8.cgi?{m.group(1)}"
    # najdi nejvyšší úroveň a počet dlaždic
    def tile(t, x, y):
        d, _ = get(f"{src}.0.{t}-{x}-{y}", referer=ref, binary=True)
        return d
    tier = 1
    while tile(tier + 1, 0, 0):
        tier += 1
    if nahled:
        tier = max(1, tier - 2)
    tmp = tempfile.mkdtemp(prefix="trebon_")
    tile_rows, y = [], 0
    try:
        while True:
            x, row = 0, []
            while True:
                d = tile(tier, x, y)
                if not d:
                    break
                p = os.path.join(tmp, f"t_{y}_{x}.jpg")
                with open(p, "wb") as f:
                    f.write(d)
                row.append(p)
                x += 1
            if not row:
                break
            tile_rows.append(row)
            y += 1
        _compose_tiles(tile_rows, out, tmp, MAGICK)
    finally:
        shutil.rmtree(tmp)


def strom(kod="1", obec=None):
    """Strom archiválií portálu (urbáře 1U, pozemkové knihy 1q, sčítání 1s, kroniky 1k, vrchnostenská registra 1t).
    Vypíše podsložky (kód | název) a svazky (id | popis); s obcí jen svazky, které ji obsahují."""
    if not re.fullmatch(r"\w{1,20}", kod):
        sys.exit(f"Kód stromu je třeba 1q nebo 1U (z výpisu `strom`), ne „{kod}“.")
    page, _ = get(f"/tree.php?doctree={urllib.parse.quote(kod)}&menu=1")
    slozky = re.findall(r"<a[^>]*doctree=(\w+)[^>]*>(.*?)</a>", page, re.S)   # podsložky jako odkazy
    # kořen stromu má složky jako <div onclick='ope("","tree.php?menu=0&doctree=1U")'>…Urbariums</div>
    slozky += re.findall(r"doctree=(\w+)\"\)'>(?:<div[^>]*></div>)?(?:<i[^>]*></i>)?([^<]*)", page)
    vypsane = set()
    for k, nazev in slozky:
        if k.startswith(kod) and k != kod and k not in vypsane and text(nazev):
            vypsane.add(k)
            print(k, "|", re.sub(r"\s+", " ", text(nazev)))
    radky = []
    for bid, row in re.findall(r"id='(\d+)'[^>]*>(.*?)</t(?:r|body)>", page, re.S):
        cells = [re.sub(r"\s+", " ", text(c)) for c in re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)]
        cells = [c for c in cells if c and c != "List of localities"]
        if cells:
            radky.append((bid, cells))
    if obec and radky:
        print(f"(hledám obec ve {len(radky)} svazcích, 1 dotaz na svazek – chvíli to potrvá)", file=sys.stderr)
    hledana = bez_diakritiky(obec or "")
    for bid, cells in radky:
        if obec:
            o = obce(bid)
            if hledana not in bez_diakritiky(o):
                continue
            cells = cells + ["obce: " + o[:300]]
        print(bid, "|", " | ".join(cells))


def bez_diakritiky(s):
    return "".join(c for c in unicodedata.normalize("NFKD", s.lower()) if not unicodedata.combining(c))


def obce(bid):
    if not str(bid).isdigit():
        sys.exit(f"id knihy je číslo, ne „{bid}“.")
    t, _ = get(f"/pages/ajaxobec4.php?id={bid}")
    casti = [re.sub(r"\s+", " ", c).strip() for c in re.split(r"[,|]", text(t))]   # portál odděluje „,,,,“ a „|“
    return ", ".join(dict.fromkeys(c for c in casti if c))


def svazek(bid):
    page, _ = get(f"/{bid}/1")
    t = re.search(r"document\.title=\"([^\"]*)\"", page) or re.search(r"<title>([^<]*)", page)
    nazev = t.group(1).strip() if t else f"kniha {bid}"
    if "DigiArchiv" in nazev:
        nazev = f"kniha {bid} (název doplň ručně)"
    path = os.path.join(ROOT, "data", "svazky.json")
    d = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
    # nejen matriky: i urbáře, pozemkové knihy a sčítání ze `strom` (#63) – proto obecně „SOA Třeboň“ a popis = obce
    d[f"trebon_{bid}"] = {"archiv": "SOA Třeboň", "portal": "digi.ceskearchivy.cz",
                          "svazek": nazev, "popis": obce(bid)[:300], "url": f"{BASE}/{bid}"}
    json.dump(d, open(path, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
    print(f"trebon_{bid} -> {nazev}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    if a[0] == "misto":
        print(*misto(a[1]), sep=" | ")
    elif a[0] == "svazky":
        for bid, c in svazky(a[1]):
            print(bid, "|", " | ".join(x[:300] for x in c if x))
    elif a[0] == "rejstrik":
        _print_rejstrik(rejstrik(a[1], a[2]))
    elif a[0] == "snimek":
        snimek(a[1], a[2], a[3], len(a) > 4)
    elif a[0] == "svazek":
        svazek(a[1])
    elif a[0] == "strom":
        strom(a[1] if len(a) > 1 else "1", a[2] if len(a) > 2 else None)
    elif a[0] == "obce":
        print(obce(a[1]))
    else:
        sys.exit(__doc__)
