import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

GED_IMPORT = Path(__file__).resolve().parents[1] / "tools" / "ged_import.py"


class GedImportRootSelectionTests(unittest.TestCase):
    def test_selects_duplicate_name_by_gedcom_id(self):
        gedcom = """0 HEAD
1 CHAR UTF-8
0 @I1@ INDI
1 NAME Same /Name/
1 BIRT
2 DATE 1 JAN 1900
0 @I2@ INDI
1 NAME Same /Name/
1 BIRT
2 DATE 1 JAN 1950
0 TRLR
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "tree.ged"
            path.write_text(gedcom, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(GED_IMPORT), str(path), "@I2@"],
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
        self.assertIn("1 | Same Name | * 1950", result.stdout)
        self.assertNotIn("* 1900", result.stdout)


def ged(data, *args):
    """Spustí ged_import.py na GEDCOM v bajtech, vrátí (stdout, stderr)."""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "tree.ged"
        path.write_bytes(data)
        r = subprocess.run([sys.executable, "-X", "utf8", str(GED_IMPORT), str(path), *args], capture_output=True,
                           text=True, encoding="utf-8", timeout=20)
    return r.stdout, r.stderr


class GedImportRobustnessTests(unittest.TestCase):
    def test_kruh_ve_stromu_skonci(self):   # #25: osoba vlastním předkem – dřív nekonečná smyčka
        data = b"""0 HEAD
0 @I1@ INDI
1 NAME Syn /A/
1 FAMC @F1@
0 @I2@ INDI
1 NAME Otec /A/
1 FAMS @F1@
1 FAMC @F2@
0 @F1@ FAM
1 HUSB @I2@
1 CHIL @I1@
0 @F2@ FAM
1 HUSB @I1@
1 CHIL @I2@
0 TRLR
"""
        out, err = ged(data, "@I1@")
        self.assertIn("2 | Otec A", out)
        self.assertIn("vlastním předkem", err)

    def test_myheritage_conc_v_pulce_znaku_a_hole_radky(self):
        jmeno = "Žofie".encode("utf-8")   # Ž = 2 bajty, rozseknuté mezi NOTE a CONC
        data = (b"0 HEAD\n0 @I1@ INDI\n1 NAME Anna /B/\n1 NOTE Babi&ccaron;ka " + jmeno[:1] + b"\n2 CONC " + jmeno[1:]
                + b" z Prahy\nholy radek bez cisla\n1 SOUR @S1@\n2 PAGE str. 42\n0 @S1@ SOUR\n1 TITL Strom X\n"
                b"1 AUTH Petr\n0 TRLR\n")
        out, _ = ged(data, "@I1@")
        self.assertIn("Babička Žofie z Prahy", out)
        self.assertIn("holy radek bez cisla", out)
        self.assertIn("zdroj: Strom X (Petr), str. 42", out)
        self.assertNotIn("�", out)

    def test_adopce_ma_prednost_vlastni_rodina_a_deti_dvou_rodicu(self):
        data = b"""0 HEAD
0 @I1@ INDI
1 NAME Dite /C/
1 FAMC @F9@
2 PEDI adopted
1 FAMC @F1@
0 @I2@ INDI
1 NAME Vlastni /C/
1 BIRT
2 DATE BEF 1861
0 @I3@ INDI
1 NAME Adoptivni /D/
0 @I4@ INDI
1 NAME Matka /E/
0 @F1@ FAM
1 HUSB @I2@
1 CHIL @I1@
0 @F9@ FAM
1 HUSB @I3@
1 CHIL @I1@
0 TRLR
"""
        out, err = ged(data, "@I1@")
        self.assertIn("2 | Vlastni C | * před 1861", out)
        self.assertIn("víc rodin rodičů", err)
        out, _ = ged(data, "@I2@", "@I4@", "--deti", "--osoby")
        self.assertIn(" 2: dict(n='Vlastni C'", out)
        self.assertIn(" 3: dict(n='Matka E'", out)


if __name__ == "__main__":
    unittest.main()
