#!/usr/bin/env python3
"""Přidá nebo nahradí jednu položku v datech projektu – formát souboru zůstane stejný (odsazení 1, české znaky, konce
řádků LF), takže změna v historii je jen ta jedna položka.

Použití (z kořene projektu):
  zapis.py <soubor> <klíč> <vstup.json> [--sloucit]
    soubor     zaznamy | svazky | prepisy | zvyrazneni | mista | dokumenty   (= data/<soubor>.json)
    klíč       zaznamy: „klic“ zápisu; dokumenty: „img“; ostatní: klíč ve slovníku (id svazku, klíč zápisu, obec)
    vstup.json soubor s jedním objektem JSON (napiš ho nástrojem Write do pracovni/), „-“ = ze vstupu
    --sloucit  jen změní / doplní uvedená pole, ostatní pole položky nechá
Položka se stejným klíčem se nahradí, jinak se přidá na konec. Python skripty ani `sed -i` na data nepoužívej.

  zapis.py smazat <klíč zápisu> [--ano]
    zápis, který se ukázal jako cizí: odebere ho ze zaznamy, prepisy a zvyrazneni a smaže vyrezy/<klíč>.jpg
    a zdroje/<klíč>.jpg (#54). Bez --ano jen vypíše, co by smazal. Odkazy v data/osoby.py (r=[…]) nemění –
    vypíše, kde jsou, oprav je ručně. Ostatní položky a formát souborů zůstanou beze změny.
"""
import json, os, re, sys
for _s in (sys.stdout, sys.stderr):   # UTF-8 výstup i na Windows bez -X utf8 (cp1250 neumí třeba „→“)
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEZNAMY = {"zaznamy": "klic", "dokumenty": "img"}   # soubory se seznamem: pole, podle kterého se položka pozná
SLOVNIKY = {"svazky", "prepisy", "zvyrazneni", "mista"}
WS = re.compile(r"\s*")


def polozky(text, se_zacatkem=False):
    """Položky nejvyšší úrovně: [(klíč nebo None, začátek hodnoty, konec hodnoty)] – pozice v původním textu.
    se_zacatkem: navíc začátek celé položky (u slovníku pozice klíče)."""
    dec, i = json.JSONDecoder(), WS.match(text).end()
    otevreni, i, out = text[i], i + 1, []
    while True:
        i = WS.match(text, i).end()
        if text[i] in "]}":
            return out
        klic, zacatek = None, i
        if otevreni == "{":
            klic, i = dec.raw_decode(text, i)
            i = WS.match(text, WS.match(text, i).end() + 1).end()   # za dvojtečku
        _, j = dec.raw_decode(text, i)
        out.append((klic, i, j, zacatek) if se_zacatkem else (klic, i, j))
        i = WS.match(text, j).end()
        if text[i] == ",":
            i += 1


def bez_polozky(text, idx):
    """Text JSON bez položky idx (nejvyšší úroveň); ostatní položky zůstanou doslova."""
    poz = polozky(text, se_zacatkem=True)
    if len(poz) == 1:   # jediná položka: zůstane prázdný seznam / slovník
        _, _, e, z = poz[0]
        return text[:z].rstrip() + text[e:].lstrip(" \t\r\n,")
    if idx < len(poz) - 1:   # od začátku položky po začátek další (s čárkou a odsazením)
        return text[:poz[idx][3]] + text[poz[idx + 1][3]:]
    return text[:poz[idx - 1][2]] + text[poz[idx][2]:]   # poslední: od konce předchozí (i s čárkou)


def smazat(klic, ano):
    """Odebere zápis ze zaznamy / prepisy / zvyrazneni a smaže jeho obrázky."""
    zmeny = []
    for nazev in ("zaznamy", "prepisy", "zvyrazneni"):
        path = os.path.join(ROOT, "data", nazev + ".json")
        if not os.path.exists(path):
            continue
        text = open(path, encoding="utf-8-sig").read()
        if not text.strip():
            continue
        data = json.loads(text)
        if nazev == "zaznamy":
            idx = next((n for n, x in enumerate(data) if isinstance(x, dict) and x.get("klic") == klic), None)
        else:
            idx = next((n for n, (k, _, _) in enumerate(polozky(text)) if k == klic), None) if data else None
        if idx is not None:
            zmeny.append((f"data/{nazev}.json", path, bez_polozky(text, idx)))
    obrazky = [os.path.join(ROOT, d, klic + ".jpg") for d in ("vyrezy", "zdroje")]
    obrazky = [o for o in obrazky if os.path.exists(o)]
    if not zmeny and not obrazky:
        sys.exit(f"Zápis „{klic}“ v datech ani v obrázcích není.")
    for nazev, _, novy in zmeny:
        json.loads(novy)   # pojistka
        print(("odebráno z " if ano else "odebral bych z ") + nazev)
    for o in obrazky:
        print(("smazáno " if ano else "smazal bych ") + os.path.relpath(o, ROOT))
    osoby = os.path.join(ROOT, "data", "osoby.py")
    if os.path.exists(osoby):
        for n, radek in enumerate(open(osoby, encoding="utf-8"), 1):
            if re.search(r"[\"']" + re.escape(klic) + r"[\"']", radek):
                print(f"POZOR: data/osoby.py, řádek {n} cituje „{klic}“ – oprav ho ručně (r=[…], zaznamy=[…])")
    if not ano:
        print("Nic nesmazáno – pro provedení přidej --ano.")
        return
    for _, path, novy in zmeny:
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8", newline="\n") as f:
            f.write(novy)
        os.replace(tmp, path)
    for o in obrazky:
        os.remove(o)


