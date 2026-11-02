#!/usr/bin/env python3
"""Vedlejší linie (sourozenci předků a jejich potomci) z rodinného stromu GEDCOM do data/vetve.json.

Použití (z kořene projektu):
  python3 -I tools/vetve_import.py                      -> jen výpis: kolik osob by se převzalo a kde strom nesedí s osoby.py
  python3 -I tools/vetve_import.py --zapsat             -> zapíše data/vetve.json (existující soubor nepřepíše)
  python3 -I tools/vetve_import.py --zapsat --prepsat   -> přepíše i existující data/vetve.json (ruční úpravy se ztratí!)
  … --ged dokumenty/jiny.ged                            -> jiný soubor stromu (výchozí dokumenty/strom.ged)

Postup: ve stromu najde výchozí osobu (jméno a rok narození z P[1] v data/osoby.py), přiřadí předkům Kekulého čísla
a u každého čísla ověří, že jde o stejnou osobu jako v osoby.py (jméno bez diakritiky, rok narození ±2). Výzkum mohl
strom mezitím opravit – kde osoba nesedí, nad ní se nepokračuje a její děti se nepřipojí (vypíše se seznam).
Převezme všechny potomky ověřených předků, kteří sami nejsou předky, a jejich manžele (i druhé manžele předků).
Z GEDCOM bere jen jména, data, místa a povolání – ne adresy, e-maily ani telefony. Stav všech osob „fam“ (rodinný strom).

Formát data/vetve.json:
  {"zdroj": …, "importovano": …, "predci": {"k16": "jméno v osoby.py při importu"},
   "osoby": [{"id": "g123", "n": "Jméno Příjmení", "sex": "M", "y": "1902–1980", "f": ["* 3. 4. 1902 Chvaly", …],
              "st": "fam", "rodice": ["k16", "k17"] | ["g45", "g46"] | [], "manzele": ["g200"], "zdroj": "ged:@I123@"}]}
  rodice: „k“ + Kekulé číslo = přímý předek z osoby.py, „g…“ = osoba z tohoto souboru; přiženění mají rodice [].
"""
import datetime, difflib, json, os, re, runpy, sys, unicodedata
for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
import ged_import as g   # noqa: E402

OUT = os.path.join(ROOT, "data", "vetve.json")


def norm(text):
    t = unicodedata.normalize("NFD", text or "")
    t = "".join(c for c in t if not unicodedata.combining(c)).lower()
    t = re.sub(r"\(.*?\)", " ", t).replace("ß", "ss")
    return " ".join(re.findall(r"[a-z]+", t))


def p_year(p):
    y = (p.get("y") or "").strip()
    if y.startswith(("?", "†")) or re.match(r"^[–-]", y):
        return None
    m = re.search(r"\d{4}", y)
    return int(m.group()) if m else None


def birth_year(ind):
    for n in ind["_sub"]:
        if n["tag"] in ("BIRT", "CHR"):
            y = g.year(g.first(n, "DATE"))
            if y:
                return y
    return None


def name_ok(p, ind):
    """Sedí jméno osoby ze stromu s P[k]? Tolerantně k pravopisu (Heeß/Hess, Markowetzová/Markovcová)."""
    spell = lambda t: t.replace("w", "v").replace("tz", "c").replace("th", "t").replace("ph", "f")
    a, b = spell(norm(p["n"])), spell(norm(ind and g.name(ind)))
    if not a or not b:
        return False
    wa, wb = a.split(), b.split()
    surname_ok = difflib.SequenceMatcher(None, wa[-1], wb[-1]).ratio() >= 0.75 if len(wa) > 1 and len(wb) > 1 else True
    given_ok = difflib.SequenceMatcher(None, wa[0], wb[0]).ratio() >= 0.75 or wa[0] in wb or wb[0] in wa
    return surname_ok and given_ok


def year_ok(p, ind):
    ya, yb = p_year(p), birth_year(ind)
    return ya is None or yb is None or abs(ya - yb) <= 2


