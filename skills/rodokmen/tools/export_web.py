#!/usr/bin/env python3
"""Export dat rodokmenu (data/*) do webu ve složce web/.

Čte data/osoby.py, data/zaznamy.json, data/svazky.json, data/prepisy.json, data/zvyrazneni.json,
data/mista.json, data/web.json, data/dokumenty.json a markdownové poznámky. Zapisuje
web/src/data/site.json, web/src/generated/*, web/public/{img,zdroje}, web/public/prihlaseni.html,
web/nginx.conf a web/netlify/edge-functions/brana.js.

Spouští se z web/ příkazem `npm run data` (nebo přímo `python3 -I tools/export_web.py`, na Windows `python -I -X utf8 …`).
"""
import datetime, hashlib, html, json, os, re, shutil, subprocess, sys, unicodedata
for _s in (sys.stdout, sys.stderr):   # UTF-8 výstup i na Windows bez -X utf8 (cp1250 neumí třeba „→“)
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
DATA = os.path.join(ROOT, "data")
WEB = os.path.join(ROOT, "web")
VYREZY = os.path.join(ROOT, "vyrezy")      # výřezy zápisů a dokumentů (asi 1800 px) – zobrazují se na webu
ZDROJE = os.path.join(ROOT, "zdroje")      # tytéž výřezy v plném rozlišení (proklik)

LINE_COLORS = {8: "#EFB45F", 9: "#F09A78", 10: "#E58AA6", 11: "#B99AE0",
               12: "#86B8E8", 13: "#6FCBB9", 14: "#9CD17A", 15: "#D3D46A"}
STATUS = {"doc": "doloženo matrikou", "prob": "pravděpodobné", "fam": "údaj od rodiny",
          "mh": "jen z cizího rodokmenu", "unk": "neznámé"}
SIDE_KIND = {"bratr": "sib", "sestra": "sib", "manžel": "spouse", "manželka": "spouse", "syn": "child", "dcera": "child"}
SIB_STATUS = {"hotovo": "done", "částečně": "partial"}
KINDS = {"N": "křest / narození", "O": "sňatek", "Z": "úmrtí", "I": "rejstřík", "S": "sčítání lidu", "J": "jiný pramen"}


BEZPECNY_KLIC = re.compile(r"(?!\.)(?!.*\.\.)[\w.-]+")   # klíč = název souboru obrázku: žádné / \ ani „..“ (#25)


def bezpecny(key):
    return isinstance(key, str) and bool(BEZPECNY_KLIC.fullmatch(key))


def jload(name, default):
    path = os.path.join(DATA, name)
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_people():
    ns = {}
    exec(open(os.path.join(DATA, "osoby.py"), encoding="utf-8").read(), ns)
    for name, default in (("P", {}), ("SIDE", []), ("LINES", {}), ("ISSUES", []), ("HYPOTEZY", []), ("SAME", {}), ("RODINA", {})):
        ns.setdefault(name, default)
    return ns


def record_rows():
    svazky = jload("svazky.json", {})
    rows = []
    for z in jload("zaznamy.json", []):
        sv = svazky.get(z.get("svazek", ""), {})
        key = z["klic"]
        if not bezpecny(key):
            print(f"POZOR: zápis s klíčem {key!r} vynechán – klíč smí mít jen písmena, číslice, _ - . (tools/kontrola.py)")
            continue
        rows.append(dict(
            key=key, kind=z.get("druh", "J"), date=z.get("datum", ""), title=z.get("nazev", key),
            summary=z.get("shrnuti", ""), scan=z.get("snimek", ""),
            archive=sv.get("archiv", ""), volume=sv.get("svazek", ""), vdesc=sv.get("popis", ""),
            portal=sv.get("portal", "archivu"), url=z.get("odkaz") or sv.get("url", ""),
            img=os.path.exists(os.path.join(VYREZY, key + ".jpg")),
            full=os.path.exists(os.path.join(ZDROJE, key + ".jpg")),
        ))
    return rows


