#!/usr/bin/env python3
"""Pražské policejní přihlášky 1850–1914 (Národní archiv, digi.nacr.cz/prihlasky2) bez prohlížeče.

Použití (z kořene projektu):
  policie_prihlasky.py <Příjmení> [Jméno] [rok_od] [rok_do] [--stran N]
      -> pořadí | příjmení | jméno | rok narození, všechny výsledky (web je dává po 20; nástroj projde
         nejvýš N stran, výchozí 5 = 100 výsledků – při víc zúži hledání jménem nebo roky)
Příjmení je začátek jména bez diakritiky („Kolar“ najde Kolář, Kolár, Kolarik…; „Simek“ najde Šimek, „Šimek“ ne).
Roky = rok narození osoby. Ve výsledcích jsou i manželky a děti – bývají na STEJNÉ kartě jako hlava rodiny,
takže dvě pořadí se stejným kartonem a obrazem jsou v pořádku.
  policie_prihlasky.py karta <pořadí> <výstup.jpg> <Příjmení> [Jméno] [rok_od] [rok_do]
      -> stáhne kartu (hlava rodiny, manželka s místem narození, děti, adresy) z výsledku stejného hledání
         (i pořadí nad 20), vypíše, komu pořadí patří, citaci a trvalý odkaz (portál dává kartu jen v 1000 × 1333 px)
Trvalý odkaz na kartu:
  https://digi.nacr.cz/prihlasky2/index.php?action=link&ref=czarch:CZ-100000010:874&karton=<K>&folium=<F>
Pokrývá Prahu I–VIII; po roce ~1900 i část Žižkova a Vinohrad. Smíchov, Karlín ap. byly do 1922 samostatná města.
"""
import re, sys, time, urllib.parse, urllib.request
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__))); import slusne  # noqa: E402 – brzda proti zablokování archivem (společný limit dotazů, tools/slusne.py)
for _s in (sys.stdout, sys.stderr):   # UTF-8 výstup i na Windows bez -X utf8 (cp1250 neumí třeba „→“)
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

BASE = "https://digi.nacr.cz/prihlasky2/"
NA_STRANU = 20
_op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
_op.addheaders = [("User-Agent", "Mozilla/5.0 (rodokmen)")]
RADEK = re.compile(r'record=(\d+)">([^<]*)</a></td>\s*<td class="table_jmeno">([^<]*)</td>\s*<td class="table_rok">([^<]*)<')


def get(url, data=None):
    if data:
        data = urllib.parse.urlencode(data).encode()
    for i in range(5):   # server občas neodpovídá
        try:
            return _op.open(url, data, timeout=40).read().decode("utf-8", "replace")
        except Exception as e:
            print("znovu", i + 1, e, file=sys.stderr)
            time.sleep(5 * (i + 1))
    sys.exit("server neodpovídá")


def radky(h):
    """{pořadí: (příjmení, jméno, rok)} z jedné strany výsledků."""
    return {int(r[0]): tuple(x.strip() for x in r[1:]) for r in RADEK.findall(h)}


def pocet(h):
    m = re.search(r"záznamů:\s*(\d+)", h)
    return int(m.group(1)) if m else 0


def strana(session, poradi):
    """Strana výsledků, na které je pořadí (web stránkuje po 20: action=list&od=0, 20, 40…)."""
    od = (poradi - 1) // NA_STRANU * NA_STRANU
    return radky(get(f"{BASE}?session={session}&action=list&od={od}"))


def karta(session, poradi, out, prvni):
    poradi = int(poradi)
    kdo = (prvni if poradi <= NA_STRANU else strana(session, poradi)).get(poradi)
    h = get(f"{BASE}?session={session}&action=image&record={poradi}")
    m = re.search(r'src="images/((\d+)-(\d+)\.jpg)"', h)
    zaznam = re.search(r"záznam č\.\s*(\d+)", h)
    if not m or (zaznam and int(zaznam.group(1)) != poradi):
        sys.exit(f"karta č. {poradi} nenalezena (je pořadí z tohoto hledání?)")
    for i in range(5):
        try:
            data = _op.open(BASE + "images/" + m.group(1), timeout=60).read()
            break
        except Exception as e:
            print("znovu", i + 1, e, file=sys.stderr)
            time.sleep(5 * (i + 1))
    else:
        sys.exit("server neodpovídá")
    with open(out, "wb") as f:
        f.write(data)
    k, fo = int(m.group(2)), int(m.group(3))
    if kdo:
        print(f"pořadí {poradi}: {' '.join(kdo)} – hledej tuto osobu na kartě (manželka a děti bývají na kartě hlavy rodiny)")
    print(out, f"– Národní archiv, Policejní ředitelství I, konskripce, karton {k}, obraz {fo}")
    print(f"odkaz: {BASE}index.php?action=link&ref=czarch:CZ-100000010:874&karton={k}&folium={fo}")


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    args = sys.argv[1:]
    stran = 5
    if "--stran" in args:
        i = args.index("--stran")
        if i + 1 >= len(args) or not args[i + 1].isdigit() or int(args[i + 1]) < 1:
            sys.exit("--stran chce kladné číslo.")
        stran = int(args[i + 1])
        del args[i:i + 2]
    card = None
    if args[0] == "karta":
        if len(args) < 4 or not args[1].isdigit():
            sys.exit(__doc__)
        card, args = (args[1], args[2]), args[3:]
    a = args + ["", "", ""]
    prijmeni, jmeno, od, do = a[0], a[1], a[2], a[3]
    m = re.search(r"session=([0-9a-f]+)", get(BASE))
    if not m:
        sys.exit("nepodařilo se otevřít vyhledávání (změnil se web?)")
    session = m.group(1)
    h = get(BASE + "?session=" + session,
            {"prijmeni": prijmeni, "jmeno": jmeno, "action": "hledani2", "odroku": od, "doroku": do})
    n, vysledky = pocet(h), radky(h)
    if card:
        if int(card[0]) > n:
            sys.exit(f"pořadí {card[0]} neexistuje – hledání má {n} záznamů")
        return karta(session, card[0], card[1], vysledky)
    print(f"# {prijmeni} {jmeno} {od}–{do}: {n} záznamů")
    dalsi = range(NA_STRANU, min(n, stran * NA_STRANU), NA_STRANU)
    for od_ in dalsi:   # další strany po 20 (brzda: 1 dotaz za 2 s)
        vysledky.update(radky(get(f"{BASE}?session={session}&action=list&od={od_}")))
    for k in sorted(vysledky):
        print("\t".join((str(k),) + vysledky[k]))
    if n > stran * NA_STRANU:
        print(f"# zobrazeno {len(vysledky)} z {n} – zúži hledání jménem nebo roky narození (nebo --stran {n // NA_STRANU + 1})")


if __name__ == "__main__":
    main()
