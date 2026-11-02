"""kontrola.py a export_web.py na malém syntetickém projektu (bez sítě, #25, #37, #50, #54)."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / "tools"))
import kontrola  # noqa: E402
from export_web import years  # noqa: E402
from obraz import najdi_magick  # noqa: E402

OSOBY = '''
P = {
 1: dict(n="Jan-3", y="* 1990", st="fam", f=["* 1990 Holice"], r=[]),
 2: dict(n="Jan", y="1950–2010", st="doc", f=["* 1950 Holice"], r=["krest_a"]),
 3: dict(n="Jan", y="1952–2015", st="fam", f=[], r=[]),
 4: dict(n="Petr Novák", y="1920–1990", st="fam", f=["* 1920 Holice"], r=[]),
 5: dict(n="Anna", y="1925–2000", st="fam", f=[], r=[]),
 8: dict(n="Karel Novák", y="1890–1960", st="fam", f=[], r=[]),
 9: dict(n="Marie Nováková", y="1895–1970", st="fam", f=[], r=[]),
}
LINES = {8: ("Novákové", "první"), 9: ("Novákové", "druhý")}
SAME = {SAME_PLACEHOLDER}
ISSUES = [
 ("Dvojice", "Otevřené: dvojice"),
 dict(otazka="Odkud byl Petr?", stav="Otevřené: hledáme", osoby=[4], prosle=[1]),
]
'''


def projekt(tmp, same="", zaznamy=None, web=None, mista=None):
    root = Path(tmp)
    (root / "data").mkdir()
    (root / "data" / "osoby.py").write_text(OSOBY.replace("{SAME_PLACEHOLDER}", "{" + same + "}"), encoding="utf-8")
    (root / "data" / "zaznamy.json").write_text(json.dumps(zaznamy if zaznamy is not None else [
        dict(klic="krest_a", druh="N", datum="1. 2. 1950", nazev="Křest", shrnuti="Křest Jana", svazek="sv1")]),
        encoding="utf-8")
    (root / "data" / "svazky.json").write_text(json.dumps({"sv1": {"archiv": "Rodinný archiv", "svazek": "doklady"}}),
                                               encoding="utf-8")
    (root / "data" / "web.json").write_text(json.dumps(web or {"nazev": "Rodokmen Novákových", "kontakt": {"jmeno": "Petrovi"}}),
                                            encoding="utf-8")
    (root / "data" / "mista.json").write_text(json.dumps(mista if mista is not None else {}), encoding="utf-8")
    (root / "data" / "research_log.md").write_text(
        "| # | datum | zdroj | rozsah | hledáno | výsledek | citace |\n|---|---|---|---|---|---|---|\n"
        "| 1 | 2026-01-01 | ARON | sn. 1–9 | Petr | NENALEZENO | — |\n", encoding="utf-8")
    shutil.copytree(SKILL / "tools", root / "tools")
    return root


def spust(root, nastroj, *args):
    r = subprocess.run([sys.executable, "-I", "-X", "utf8", str(root / "tools" / nastroj), *args],
                       capture_output=True, text=True, encoding="utf-8", cwd=root)
    return r.returncode, r.stdout + r.stderr


class KontrolaTests(unittest.TestCase):
    def test_skutecni_novakovi_nejsou_ukazka(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, out = spust(projekt(tmp), "kontrola.py")
        self.assertNotIn("ukázkové texty", out)

    def test_ukazkova_rodina_se_hlasi(self):
        web = json.loads((SKILL / "template" / "ukazka" / "web.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as tmp:
            _, out = spust(projekt(tmp, web=web), "kontrola.py")
        self.assertIn("ukázkové texty", out)

    def test_rodinny_doklad_bez_odkazu_neni_chyba(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, out = spust(projekt(tmp), "kontrola.py")
        self.assertNotIn("chybí odkaz", out)
        zaz = [dict(klic="krest_a", druh="N", datum="1. 2. 1950", nazev="Křest", shrnuti="x")]
        with tempfile.TemporaryDirectory() as tmp:
            _, out = spust(projekt(tmp, zaznamy=zaz), "kontrola.py")
        self.assertIn("chybí odkaz", out)

    def test_prazdna_mista_varuji(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, out = spust(projekt(tmp), "kontrola.py")
        self.assertIn("mista.json je prázdný", out)
        with tempfile.TemporaryDirectory() as tmp:
            _, out = spust(projekt(tmp, mista={"Holice": {"lat": 50, "lon": 16}}), "kontrola.py")
        self.assertNotIn("mista.json je prázdný", out)
        self.assertNotIn("není na mapě", out)

    def test_same_kruh_a_retez_jsou_chyba(self):
        with tempfile.TemporaryDirectory() as tmp:
            kod, out = spust(projekt(tmp, same="4: 5, 5: 4"), "kontrola.py")
        self.assertEqual(kod, 1)
        self.assertIn("je sám alias", out)

    def test_issues_dict_a_spatny_radek_deniku(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = projekt(tmp)
            text = (root / "data" / "osoby.py").read_text(encoding="utf-8").replace("prosle=[1]", "prosle=[1, 7]")
            (root / "data" / "osoby.py").write_text(text, encoding="utf-8")
            kod, out = spust(root, "kontrola.py")
        self.assertEqual(kod, 1)
        self.assertIn("řádek deníku 7", out)
        self.assertNotIn("řádek deníku 1 ", out)

    def test_nebezpecny_klic_a_datum(self):
        zaz = [dict(klic="../ven", druh="N", datum="31. 2. 1900", nazev="x", shrnuti="x", svazek="sv1")]
        with tempfile.TemporaryDirectory() as tmp:
            kod, out = spust(projekt(tmp, zaznamy=zaz), "kontrola.py")
        self.assertEqual(kod, 1)
        self.assertIn("klíč smí mít jen", out)
        self.assertIn("neexistuje v kalendáři", out)

    def test_platne_datum(self):
        self.assertTrue(kontrola.platne_datum("asi 1850"))
        self.assertTrue(kontrola.platne_datum("29. 2. 1904"))
        self.assertFalse(kontrola.platne_datum("29. 2. 1900"))


class ZapisSmazatTests(unittest.TestCase):
    def test_smazat_zapis_i_obrazky_ostatni_beze_zmeny(self):   # #54
        with tempfile.TemporaryDirectory() as tmp:
            zaz = [dict(klic="a", druh="N", datum="1850", nazev="A", shrnuti="a"),
                   dict(klic="cizi", druh="N", datum="1851", nazev="B", shrnuti="b"),
                   dict(klic="c", druh="N", datum="1852", nazev="C", shrnuti="c")]
            root = projekt(tmp, zaznamy=zaz)
            (root / "data" / "zaznamy.json").write_text(json.dumps(zaz, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
            prep = '{\n "cizi": {"orig": "x", "cs": "y"}\n}\n'
            (root / "data" / "prepisy.json").write_text(prep, encoding="utf-8")
            (root / "data" / "zvyrazneni.json").write_text('{\n "a": {"boxes": []},\n "cizi": {"boxes": []}\n}\n', encoding="utf-8")
            for d in ("vyrezy", "zdroje"):
                (root / d).mkdir()
                (root / d / "cizi.jpg").write_bytes(b"x")
            kod, out = spust(root, "zapis.py", "smazat", "cizi")
            self.assertEqual(kod, 0, out)
            self.assertIn("Nic nesmazáno", out)
            self.assertTrue((root / "vyrezy" / "cizi.jpg").exists())
            kod, out = spust(root, "zapis.py", "smazat", "cizi", "--ano")
            self.assertEqual(kod, 0, out)
            self.assertEqual([z["klic"] for z in json.loads((root / "data" / "zaznamy.json").read_text(encoding="utf-8"))],
                             ["a", "c"])
            self.assertEqual((root / "data" / "zaznamy.json").read_text(encoding="utf-8"),
                             json.dumps([zaz[0], zaz[2]], ensure_ascii=False, indent=1) + "\n")
            self.assertEqual((root / "data" / "prepisy.json").read_text(encoding="utf-8"), "{}\n")
            self.assertEqual((root / "data" / "zvyrazneni.json").read_text(encoding="utf-8"), '{\n "a": {"boxes": []}\n}\n')
            self.assertFalse((root / "vyrezy" / "cizi.jpg").exists())
            self.assertFalse((root / "zdroje" / "cizi.jpg").exists())


@unittest.skipUnless(najdi_magick(), "export_web potřebuje ImageMagick jen na rámečky; fan_chart ho nepotřebuje")
class ExportWebTests(unittest.TestCase):
    def export(self, same=""):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp, True)
        root = projekt(tmp, same=same)
        shutil.copytree(SKILL / "template" / "web", root / "web", ignore=shutil.ignore_patterns("node_modules"))
        (root / "web" / "public" / "img").mkdir(parents=True, exist_ok=True)
        (root / "web" / "public" / "img" / "smazany.jpg").write_bytes(b"x")
        kod, out = spust(root, "export_web.py")
        self.assertEqual(kod, 0, out)
        site = json.loads((root / "web" / "src" / "data" / "site.json").read_text(encoding="utf-8"))
        return root, site

    def test_kolize_adres_osob_a_rodu(self):
        root, site = self.export()
        self.assertEqual(len({p["k"] for p in site["people"].values()}), 7)   # nikdo nepřepsán (Jan-3, Jan, Jan)
        self.assertEqual(site["people"][site["root"]]["k"], 1)
        self.assertEqual(sorted(l["k"] for l in site["lines"].values()), [8, 9])   # dva rody „Novákové“
        self.assertFalse((root / "web" / "public" / "img" / "smazany.jpg").exists())

    def test_alias_bez_vlastni_polozky_a_issues_dict(self):
        _, site = self.export(same="6: 4")
        petr = next(p for p in site["people"].values() if p["k"] == 4)
        self.assertEqual([a["k"] for a in petr["also"]], [6])
        otazka = site["issues"][1]
        self.assertEqual(otazka["title"], "Odkud byl Petr?")
        self.assertEqual(otazka["people"], [petr["slug"]])
        self.assertEqual(otazka["checked"][0]["result"], "NENALEZENO")

    def test_years_pred(self):
        self.assertEqual(years("před 1740"), "před 1740")
        self.assertEqual(years("1680 – před 1740"), "1680–?")


if __name__ == "__main__":
    unittest.main()
