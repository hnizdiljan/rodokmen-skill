#!/usr/bin/env python3
"""Kramerius – fulltextové hledání v digitálních knihovnách (API v5): noviny, ročenky, adresáře, seznamy ztrát.

Použití:
  kramerius.py 'SOLR_DOTAZ' [počet] [--server https://adresa]
      např. kramerius.py 'text_ocr:"Jan Novák" AND datum_begin:[1860 TO 1920]'
      Výpis: datum | titul | podrobnosti | PID stránky | dostupnost, pod tím úryvek textu.
  kramerius.py text <PID> [výstup.txt] [--server https://adresa]
      -> celý OCR text jedné VEŘEJNÉ stránky (stream TEXT_OCR; kontext k úryvku: obec, živnost, čísla domů).
         Neveřejné stránky (DNNT, autorská práva) nástroj nestahuje – ty jen v prohlížeči po přihlášení
         čtenáře, a na web z nich nanejvýš citace.
  Výchozí server je Národní knihovna (kramerius5.nkp.cz). `--server` zkusí jinou knihovnu se stejným rozhraním v5
  (např. Digitální studovnu Ministerstva obrany kramerius.army.cz – seznamy ztrát a vojenské matriky 1914–1918).
  Knihovny s rozhraním v7 (adresa …/search/api/client/v7.0) tento nástroj neumí.
Pozor: OCR adresářů a seznamů slévá sousední jména na řádku – shoda fráze v uvozovkách může být falešná, ověř ji
na obrázku stránky.
Když Python odmítne certifikát knihovny (na Windows chybí mezilehlý certifikát), nástroj zkusí totéž přes curl
(certifikát ověří Windows sám); curl jde taky přes brzdu.
"""
import json, re, shutil, ssl, subprocess, sys, urllib.error, urllib.parse, urllib.request
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__))); import slusne  # noqa: E402 – brzda proti zablokování archivem (společný limit dotazů, tools/slusne.py)
for _s in (sys.stdout, sys.stderr):   # UTF-8 výstup i na Windows bez -X utf8 (cp1250 neumí třeba „→“)
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

PID = re.compile(r"uuid:[0-9a-fA-F-]{36}")


def chyba_certifikatu(e):
    duvod = getattr(e, "reason", e)
    return isinstance(duvod, ssl.SSLCertVerificationError) or "CERTIFICATE_VERIFY_FAILED" in str(e)


def stahni(url):
    """Bajty odpovědi; při chybě certifikátu v Pythonu druhý pokus přes curl (systémové ověření certifikátu)."""
    try:
        with urllib.request.urlopen(url, timeout=90) as r:
            return r.read()
    except urllib.error.URLError as e:
        if not chyba_certifikatu(e):
            raise
        c = shutil.which("curl") or shutil.which("curl.exe")
        if not c:
            raise
        print("Python certifikát knihovny neověřil – zkouším curl.", file=sys.stderr)
        r = subprocess.run([c, "-sS", "--fail", "-m", "90", "-A", "Mozilla/5.0 (rodokmen)", url], capture_output=True)
        if r.returncode:
            raise OSError(r.stderr.decode("utf-8", "replace").strip() or f"curl kód {r.returncode}") from e
        return r.stdout