def jako(text, s, e, v):
    """Hodnota v JSON ve stejném stylu jako text[s:e] (na jednom řádku, nebo odsazená po jedné mezeře)."""
    if "\n" not in text[s:e]:
        return json.dumps(v, ensure_ascii=False)
    odsazeni = text[text.rfind("\n", 0, s) + 1:s]
    odsazeni = odsazeni[:len(odsazeni) - len(odsazeni.lstrip())]
    return json.dumps(v, ensure_ascii=False, indent=1).replace("\n", "\n" + odsazeni)


def main():
    if sys.argv[1:2] == ["smazat"]:
        args = [a for a in sys.argv[2:] if a != "--ano"]
        if len(args) != 1:
            sys.exit(__doc__)
        return smazat(args[0], "--ano" in sys.argv[2:])
    args = [a for a in sys.argv[1:] if a != "--sloucit"]
    sloucit = "--sloucit" in sys.argv
    if len(args) != 3 or args[0] not in {*SEZNAMY, *SLOVNIKY}:
        sys.exit(__doc__)
    nazev, klic, vstup = args
    path = os.path.join(ROOT, "data", nazev + ".json")
    try:
        obj = json.load(sys.stdin if vstup == "-" else open(vstup, encoding="utf-8-sig"))
    except (OSError, ValueError) as e:
        sys.exit(f"Vstup {vstup} není platný JSON: {e}")
    if not isinstance(obj, dict):
        sys.exit("Vstup musí být jeden objekt JSON ({…}).")
    seznam = nazev in SEZNAMY
    if seznam and obj.setdefault(SEZNAMY[nazev], klic) != klic:
        sys.exit(f"Klíč „{klic}“ nesedí s „{SEZNAMY[nazev]}“ ve vstupu („{obj[SEZNAMY[nazev]]}“).")
    text = open(path, encoding="utf-8-sig").read() if os.path.exists(path) else ""
    try:
        data = json.loads(text) if text.strip() else ([] if seznam else {})
        if not isinstance(data, list if seznam else dict):
            raise ValueError("čekal jsem " + ("seznam [ … ]" if seznam else "slovník { … }"))
    except ValueError as e:
        sys.exit(f"data/{nazev}.json nejde přečíst ({e}) – oprav ho nejdřív (git diff ukáže poslední změnu).")

    poz = polozky(text) if data else []
    if seznam:
        idx = next((n for n, x in enumerate(data) if isinstance(x, dict) and x.get(SEZNAMY[nazev]) == klic), None)
    else:
        idx = next((n for n, (k, _, _) in enumerate(poz) if k == klic), None)
    stare = None if idx is None else (data[idx] if seznam else data[klic])
    nove = {**stare, **obj} if sloucit and isinstance(stare, dict) else obj
    if not poz:   # prázdný nebo nový soubor
        text = json.dumps([nove] if seznam else {klic: nove}, ensure_ascii=False, indent=1) + "\n"
    elif idx is not None:   # nahradit jen text té jedné položky, zbytek souboru zůstane doslova
        _, s, e = poz[idx]
        text = text[:s] + jako(text, s, e, nove) + text[e:]
    else:   # přidat za poslední položku ve stejném stylu
        _, s, e = poz[-1]
        radek = text[text.rfind("\n", 0, s) + 1:s]
        odsazeni = radek[:len(radek) - len(radek.lstrip())]
        text = (text[:e] + ",\n" + odsazeni + ("" if seznam else json.dumps(klic, ensure_ascii=False) + ": ")
                + jako(text, s, e, nove) + text[e:])
    json.loads(text)   # pojistka: výsledek musí být platný JSON

    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(tmp, path)   # celý soubor naráz – při chybě nezůstane rozepsaný
    print(f"data/{nazev}.json: {'přidáno' if idx is None else 'změněno'} „{klic}“")


if __name__ == "__main__":
    main()
