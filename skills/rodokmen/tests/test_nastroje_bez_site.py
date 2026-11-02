"""Nástroje, které jinak jdou na síť – tady jen jejich logika bez sítě (#12, #21, #25, #37, #54, #63)."""
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import aron_img  # noqa: E402
import cache  # noqa: E402
import hlavicky  # noqa: E402
import kramerius  # noqa: E402
import obraz  # noqa: E402
import overit  # noqa: E402
import policie_prihlasky  # noqa: E402
import slusne  # noqa: E402
import trebon  # noqa: E402

MAGICK = obraz.najdi_magick()


def rozmer(path):
    return subprocess.run([MAGICK, path, "-format", "%wx%h", "info:"], capture_output=True, text=True).stdout


class ParsovaniTests(unittest.TestCase):
    def test_hlavicky_snimky(self):
        self.assertEqual(hlavicky.snimky("1-5,40,80-120:20,3"), [1, 2, 3, 4, 5, 40, 80, 100, 120])
        with self.assertRaises(SystemExit):
            hlavicky.snimky("1-100")   # víc než 40 najednou
        with self.assertRaises(SystemExit):
            hlavicky.snimky("5-1")
        with self.assertRaises(SystemExit):
            hlavicky.oblast("0,0,1200,300")   # pixely

    def test_overit_poloviny_prekryv_8_procent_oblasti(self):
        a, b = overit.poloviny((0.2, 0.0, 0.6, 1.0), "h")
        self.assertAlmostEqual(a[2] - b[0], 0.4 * 0.08)
        a, b = overit.poloviny((0.0, 0.5, 1.0, 0.6), "v")
        self.assertAlmostEqual(a[3] - b[1], 0.1 * 0.08)
        self.assertEqual((a[1], b[3]), (0.5, 0.6))

    def test_retry_after(self):
        self.assertEqual(slusne.retry_after("120"), 120)
        self.assertEqual(slusne.retry_after(""), 0)
        self.assertEqual(slusne.retry_after("nesmysl"), 0)
        self.assertEqual(slusne.retry_after("999999"), slusne.OKNO)
        self.assertEqual(slusne.retry_after("Wed, 21 Oct 2015 07:28:00 GMT", ted=1445412480 - 600), 600)

    def test_kramerius_text_ocr_utf16(self):
        self.assertEqual(kramerius.dekoduj("Hnízdil".encode("utf-16")), "Hnízdil")
        self.assertEqual(kramerius.dekoduj("Hnízdil".encode("utf-8")), "Hnízdil")
        with self.assertRaises(SystemExit):
            kramerius.text("https://kramerius5.nkp.cz", "../etc")

    def test_kramerius_neverejna_stranka_se_nestahuje(self):
        with mock.patch.object(kramerius, "stahni", return_value=b'{"policy": "private"}') as st:
            with self.assertRaises(SystemExit) as e:
                kramerius.text("https://kramerius5.nkp.cz", "uuid:" + "0" * 8 + "-0000-0000-0000-" + "0" * 12)
        self.assertIn("není veřejná", str(e.exception))
        self.assertEqual(st.call_count, 1)   # TEXT_OCR se už nežádá

    def test_policie_radky_a_strana(self):
        h = ('<td class="table_prijmeni"><a href="?session=ab&amp;action=image&amp;record=21">Novák</a></td>\n'
             '   <td class="table_jmeno">Jan</td>\n   <td class="table_rok">1865</td>')
        self.assertEqual(policie_prihlasky.radky(h), {21: ("Novák", "Jan", "1865")})
        with mock.patch.object(policie_prihlasky, "get", return_value=h) as g:
            policie_prihlasky.strana("ab", 21)
        self.assertIn("action=list&od=20", g.call_args[0][0])


class TrebonKonecKnihyTests(unittest.TestCase):
    def test_stejny_snimek_jako_predchozi(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(cache, "KOREN", tmp):
            for n, obsah in ((1, b"a"), (2, b"b"), (3, b"b")):
                p = cache.cesta(f"trebon/99/sn{n:04d}.jpg")
                os.makedirs(os.path.dirname(p), exist_ok=True)
                Path(p).write_bytes(obsah)
            self.assertFalse(trebon.za_koncem("99", 2))
            self.assertTrue(trebon.za_koncem("99", 3))
            self.assertFalse(trebon.za_koncem("99", 4))


@unittest.skipUnless(MAGICK, "potřebuje ImageMagick")
class ObrazkoveTests(unittest.TestCase):
    def test_aron_vyrez_presne_ne_po_dlazdicich(self):   # #25: 0.1–0.2 z 300×200 = 30×20, ne celá dlaždice 128×128
        with tempfile.TemporaryDirectory() as tmp:
            stranka = os.path.join(tmp, "stranka.png")
            subprocess.run([MAGICK, "-size", "300x200", "gradient:", stranka], check=True)
            dzi = ('<?xml version="1.0"?><Image xmlns="http://schemas.microsoft.com/deepzoom/2009" TileSize="128" '
                   'Overlap="0" Format="jpg"><Size Width="300" Height="200"/></Image>')

            def get(url, binary=False, tries=4):
                if url.endswith(".dzi"):
                    return dzi
                c, r = map(int, url.rsplit("/", 1)[1][:-4].split("_"))
                t = os.path.join(tmp, f"t{c}_{r}.jpg")
                subprocess.run([MAGICK, stranka, "-crop", f"128x128+{c * 128}+{r * 128}", "+repage", t], check=True)
                return Path(t).read_bytes()
            out = os.path.join(tmp, "vyrez.jpg")
            with mock.patch.object(aron_img, "get", side_effect=get):
                aron_img.fetch_image("https://x/a.dzi", 0, out, (0.1, 0.1, 0.2, 0.2))
            self.assertEqual(rozmer(out), "30x20")
            with mock.patch.object(aron_img, "get", side_effect=get):
                aron_img.fetch_image("https://x/a.dzi", 0, out)
            self.assertEqual(rozmer(out), "300x200")

    def test_hlavicky_ze_souboru(self):
        with tempfile.TemporaryDirectory() as tmp:
            for n in (1, 2, 3):
                subprocess.run([MAGICK, "-size", "400x600", "xc:white", os.path.join(tmp, f"s{n}.png")], check=True)
            out = os.path.join(tmp, "prehled.jpg")
            with redirect_stdout(StringIO()) as o, redirect_stderr(StringIO()):
                hlavicky.main(["soubory", os.path.join(tmp, "s{n}.png"), "1-4", out, "--po", "2", "--oblast", "0,0,1,0.1"])
            self.assertTrue(os.path.exists(os.path.join(tmp, "prehled_1.jpg")))
            self.assertTrue(os.path.exists(os.path.join(tmp, "prehled_2.jpg")))
            self.assertIn("Chybí 1 snímků", o.getvalue())   # snímek 4 neexistuje

    def test_overit_nezvetsuje_dlouhy_vyrez(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = os.path.join(tmp, "dlouhy.png")
            subprocess.run([MAGICK, "-size", "600x2400", "xc:white", src], check=True)
            pre = os.path.join(tmp, "ov")
            r = subprocess.run([sys.executable, "-I", "-X", "utf8", overit.__file__, src, "0,0,1,1", pre, "v"],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(rozmer(pre + "_0.jpg"), "600x1296")
            r = subprocess.run([sys.executable, "-I", "-X", "utf8", overit.__file__, os.path.join(tmp, "neni.png"),
                                "0,0,1,1", pre], capture_output=True, text=True)
            self.assertNotEqual(r.returncode, 0)


if __name__ == "__main__":
    unittest.main()
