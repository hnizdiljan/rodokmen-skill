"""mza.py bez sítě: sdílená cache snímků, výřez z cache a hlášení odmítnutí archivu brzdě (tools/slusne.py)."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import cache  # noqa: E402
import mza  # noqa: E402
import obraz  # noqa: E402
import slusne  # noqa: E402

HAS_IMAGEMAGICK = bool(obraz.najdi_magick())


def rozmer(path):
    r = subprocess.run([obraz.magick(), path, "-format", "%wx%h", "info:"], check=True, capture_output=True, text=True)
    return r.stdout


@unittest.skipUnless(HAS_IMAGEMAGICK, "ImageMagick is required")
class SnimekCacheTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.koren = mock.patch.object(cache, "KOREN", os.path.join(self.tmp, "cache"))
        self.koren.start()
        self.stazeno = []

        def stahni(dzi, out, nahled=False, orez=None):
            self.stazeno.append((dzi, nahled, orez))
            subprocess.run([obraz.magick(), "-size", "200x100", "xc:white", out], check=True)

        self.patche = [mock.patch.object(mza, "stahni", stahni),
                       mock.patch.object(mza, "snimky", lambda bid: (["https://www.mza.cz/iipsrv/a.dzi"], ["obr_0001"]))]
        for p in self.patche:
            p.start()

    def tearDown(self):
        for p in self.patche:
            p.stop()
        self.koren.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_cely_snimek_se_stahne_jen_jednou(self):
        out = os.path.join(self.tmp, "pracovni", "a.jpg")
        with redirect_stdout(StringIO()):
            mza.snimek("123", "1", out)
            mza.snimek("123", "1", out)
        self.assertEqual(len(self.stazeno), 1)
        self.assertTrue(os.path.exists(cache.cesta("mza/123/sn0001-u0.jpg")))
        self.assertEqual(rozmer(out), "200x100")

    def test_vyrez_z_cache_bez_stahovani(self):
        with redirect_stdout(StringIO()):
            mza.snimek("123", "1", os.path.join(self.tmp, "cely.jpg"))
            vystup = StringIO()
            with redirect_stdout(vystup):
                mza.snimek("123", "1", os.path.join(self.tmp, "vyrez.jpg"), orez=[0.5, 0.0, 1.0, 0.5])
        self.assertEqual(len(self.stazeno), 1)
        self.assertIn("z cache", vystup.getvalue())
        self.assertEqual(rozmer(os.path.join(self.tmp, "vyrez.jpg")), "100x50")

    def test_vyrez_bez_cache_stahne_jen_vyrez_a_neulozi_ho(self):
        with redirect_stdout(StringIO()):
            mza.snimek("123", "1", os.path.join(self.tmp, "vyrez.jpg"), nahled=True, orez=[0.0, 0.0, 0.5, 0.5])
        self.assertEqual(self.stazeno, [("https://www.mza.cz/iipsrv/a.dzi", True, [0.0, 0.0, 0.5, 0.5])])
        self.assertFalse(os.path.exists(cache.cesta("mza/123/sn0001-u2.jpg")))


class CurlBrzdaTests(unittest.TestCase):
    def test_429_zastavi_web_a_nic_neopakuje(self):
        odpoved = subprocess.CompletedProcess([], 0, stdout=b"Too many429", stderr=b"")
        with mock.patch.object(mza.subprocess, "run", return_value=odpoved) as run, \
                mock.patch.object(slusne, "zastav", side_effect=slusne.Zastaveno(slusne.KOD)) as zastav:
            with self.assertRaises(slusne.Zastaveno):
                mza.curl_get("https://www.mza.cz/iipsrv/a_files/12/0_0.jpg")
        self.assertEqual(run.call_count, 1)
        zastav.assert_called_once_with("www.mza.cz", "HTTP 429")

    def test_zastaveny_web_v_brzde_se_neopakuje(self):
        odpoved = subprocess.CompletedProcess([], slusne.KOD, stdout=b"", stderr=b"slusne: www.mza.cz je zastaveny")
        with mock.patch.object(mza.subprocess, "run", return_value=odpoved) as run:
            with self.assertRaises(slusne.Zastaveno):
                mza.curl_get("https://www.mza.cz/iipsrv/a_files/12/0_0.jpg")
        self.assertEqual(run.call_count, 1)

    def test_neplatne_id_knihy_nejde_do_cesty_cache(self):
        with self.assertRaises(SystemExit):
            mza.snimky("../x")


if __name__ == "__main__":
    unittest.main()