def log_rows():
    """Řádky tabulky deníku (data/research_log.md) podle čísla: {n: dict(n, date, source, range, goal, result)} – pro ISSUES."""
    rows = {}
    path = os.path.join(DATA, "research_log.md")
    if not os.path.exists(path):
        return rows
    for line in open(path, encoding="utf-8"):
        m = re.match(r"^\|\s*(\d+)\s*\|", line)
        if not m:
            continue
        cells = [c.strip() for c in line.strip()[1:-1].split(" | ")]
        if len(cells) < 6:
            continue
        if len(cells) > 7:   # svislítko uvnitř textu výsledku
            cells = cells[:5] + [" | ".join(cells[5:-1]), cells[-1]]
        clean = lambda t: re.sub(r"\*\*(.+?)\*\*", r"\1", t).replace("`", "")
        rows[int(m.group(1))] = dict(n=int(m.group(1)), date=cells[1], source=clean(cells[2]), range=clean(cells[3]),
                                     goal=clean(cells[4]), result=clean(cells[5]))
    return rows


def strip_comments(md):
    """Poznámky <!-- … --> v markdownu jsou pro Clauda, ne pro web."""
    return re.sub(r"<!--.*?-->\n?", "", md, flags=re.S)


def story_frontmatter(path, slug):
    """Načte omezené skalární frontmatter pro příběhy bez další Python závislosti."""
    text = open(path, encoding="utf-8").read()
    match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", text, re.S)
    if not match:
        sys.exit(f"CHYBA: {path}: chybí YAML frontmatter.")
    fields = {}
    for line in match.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        item = re.fullmatch(r"(title|lead|rod):\s*(.*?)\s*", line)
        if not item:
            sys.exit(f"CHYBA: {path}: očekávám pouze skalární pole title, lead a rod.")
        key, value = item.groups()
        if key in fields:
            sys.exit(f"CHYBA: {path}: pole {key} je uvedené vícekrát.")
        if value.startswith('"'):
            try:
                value = json.loads(value)
            except json.JSONDecodeError as ex:
                sys.exit(f"CHYBA: {path}: neplatná hodnota {key}: {ex}")
            if not isinstance(value, str):
                sys.exit(f"CHYBA: {path}: {key} musí být text.")
        elif value.startswith("'"):
            if len(value) < 2 or not value.endswith("'"):
                sys.exit(f"CHYBA: {path}: neuzavřená hodnota {key}.")
            value = value[1:-1].replace("''", "'")
        fields[key] = value
    for key in ("title", "lead"):
        if key not in fields:
            sys.exit(f"CHYBA: {path}: ve frontmatter chybí pole {key}.")
    if not fields["title"].strip():
        sys.exit(f"CHYBA: {path}: title nesmí být prázdný.")
    rod = fields.get("rod")
    # rod je volitelný (příběh nemusí patřit jednomu rodu – třeba „Za války“); je-li, musí to být číslo 8–15
    if rod is not None and not re.fullmatch(r"(?:[8-9]|1[0-5])", rod):
        sys.exit(f"CHYBA: {path}: rod musí být číslo 8 až 15 (nebo pole rod vynech).")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        sys.exit(f"CHYBA: {path}: název souboru musí být bezpečný slug z malých písmen, číslic a pomlček.")
    return dict(slug=slug, title=fields["title"], lead=fields["lead"],
                rod=int(rod) if rod is not None else None, text=text)


def slugify(text):
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def norm_answer(text):
    """Stejná normalizace jako v prihlaseni.html: bez diakritiky, malá písmena, jen a-z0-9."""
    t = unicodedata.normalize("NFD", text)
    t = "".join(c for c in t if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9]", "", t)


def years(y):
    y = (y or "").strip()
    ys = re.findall(r"\d{4}", y)
    if not ys:
        return ""
    approx = "≈" if re.match(r"^(asi|≈)", y) else ""
    head, dash, tail = y.partition("–")
    if y.startswith(("?", "†")) or (dash and not re.search(r"\d", head)) or re.match(r"po\b", y):
        # neznámé narození: ukázat jen úmrtí („? – před 1743“ → „† před 1743“, „– po 1921“ → „žil 1921“)
        if re.search(r"\bpo\b", tail or y):
            return "žil " + ys[-1]
        return "† " + ("před " if "před" in y else "") + ys[-1]
    if y.startswith("*"):
        return "* " + ys[0]
    if len(ys) == 1:
        return ("před " if re.match(r"před\b", y) else approx) + ys[0]   # „před 1740“ není přesný rok (#25)
    second = "?" if "před" in tail else ("po " if re.search(r"\bpo\b", tail) else "") + \
        ("≈" if re.search(r"(asi|≈)", tail) else "") + ys[-1]
    return f"{approx}{ys[0]}–{second}"