def dekoduj(data):
    """TEXT_OCR bývá v UTF-16 s BOM (FF FE), jinde UTF-8."""
    if data[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return data.decode("utf-16")
    if data[:3] == b"\xef\xbb\xbf":
        return data[3:].decode("utf-8", "replace")
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("cp1250", "replace")


def kontrola_serveru(server):
    s = urllib.parse.urlsplit(server)
    if (s.scheme != "https" or s.username or s.password or s.port not in (None, 443) or s.query or s.fragment
            or not re.fullmatch(r"[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)+", s.hostname or "")   # jen jména s tečkou (ne localhost)
            or re.fullmatch(r"[0-9.]+", s.hostname or "")):                               # ani IP adresy (interní sítě)
        sys.exit("--server musí být adresa knihovny s https:// a doménovým jménem (např. https://kramerius5.nkp.cz).")
    return s.hostname


def text(server, pid, out=None):
    if not PID.fullmatch(pid):
        sys.exit(f"PID má tvar uuid:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx (z výpisu hledání), ne „{pid}“.")
    api = f"{server}/search/api/v5.0/item/{pid}"
    try:
        info = json.loads(stahni(api))
    except (OSError, ValueError) as e:
        sys.exit(f"Knihovna stránku {pid} nevrátila ({type(e).__name__}: {str(e)[:100]}).")
    if info.get("policy") != "public":   # DNNT a díla pod autorským zákonem: neobcházet
        sys.exit(f"Stránka {pid} není veřejná (policy: {info.get('policy')}) – text jen v prohlížeči knihovny po přihlášení "
                 "čtenáře; nástroj ho nestahuje.")
    try:
        t = dekoduj(stahni(api + "/streams/TEXT_OCR"))
    except OSError as e:
        sys.exit(f"Stránka {pid} nemá OCR text, nebo ho knihovna nevydala ({str(e)[:100]}).")
    if out:
        with open(out, "w", encoding="utf-8", newline="\n") as f:
            f.write(t)
        print(f"uloženo {out} ({len(t)} znaků) – {info.get('root_title') or info.get('title', '')}")
    else:
        print(t)


def hledej(server, q, rows):
    host = urllib.parse.urlsplit(server).hostname
    if not (rows.isascii() and rows.isdigit()) or not 1 <= int(rows) <= 200:
        sys.exit("Počet výsledků musí být číslo 1–200.")
    p = {"q": f"({q}) AND fedora.model:page",   # závorky: jinak by „A OR B“ vrátilo i jiné typy dokumentů než stránky
         "fl": "PID,root_title,root_pid,datum_str,details,dostupnost", "rows": rows, "wt": "json",
         "hl": "true", "hl.fl": "text_ocr", "hl.fragsize": "250"}
    u = server + "/search/api/v5.0/search?" + urllib.parse.urlencode(p)
    try:
        d = json.loads(stahni(u))
    except (OSError, ValueError) as e:   # síť, HTTP chyba i odpověď, která není JSON (jiná verze rozhraní)
        sys.exit(f"Knihovna {host} neodpověděla jako Kramerius v5 ({type(e).__name__}: {str(e)[:100]}).")
    try:
        pocet, dokumenty, hl = d["response"]["numFound"], d["response"]["docs"], d.get("highlighting", {})
    except (KeyError, TypeError):
        sys.exit(f"Knihovna {host} vrátila JSON v jiné podobě než Kramerius v5 (možná verze 7).")
    print("found", pocet)
    for x in dokumenty:
        h = " | ".join(hl.get(x["PID"], {}).get("text_ocr", []))[:400].replace("\n", " ")
        print("-", x.get("datum_str"), "|", str(x.get("root_title"))[:60], "|", x.get("details"), "|", x["PID"], "|", x.get("dostupnost"))
        if h:
            print("   ", h)
    if dokumenty:
        print("Celý text veřejné stránky: kramerius.py text <PID>")


def main(a):
    server = "https://kramerius5.nkp.cz"
    if "--server" in a:
        i = a.index("--server")
        if i + 1 >= len(a):
            sys.exit("--server chce adresu knihovny (https://…).")
        server = a[i + 1].rstrip("/")
        del a[i:i + 2]
    kontrola_serveru(server)
    if not a:
        sys.exit(__doc__)
    if a[0] == "text":
        if len(a) < 2:
            sys.exit(__doc__)
        return text(server, a[1], a[2] if len(a) > 2 else None)
    return hledej(server, a[0], a[1] if len(a) > 1 else "30")


if __name__ == "__main__":
    main(sys.argv[1:])
