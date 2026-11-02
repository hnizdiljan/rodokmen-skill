"""export_web.py nad ukázkovým projektem (novy_projekt.py --ukazka) – bez Node.js, jen data webu."""
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]


def run(*args):
    return subprocess.run([sys.executable, "-I", "-X", "utf8", *map(str, args)],
                          capture_output=True, text=True, encoding="utf-8")


class ExportWebTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="rk_test_export_")
        cls.proj = Path(cls.tmp) / "projekt"
        r = run(SKILL / "tools" / "novy_projekt.py", cls.proj, "--ukazka")
        assert r.returncode == 0, r.stdout + r.stderr
        cls.osoby = (cls.proj / "data" / "osoby.py").read_text(encoding="utf-8")
        cls.web = (cls.proj / "data" / "web.json").read_text(encoding="utf-8")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def setUp(self):
        (self.proj / "data" / "osoby.py").write_text(self.osoby, encoding="utf-8")
        (self.proj / "data" / "web.json").write_text(self.web, encoding="utf-8")
        (self.proj / "data" / "dokumenty.json").write_text("[]", encoding="utf-8")

    def export(self):
        r = run(self.proj / "tools" / "export_web.py")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return r.stdout

    def site(self):
        return json.loads((self.proj / "web" / "src" / "data" / "site.json").read_text(encoding="utf-8"))

    def set_same(self, same, extra=""):
        text = self.osoby.replace("SAME = {}", f"SAME = {same!r}")
        self.assertIn("SAME = {}", self.osoby)
        if extra:
            text = text.replace("\nSAME = ", f"\n{extra}\nSAME = ", 1)
        (self.proj / "data" / "osoby.py").write_text(text, encoding="utf-8")

    def test_alias_bez_polozky_v_p(self):
        # #50 / #31: alias ze SAME bez vlastní položky v P – dřív KeyError, vějíř se vůbec nevyrobil
        self.set_same({71: 65})
        self.export()
        site = self.site()
        anna, vaclav = site["aliases"]["71"], site["aliases"]["142"]   # 142 = otec aliasu = otec osoby 65 (130)
        self.assertEqual(site["people"][anna]["k"], 65)
        self.assertEqual(site["people"][vaclav]["k"], 130)
        self.assertEqual([a["k"] for a in site["people"][anna]["also"]], [71])
        rod = next(l for l in site["lines"].values() if l["k"] == 8)
        self.assertEqual(len(rod["people"]), len(set(rod["people"])))   # předek v rodu dvakrát je v seznamu jednou
        svg = (self.proj / "web" / "src" / "generated" / "fan.svg").read_text(encoding="utf-8")
        hrefs = re.findall(r'<a href="([^"]+)"><title>([^<]*)</title>', svg)
        for slug in (anna, vaclav):   # na obou místech ve vějíři, podruhé s poznámkou
            titles = [t for h, t in hrefs if h == f"/osoba/{slug}/"]
            self.assertEqual(len(titles), 2, titles)
            self.assertEqual(sum("vícekrát" in t for t in titles), 1, titles)

    def test_alias_s_polozkou_v_p(self):
        self.set_same({71: 65}, "P[71] = {'n': 'Anna Junková', 'y': '1803–1870', 'st': 'doc', 'f': ['TÁŽ OSOBA jako 65']}")
        self.export()
        anna = self.site()["people"][self.site()["aliases"]["71"]]
        self.assertFalse(any(f.startswith("TÁŽ OSOBA") for f in anna["facts"]))

    def test_snatek_dolozeny_jen_kde_je(self):
        # #30: web psal „Manželka/Manžel“ i u nesezdaných rodičů – teď jen u doloženého sňatku (families.married)
        self.set_same({}, "P[1]['n'] = 'Petr Novák'\nP[3]['f'] = ['* 1955 Chrudim']\nP[2]['f'] = ['* 1952 Holice']")
        self.export()
        site = self.site()
        fam = lambda k: site["families"][site["people"][next(s for s, p in site["people"].items() if p["k"] == k)]["family"]]
        self.assertFalse(fam(1)["married"])   # rodiče výchozí osoby: bez × i „provd.“
        self.assertTrue(fam(4)["married"])    # × 1948 Holice

    def test_otevreny_web_ma_v_nginx_jediny_default(self):
        # #61: "otevreny": true → dřív dva řádky default v map a nginx nenastartoval
        cfg = json.loads(self.web)
        cfg["prihlaseni"] = {"otevreny": True}
        (self.proj / "data" / "web.json").write_text(json.dumps(cfg, ensure_ascii=False), encoding="utf-8")
        self.export()
        nginx = (self.proj / "web" / "nginx.conf").read_text(encoding="utf-8")
        mapa = re.search(r"map \$cookie_rodokmen \$rodokmen_ok \{(.*?)\}", nginx, re.S).group(1)
        self.assertEqual(re.findall(r"^\s*default\s+(\d);", mapa, re.M), ["1"])

    def test_dokumenty_na_strance_pribehu(self):
        # #61: stránka příběhu ukazovala všechny dokumenty, i cizích rodů
        shutil.copy(self.proj / "vyrezy" / next(p.name for p in (self.proj / "vyrezy").glob("*.jpg")),
                    self.proj / "vyrezy" / "test_dokument.jpg")
        docs = [dict(img="test_dokument", popis="rod 8", osoby=[16]),
                dict(img="test_dokument", popis="rod 12", osoby=[24]),
                dict(img="test_dokument", popis="všude", osoby=[24], pribeh=True),
                dict(img="test_dokument", popis="nikde", osoby=[16], pribeh=False)]
        (self.proj / "data" / "dokumenty.json").write_text(json.dumps(docs, ensure_ascii=False), encoding="utf-8")
        cfg = json.loads(self.web)
        cfg.setdefault("pribeh", {})["rod"] = 8
        (self.proj / "data" / "web.json").write_text(json.dumps(cfg, ensure_ascii=False), encoding="utf-8")
        self.export()
        shown = {d["caption"]: d["stories"] for d in self.site()["docs"]}
        self.assertEqual(shown, {"rod 8": [""], "rod 12": [], "všude": [""], "nikde": []})
        del cfg["pribeh"]["rod"]   # jediný příběh bez rodu ukáže všechno kromě pribeh: false (jako dřív)
        (self.proj / "data" / "web.json").write_text(json.dumps(cfg, ensure_ascii=False), encoding="utf-8")
        self.export()
        shown = {d["caption"]: d["stories"] for d in self.site()["docs"]}
        self.assertEqual(shown, {"rod 8": [""], "rod 12": [""], "všude": [""], "nikde": []})


if __name__ == "__main__":
    unittest.main()