def gen(k):
    return k.bit_length() - 1


def relation(k):
    g, male = gen(k), (k % 2 == 0)
    if g == 0:
        return "výchozí osoba rodokmenu"
    if g == 1:
        return "otec" if male else "matka"
    base = "dědeček" if male else "babička"
    if g <= 5:
        return "pra" * (g - 2) + base
    return f"{'předek' if male else 'předkyně'} v {g}. generaci ({'pra' * (g - 2)}{base})"


def placeholder(p):
    return p["n"].startswith(("otec neuveden", "matka neuvedena")) or p["n"] in ("", "?")


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # -I nepřidává složku skriptu
from obraz import najdi_magick   # společný hledač ImageMagicku (tools/obraz.py)
from osobnosti import zarad as osobnost   # stránka „Osobnosti“: kategorie podle faktů (tools/osobnosti.py)


def magick_bin():
    return najdi_magick()


def size(path):
    w, h = subprocess.run([magick_bin(), path + "[0]", "-format", "%w %h", "info:"],
                          capture_output=True, text=True, check=True).stdout.split()
    return int(w), int(h)


def draw_boxes(src, dst, boxes, small):
    """Kopie výřezu v plném rozlišení s nakreslenými rámečky (pokud má stejný poměr stran jako webový výřez,
    na kterém se rámečky měřily). Vrací False, pak se kopíruje bez rámečků."""
    if not os.path.exists(small) or not magick_bin():
        return False
    (W, H), (w, h) = size(src), size(small)
    if abs(W / H - w / h) > 0.015 * (w / h):
        return False
    sw = max(4, round(W / 450))
    cmd = [magick_bin(), src, "-fill", "none", "-stroke", "#d7302a", "-strokewidth", str(sw)]
    for x0, y0, x1, y1 in boxes:
        cmd += ["-draw", f"rectangle {x0 * W:.0f},{y0 * H:.0f},{x1 * W:.0f},{y1 * H:.0f}"]
    subprocess.run(cmd + ["-quality", "90", dst], check=True)
    return True


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def login_files(cfg):
    """Přihlašovací brána: otázka na webu, na serveru (nginx i Netlify) jen otisk odpovědi (SHA-256).
    Stejný otisk spočítá přihlašovací stránka a uloží ho do cookie – samotná odpověď se nikam neukládá."""
    login = cfg.get("prihlaseni") or {}
    answer = norm_answer(login.get("odpoved", ""))
    tpl = open(os.path.join(WEB, "prihlaseni.sablona.html"), encoding="utf-8").read()
    if "rodokmen:" not in tpl:   # stará šablona (do 0.4.0) ukládá do cookie odpověď – s novou bránou by se nikdo nepřihlásil
        sys.exit("CHYBA: web/ má starou šablonu přihlášení. Aktualizujte projekt: python3 -I <skill>/tools/novy_projekt.py <složka projektu>")
    contact = cfg.get("kontakt") or {}
    hint = ""
    if contact.get("email"):
        hint = (f'Neznáte odpověď? Napište {html.escape(contact.get("jmeno", ""))} na '
                f'<a href="mailto:{html.escape(contact["email"])}">{html.escape(contact["email"])}</a>.')
    page = (tpl.replace("{{NAZEV}}", html.escape(cfg.get("nazev", "Rodokmen")))
               .replace("{{UVOD}}", html.escape(login.get("uvod", "Tenhle web je jen pro rodinu a příbuzné.")))
               .replace("{{OTAZKA}}", html.escape(login.get("otazka", "Odpověď na rodinnou otázku")))
               .replace("{{NAPOVEDA}}", hint))
    write(os.path.join(WEB, "public", "prihlaseni.html"), page)

    edge = os.path.join(WEB, "netlify", "edge-functions", "brana.js")
    if answer:
        digest = hashlib.sha256(("rodokmen:" + answer).encode()).hexdigest()
        nginx_map = f'  "{digest}" 1;'
        write(edge, open(os.path.join(WEB, "netlify", "brana.sablona.js"), encoding="utf-8").read().replace("{{HASH}}", digest))
    else:   # bez přihlášení – web je otevřený
        nginx_map = "  default 1;"
        if os.path.exists(edge):
            os.remove(edge)
    nginx = open(os.path.join(WEB, "nginx.sablona.conf"), encoding="utf-8").read()
    if not answer:   # šablona už má „default 0;“ – druhý default nginx odmítne
        nginx = nginx.replace("  default 0;\n", "")
    nginx = nginx.replace("{{ODPOVED}}", nginx_map)
    write(os.path.join(WEB, "nginx.conf"), nginx)
    return bool(answer)