def same_person(p, ind, partner_ok=False):
    """Je osoba ze stromu stejná jako P[k]? Jméno a rok narození ±2 – nebo jméno, když sedí i jméno manžela/manželky
    (stejný pár = stejná rodina, strom se jen liší v roku narození)."""
    return name_ok(p, ind) and (year_ok(p, ind) or partner_ok)


def years_text(ind):
    by = dy = ""
    for n in ind["_sub"]:
        d = g.first(n, "DATE")
        if n["tag"] in ("BIRT", "CHR") and not by and d:
            by = g.cz_date(d)
        if n["tag"] in ("DEAT", "BURI") and not dy and d:
            dy = g.cz_date(d)
    yb, yd = re.search(r"\d{4}", by), re.search(r"\d{4}", dy)
    pre = lambda d: "asi " if d.startswith("asi") else ""
    if yb and yd:
        return f"{pre(by)}{yb.group()}–{pre(dy)}{yd.group()}"
    if yb:
        return f"* {pre(by)}{yb.group()}"
    if yd:
        return f"† {yd.group()}"
    return ""


def facts(ind, recs):
    out = []
    for tag, date, place, extra in g.events(ind, recs):
        mark = g.EVENTS[tag]
        if tag == "MARR":
            txt = " ".join(x for x in (mark, date, place, "" if extra.startswith("(beze") else extra) if x)
            if txt != mark:
                out.append(txt)
        else:
            txt = " ".join(x for x in (mark, date, place) if x)
            if extra:
                txt += f" ({extra})"
            if txt != mark:
                out.append(txt)
    for n in g.sub(ind, "OCCU"):
        if n.get("val", "").strip():
            out.append(n["val"].strip())
    return out


def main():
    ged = sys.argv[sys.argv.index("--ged") + 1] if "--ged" in sys.argv else os.path.join(ROOT, "dokumenty", "strom.ged")
    recs = g.read(ged)
    I = {k: v for k, v in recs.items() if v["_type"] == "INDI"}
    F = {k: v for k, v in recs.items() if v["_type"] == "FAM"}
    P = runpy.run_path(os.path.join(ROOT, "data", "osoby.py"))["P"]

    root = [i for i in I.values() if norm(g.name(i)) == norm(P[1]["n"]) and birth_year(i) == p_year(P[1])]
    if len(root) != 1:
        sys.exit(f"Výchozí osobu {P[1]['n']} jsem ve stromu nenašel jednoznačně ({len(root)} kandidátů).")

    # předci: jen ověření (stejná osoba jako v osoby.py); nad neověřeným se nepokračuje
    kek, bad, queue = {1: root[0]["_id"]}, [], [1]
    ged_anc = set()   # všichni předci podle stromu (i neověření) – jejich děti nejsou „vedlejší linie“
    while queue:
        k = queue.pop()
        f, m = g.parents(I[kek[k]], recs)
        pair_ok = {2 * k: 2 * k + 1 in P and m is not None and name_ok(P[2 * k + 1], m),
                   2 * k + 1: 2 * k in P and f is not None and name_ok(P[2 * k], f)}
        for c, par in ((2 * k, f), (2 * k + 1, m)):
            if not par:
                continue
            ged_anc.add(par["_id"])
            if c in P and same_person(P[c], par, pair_ok[c]):
                kek[c] = par["_id"]
                queue.append(c)
            else:
                bad.append((c, P.get(c, {}).get("n", "– v osoby.py chybí –"), g.name(par), birth_year(par)))
    ged_anc |= set(kek.values())
    k_of = {v: k for k, v in kek.items()}

    def fams(pid):
        return [F[n["val"].strip()] for n in g.sub(I[pid], "FAMS") if n["val"].strip() in F]

    def spouse_in(fam, pid):
        return next((n["val"].strip() for n in fam["_sub"] if n["tag"] in ("HUSB", "WIFE") and n["val"].strip() != pid), None)

    def kids(fam):
        return [n["val"].strip() for n in fam["_sub"] if n["tag"] == "CHIL" and n["val"].strip() in I]

    gid = lambda x: "g" + re.sub(r"\D", "", x)
    ref = lambda x: f"k{k_of[x]}" if x in k_of else gid(x)
    people, skipped = {}, []

    def add(pid, parents):
        if pid in people or pid in ged_anc:
            return
        ind = I[pid]
        nm = g.name(ind)
        people[pid] = dict(id=gid(pid), n=nm if re.search(r"[^\W\d_]", nm) else "(beze jména)", sex=g.first(ind, "SEX") or "?", y=years_text(ind), f=facts(ind, recs),
                           st="fam", rodice=parents, manzele=[], zdroj=f"ged:{pid}")

    def descend(pid):
        for fam in fams(pid):
            sp = spouse_in(fam, pid)
            if sp and sp in I and sp not in ged_anc:
                add(sp, [])
                if gid(sp) not in people[pid]["manzele"]:
                    people[pid]["manzele"].append(gid(sp))
                if gid(pid) not in people[sp]["manzele"]:
                    people[sp]["manzele"].append(gid(pid))
            for c in kids(fam):
                if c not in people and c not in ged_anc:
                    add(c, [ref(pid)] + ([ref(sp)] if sp and sp in I else []))
                    descend(c)

    for pid, k in sorted(k_of.items(), key=lambda x: x[1]):
        for fam in fams(pid):
            sp = spouse_in(fam, pid)
            if sp in ged_anc and sp not in k_of:   # druhý rodič je předek podle stromu, ale nesedí s osoby.py
                skipped.append((k, g.name(I[sp]), len(kids(fam))))
                continue
            if sp and sp in k_of and k_of[sp] < k:   # pár předků už zpracován z druhé strany
                continue
            if sp and sp in I and sp not in ged_anc:   # další manželství předka
                add(sp, [])
                people[sp]["manzele"].append(f"k{k}")
            for c in kids(fam):
                if c in ged_anc or c in people:
                    continue
                par = [f"k{k}"] + ([ref(sp)] if sp and sp in I else [])
                add(c, sorted(par, key=lambda r: (r[0] != "k", int(r[1:]) if r[0] == "k" else 0)))
                descend(c)

    osoby = [{k: v for k, v in p.items() if v != [] or k in ("rodice", "f")} for p in people.values()]
    osoby.sort(key=lambda p: int(p["id"][1:]))
    n_desc = sum(1 for p in osoby if p["rodice"])
    print(f"Strom: {len(I)} osob. Předků ověřeno {len(kek)}, nesedí {len(bad)}.")
    print(f"Vedlejší linie: {n_desc} potomků předků (sourozenci a jejich rodiny), {len(osoby) - n_desc} přiženěných.")
    if bad:
        print("\nPředci, kde strom nesedí s osoby.py (nad nimi se nepokračuje):")
        for c, pn, gn, gy in sorted(bad):
            print(f"  {c}: osoby.py „{pn}“ × strom „{gn}“ {gy or ''}")
    if skipped:
        print("\nRodiny vynechané, protože druhý rodič nesedí s osoby.py:")
        for k, sn, nk in skipped:
            print(f"  předek {k} × {sn}: {nk} dětí")
    if "--zapsat" not in sys.argv:
        print("\n(jen výpis – zapíšete s --zapsat)")
        return
    if os.path.exists(OUT) and "--prepsat" not in sys.argv:
        sys.exit(f"\n{OUT} už existuje – přepíšu ho jen s --prepsat (ruční úpravy by se ztratily).")
    used = sorted({r for p in osoby for r in p["rodice"] + p.get("manzele", []) if r.startswith("k")}, key=lambda r: int(r[1:]))
    data = dict(zdroj=os.path.relpath(ged, ROOT).replace("\\", "/"), importovano=datetime.date.today().isoformat(),
                predci={r: P[int(r[1:])]["n"] for r in used}, osoby=osoby)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print(f"\nZapsáno {OUT}: {len(osoby)} osob.")


if __name__ == "__main__":
    main()