def main():
    ns = load_people()
    P, LINES, SIDE, ISSUES = ns["P"], ns["LINES"], ns["SIDE"], ns["ISSUES"]
    if 1 not in P:
        sys.exit("V data/osoby.py chybí výchozí osoba (číslo 1).")
    SAME = ns["SAME"]                       # alias Kekulé → kanonické Kekulé (předek v rodokmenu vícekrát)
    cfg = jload("web.json", {})
    # web.json "puvodni_jmena": true → jméno osoby v původních tvarech ze zápisů (pole zap v osoby.py, „Nowakin / Nováková“);
    # jinak dnešní podoba n. Adresa stránky (slug) je vždy podle n.
    puvodni = lambda p: " / ".join(p["zap"]) if cfg.get("puvodni_jmena") and p.get("zap") else p["n"]
    login = cfg.get("prihlaseni") or {}
    if "--nasazeni" in sys.argv and not norm_answer(login.get("odpoved", "")) and not login.get("otevreny"):
        sys.exit("CHYBA: v data/web.json není odpověď na přihlašovací otázku – web by byl otevřený komukoli.\n"
                 "Nastavte prihlaseni.odpoved, nebo (jen když to opravdu chcete) prihlaseni.otevreny: true.")
    docs_cfg = jload("dokumenty.json", [])
    recs = {r["key"]: r for r in record_rows()}

    slugs, used = {}, set()
    for k in sorted(P):
        p = P[k]
        if placeholder(p) or k in SAME:
            continue
        yv = (p.get("y") or "").strip()
        ys = [] if yv.startswith(("?", "†")) else re.findall(r"\d{4}", yv)   # rok úmrtí do adresy nedávat
        s = base = slugify(p["n"] + (" " + ys[0] if ys else ""))
        n = 0
        while s in used or not s:   # i „jan-3“ už může být obsazené (osoba „Jan 3“) – zkoušet dál (#25)
            s = (f"{base}-{k}" if not n else f"{base}-{k}-{n}").lstrip("-")
            n += 1
        used.add(s)
        slugs[k] = s
    for a, c in SAME.items():
        slugs[a] = slugs[c]
    aliases_of = {}
    for a, c in SAME.items():
        aliases_of.setdefault(c, []).append(a)

    def line_of(k):
        g = gen(k)
        return k >> (g - 3) if g >= 3 else None

    people = {}
    for k, p in sorted(P.items()):
        if k not in slugs or k in SAME:
            continue
        path, c = [], k
        while c >= 1:
            path.append(slugs.get(c))
            c //= 2
        people[slugs[k]] = dict(
            k=k, slug=slugs[k], name=puvodni(p), modern=p["n"], zap=p.get("zap", []), y=p.get("y", ""), years=years(p.get("y")), st=p.get("st", "unk"),
            status=STATUS.get(p.get("st"), ""), gen=gen(k), sex="M" if k == 1 and p.get("sex", "M") == "M" or k > 1 and k % 2 == 0 else "F",
            rel=relation(k), line=line_of(k), facts=p.get("f", []), note=p.get("note", ""), vyz=p.get("vyz", ""), records=[r for r in p.get("r", []) if r in recs],
            father=slugs.get(2 * k), mother=slugs.get(2 * k + 1),
            fatherUnknown=(2 * k in P and placeholder(P[2 * k])), motherUnknown=(2 * k + 1 in P and placeholder(P[2 * k + 1])),
            child=slugs.get(k // 2) if k > 1 else None, spouse=slugs.get(k ^ 1) if k > 1 else None,
            family=None, ownFamily=None, path=path,
            side=[dict(name=s["n"], text=s["t"], records=[r for r in s.get("r", []) if r in recs], rel=s.get("v") or "příbuzný",
                       years=years(s.get("y")), kind=SIDE_KIND.get((s.get("v") or "").lower(), "other")) for s in SIDE if s["k"] == k],
            sibStatus=SIB_STATUS.get(p.get("sour"), "none"),
            docs=[dict(img=d["img"], caption=d["popis"]) for d in docs_cfg if k in d.get("osoby", [])],
            children=[slugs[c] for c in [k // 2] + [a // 2 for a in aliases_of.get(k, [])] if k > 1 and c in slugs],
            also=[dict(k=a, rel=relation(a), line=line_of(a), child=slugs.get(a // 2)) for a in aliases_of.get(k, [])],
        )
        if aliases_of.get(k):
            for a in aliases_of[k]:
                people[slugs[k]]["records"] = list(dict.fromkeys(people[slugs[k]]["records"] + [r for r in P.get(a, {}).get("r", []) if r in recs]))
            people[slugs[k]]["facts"] = [f for f in people[slugs[k]]["facts"] if not f.startswith("TÁŽ OSOBA")]

    # RODINA: osoby mimo přímou linii pro stromový graf. Odkazy: "k12" = přímý předek, "o:zkratka" = osoba z RODINA,
    # "?12" = neznámý předek na místě 12 (sourozenci se tak poznají i bez známých rodičů).
    R = ns["RODINA"]

    def ref(v):
        if isinstance(v, int):
            v = SAME.get(v, v)
            return f"k{v}" if v in slugs else f"?{v}"
        return f"o:{v}" if isinstance(v, str) and v in R else None

    others = []
    for oid, o in R.items():
        others.append(dict(id=f"o:{oid}", name=o["n"], y=o.get("y", ""), years=years(o.get("y")), sex=o.get("sex", ""),
                           st=o.get("st", ""), status=STATUS.get(o.get("st"), ""), father=ref(o.get("otec")),
                           mother=ref(o.get("matka")), partners=[x for x in map(ref, o.get("partner", [])) if x],
                           facts=o.get("f", []), note=o.get("note", ""), records=[r for r in o.get("r", []) if r in recs]))
    # na stránce osoby a rodiny je ukázat jako příbuzné (dřív byli jen v SIDE)
    for pp in people.values():
        me, k = f"k{pp['k']}", pp["k"]
        birth = (ref(2 * k), ref(2 * k + 1))
        for o in others:
            if (o["father"], o["mother"]) == birth:
                rel = "bratr" if o["sex"] == "M" else "sestra"
            elif o["father"] == me or o["mother"] == me:
                rel = "syn" if o["sex"] == "M" else "dcera"
            elif me in o["partners"] or any(me in (c["father"], c["mother"]) and o["id"] in (c["father"], c["mother"]) for c in others):
                rel = "manžel" if o["sex"] == "M" else "manželka"
            elif birth[0] in (o["father"], o["mother"]) and not birth[0].startswith("?") or                     birth[1] in (o["father"], o["mother"]) and not birth[1].startswith("?"):
                rel = "nevlastní bratr" if o["sex"] == "M" else "nevlastní sestra"
            else:
                continue
            pp["side"].append(dict(name=o["name"], text=o["note"] or "; ".join(o["facts"]), records=o["records"], rel=rel,
                                   years=o["years"], kind=SIDE_KIND.get(rel, "other"), id=o["id"]))

    families = {}
    for k in sorted(P):
        f, m = 2 * k, 2 * k + 1
        if k not in slugs or k in SAME or (f not in slugs and m not in slugs):
            continue
        fs, ms = slugs.get(f), slugs.get(m)
        fid = "-a-".join(x for x in (fs, ms) if x) if fs and ms else (fs or ms) + "-rodina"
        surname = (P[m]["n"].split()[-1] if m in P else "").strip("()?")
        mfacts = [x for x in P.get(f, {}).get("f", []) + P.get(m, {}).get("f", []) if x.startswith("×")]
        marriage = [x for x in mfacts if surname and surname[:5] in x] or mfacts
        frec = P.get(f, {}).get("r", []) + P.get(m, {}).get("r", [])
        child_rec = [r for r in P[k].get("r", []) if r in recs and recs[r]["kind"] == "N"]
        rlist = [r for r in dict.fromkeys(frec) if r in recs and recs[r]["kind"] == "O"] + child_rec
        if fid in families:   # stejný pár potkán dvakrát (předek v rodokmenu vícekrát) – jedna rodina, víc dětí
            fam = families[fid]
            fam["children"].append(slugs[k])
            fam["records"] = list(dict.fromkeys(fam["records"] + rlist))
            fam["side"] += people[slugs[k]]["side"]
        else:
            families[fid] = dict(id=fid, father=fs, mother=ms, fatherUnknown=f in P and placeholder(P[f]),
                                 child=slugs[k], children=[slugs[k]], marriage=marriage, records=rlist,
                                 line=line_of(f) if f in P else line_of(m), gen=gen(f), side=list(people[slugs[k]]["side"]))
        people[slugs[k]]["family"] = fid
        for x in (fs, ms):
            if x:
                people[x]["ownFamily"] = fid

    for p in people.values():   # stránka „Osobnosti“ (ruční vyz má na webu přednost)
        p["osobnost"] = None if p["vyz"] else osobnost(p["facts"])
    refs = {}
    for s, p in people.items():
        for r in p["records"] + [r for e in p["side"] for r in e["records"]]:
            refs.setdefault(r, []).append(s)
    hl = jload("zvyrazneni.json", {})
    prep = jload("prepisy.json", {})
    records = []
    for key, r in recs.items():
        r = dict(r)
        r["boxes"] = hl.get(key, {}).get("boxes", [])
        tr = prep.get(key, {})
        r["orig"], r["cs"] = tr.get("orig", ""), tr.get("cs", "")
        r["kindName"] = KINDS.get(r["kind"], r["kind"])
        r["people"] = list(dict.fromkeys(refs.get(key, [])))
        records.append(r)

    lines = {}
    for k, (name, desc) in sorted(LINES.items()):
        if k not in LINE_COLORS:
            continue
        members = [(p["k"], p) for p in people.values() if p["line"] == k]
        members += [(a["k"], p) for p in people.values() for a in p["also"] if a["line"] == k]
        members.sort(key=lambda x: x[0])
        ls = slugify(name) or f"rod-{k}"
        if ls in lines:   # dva rody stejného jména (dvoje Novákovi) – druhý by přepsal první (#25)
            ls = f"{ls}-{k}"
        lines[ls] = dict(k=k, slug=ls, name=name, desc=desc, color=LINE_COLORS[k],
                                    root=slugs.get(k), people=[p["slug"] for _, p in members],
                                    gens={p["slug"]: gen(kk) for kk, p in members})
    lines = {s: l for s, l in lines.items() if l["root"]}
    for p in people.values():
        p["lineSlug"] = next((l["slug"] for l in lines.values() if l["k"] == p["line"]), None)

    places = []
    for name, e in jload("mista.json", {}).items():
        if "lat" not in e:
            continue
        rx = re.compile(e.get("re") or re.escape(name))
        hits = [p for p in people.values() if rx.search(" ".join(p["facts"]))]
        byline = {}
        for p in sorted(hits, key=lambda p: p["k"]):
            byline.setdefault(p["line"] or 0, []).append(p["slug"])
        if e.get("hypoteza"):
            byline = {e.get("rod", 0): []}
        if not byline:
            continue
        yrs = [int(y) for p in hits for y in re.findall(r"\b(?:1[4-9]|20)\d\d\b", p["y"] or "")]
        places.append(dict(name=name, lat=e["lat"], lon=e["lon"], lines=[dict(k=k, people=v) for k, v in sorted(byline.items())],
                           years=[min(yrs), max(yrs)] if yrs else None, hypothesis=bool(e.get("hypoteza"))))

    known = [p for p in people.values() if p["k"] > 1]
    stats = dict(ancestors=len(known), documented=sum(p["st"] == "doc" for p in known), records=len(records),
                 generations=max(p["gen"] for p in people.values()) + 1,
                 updated=(lambda d: f"{d.day}. {d.month}. {d.year} {d.hour}:{d.minute:02d}")(datetime.datetime.now()))
    hypotheses = [dict(line=h.get("rod"), title=h.get("nadpis", "Hypotéza"), text=h.get("text", ""),
                       items=[dict(name=a, text=b) for a, b in h.get("polozky", [])],
                       records=[r for r in h.get("zaznamy", []) if r in recs]) for h in ns["HYPOTEZY"]]

    story_dir = os.path.join(DATA, "pribehy")
    story_files = sorted(
        os.path.join(story_dir, name) for name in os.listdir(story_dir)
        if name.endswith(".md")
    ) if os.path.isdir(story_dir) else []
    stories = [story_frontmatter(path, os.path.splitext(os.path.basename(path))[0])
               for path in story_files]
    multi_stories = bool(stories)
    configured_order = cfg.get("pribehy", [])
    if not isinstance(configured_order, list) or any(not isinstance(slug, str) for slug in configured_order):
        sys.exit("CHYBA: web.json → pribehy musí být seznam slugů příběhů.")
    if multi_stories:
        slugs_in_files = [story["slug"] for story in stories]
        if len(set(slugs_in_files)) != len(slugs_in_files):
            sys.exit("CHYBA: názvy souborů příběhů se po převodu na slug opakují.")
        if configured_order:
            if len(set(configured_order)) != len(configured_order) or set(configured_order) != set(slugs_in_files):
                sys.exit("CHYBA: web.json → pribehy musí obsahovat každý slug v data/pribehy/ právě jednou.")
            by_slug = {story["slug"]: story for story in stories}
            stories = [by_slug[slug] for slug in configured_order]
    elif configured_order:
        sys.exit("CHYBA: web.json → pribehy odkazuje na příběhy, ale data/pribehy/ neobsahuje žádné Markdown soubory.")
    legacy_story = os.path.join(DATA, "pribeh.md")
    if not multi_stories and os.path.exists(legacy_story):
        legacy_text = open(legacy_story, encoding="utf-8").read()
        legacy_match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", legacy_text, re.S)
        legacy_fields = {}
        if legacy_match:
            for line in legacy_match.group(1).splitlines():
                item = re.fullmatch(r"(title|lead):\s*(.*?)\s*", line)
                if item:
                    legacy_fields[item.group(1)] = item.group(2)
        stories = [dict(slug="", title=legacy_fields.get("title", "Příběh"),
                        lead=legacy_fields.get("lead", ""), rod=cfg.get("pribeh", {}).get("rod"),
                        text=legacy_text)]
    has_story = bool(stories)
    log = log_rows()

    def issue(i):   # otázka: řetězec, dvojice (otázka, stav), nebo dict(otazka, stav, osoby=[Kekulé], prosle=[řádky deníku])
        if isinstance(i, str):
            return dict(title=i, text="", people=[], checked=[])
        if isinstance(i, dict):
            return dict(title=i.get("otazka", ""), text=i.get("stav", ""),
                        people=[slugs[SAME.get(k, k)] for k in i.get("osoby", []) if SAME.get(k, k) in slugs],
                        checked=[log[n] for n in i.get("prosle", []) if n in log])
        return dict(title=i[0], text=i[1], people=[], checked=[])
    public_cfg = {k: v for k, v in cfg.items() if k != "prihlaseni"}
    public_cfg["maPribeh"] = has_story
    public_cfg["maVicePribehu"] = multi_stories
    public_cfg["pribehy"] = [story["slug"] for story in stories] if multi_stories else []
    site = dict(config=public_cfg, places=places, root=slugs[1], aliases={a: slugs[a] for a in SAME}, people=people,
                families=families, others=others, records=records, lines=lines,
                issues=[issue(i) for i in ISSUES], stats=stats, hypotheses=hypotheses,
                docs=[dict(img=d["img"], caption=d["popis"], people=[slugs[k] for k in d.get("osoby", []) if k in slugs])
                      for d in docs_cfg if os.path.exists(os.path.join(VYREZY, d["img"] + ".jpg"))])

    write(os.path.join(WEB, "src", "data", "site.json"), json.dumps(site, ensure_ascii=False, indent=1))
    gen_dir = os.path.join(WEB, "src", "generated")
    for src, dst in (("archivni_dotazy.md", "dotazy.md"), ("research_log.md", "denik.md"), ("zajimavosti.md", "zajimavosti.md")):
        path = os.path.join(DATA, src)
        text = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
        write(os.path.join(gen_dir, dst), strip_comments(re.sub(r"^# .*\n", "", text, count=1)))
    shutil.rmtree(os.path.join(gen_dir, "pribehy"), ignore_errors=True)
    if multi_stories:
        for story in stories:
            write(os.path.join(gen_dir, "pribehy", story["slug"] + ".md"), strip_comments(story["text"]))
    write(os.path.join(gen_dir, "pribehy.json"), json.dumps(
        [{key: story[key] for key in ("slug", "title", "lead", "rod")} for story in stories if story["slug"]],
        ensure_ascii=False, indent=1))
    story = stories[0]["text"] if stories else "---\ntitle: Příběh\nlead: ''\n---\n"
    write(os.path.join(gen_dir, "pribeh.md"), strip_comments(story))

    hrefs = os.path.join(gen_dir, "fan_hrefs.json")
    json.dump({k: f"/osoba/{s}/" for k, s in slugs.items()}, open(hrefs, "w", encoding="utf-8", newline="\n"))
    subprocess.run([sys.executable, "-I", "-X", "utf8", os.path.join(TOOLS, "fan_chart.py"),
                    os.path.join(gen_dir, "fan.svg"), "--web", hrefs], check=True, capture_output=True)

    gated = login_files(cfg)

    copied = removed = 0
    zv = os.path.join(DATA, "zvyrazneni.json")
    hl_mtime = os.path.getmtime(zv) if os.path.exists(zv) else 0
    wanted = [k for k in list(recs) + [d["img"] for d in docs_cfg] + ([cfg["uvod"]["foto"]] if cfg.get("uvod", {}).get("foto") else [])
              if bezpecny(k)]
    for sub, src_dir in (("img", VYREZY), ("zdroje", ZDROJE)):
        dst_dir = os.path.join(WEB, "public", sub)
        os.makedirs(dst_dir, exist_ok=True)
        keep = {k + ".jpg" for k in wanted if os.path.exists(os.path.join(src_dir, k + ".jpg"))}
        for name in os.listdir(dst_dir):   # obrázky smazaných zápisů nesmí zůstat na webu (#25); složky plní jen export
            if name.lower().endswith(".jpg") and name not in keep and os.path.isfile(os.path.join(dst_dir, name)):
                os.remove(os.path.join(dst_dir, name))
                removed += 1
        for key in wanted:
            src = os.path.join(src_dir, key + ".jpg")
            dst = os.path.join(dst_dir, key + ".jpg")
            if not os.path.exists(src):
                continue
            boxes = hl.get(key, {}).get("boxes", [])
            stale = not os.path.exists(dst) or os.path.getmtime(src) > os.path.getmtime(dst) \
                or (sub == "zdroje" and boxes and hl_mtime > os.path.getmtime(dst))
            if not stale:
                continue
            if sub == "zdroje" and boxes and draw_boxes(src, dst, boxes, os.path.join(VYREZY, key + ".jpg")):
                copied += 1
                continue
            shutil.copy2(src, dst)
            copied += 1
    print(f"{len(people)} osob, {len(families)} rodin, {len(records)} zápisů, {len(lines)} rodů, {len(places)} míst; "
          f"zkopírováno {copied} obrázků{f', smazáno {removed} starých' if removed else ''}; přihlášení {'zapnuté' if gated else 'VYPNUTÉ (web je otevřený)'}")

    # odkazy v textech, které nikam nevedou (adresa osoby se změní třeba doplněním roku narození: jan-novak → jan-novak-1798)
    targets = dict(osoba=people, zdroj=recs, rod=lines, rodina=families)
    # s více příběhy je pribeh.md jen kopie prvního z nich – kontroluje se pod svým jménem (pribehy/<slug>.md)
    texts = {f: open(os.path.join(gen_dir, f), encoding="utf-8").read()
             for f in (("zajimavosti.md",) if multi_stories else ("pribeh.md", "zajimavosti.md"))}
    if multi_stories:
        texts.update({f"pribehy/{story['slug']}.md": story["text"] for story in stories})
    texts["web.json"] = json.dumps(cfg, ensure_ascii=False)
    texts["osoby.py (hypotézy)"] = json.dumps(hypotheses, ensure_ascii=False)
    targets["pribehy"] = {story["slug"] for story in stories if story["slug"]}
    broken = [(f, m.group(0)) for f, t in texts.items()
              for m in re.finditer(r"/(osoba|zdroj|rod|rodina|pribehy)/([^/\s)\"'#?<>\]]+)", t)
              if m.group(2) not in targets[m.group(1)]]
    for f, link in dict.fromkeys(broken):
        print(f"POZOR: nefunkční odkaz {link}/ v {f} – oprav ho (adresy stránek jsou ve web/src/data/site.json)")

    # stránky Statistiky a Domy se počítají z hotového site.json
    sys.path.insert(0, TOOLS)
    import statistiky, domy_export
    statistiky.main()
    domy_export.main()


if __name__ == "__main__":
    main()
