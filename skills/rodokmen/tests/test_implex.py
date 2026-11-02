import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from implex import puvod, zrcadla  # noqa: E402

# malý rodokmen (jen čísla); v testech je osoba 5 zároveň na místě 7 (SAME = {7: 5})
P = {1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}, 10: {}, 11: {}, 21: {}}


class ImplexTests(unittest.TestCase):
    def test_bez_same_jen_vlastni_osoby(self):
        self.assertEqual(puvod(10, P, {}), 10)
        self.assertIsNone(puvod(14, P, {}))
        self.assertEqual(zrcadla(P, {}), {})

    def test_alias_bez_polozky_v_p_ukaze_hlavni_osobu_i_predky(self):
        same = {7: 5}
        self.assertEqual(puvod(7, P, same), 5)
        self.assertEqual(puvod(14, P, same), 10)
        self.assertEqual(puvod(15, P, same), 11)
        self.assertEqual(puvod(29, P, same), 21)   # 21 = matka 10, na místě aliasu tedy 29 = matka 14
        self.assertIsNone(puvod(31, P, same))
        self.assertEqual(zrcadla(P, same), {7: 5, 14: 10, 15: 11, 29: 21})

    def test_alias_s_polozkou_v_p_bere_udaje_z_hlavniho_cisla(self):
        p = {**P, 7: {"f": ["TÁŽ OSOBA jako 5"]}}
        self.assertEqual(puvod(7, p, {7: 5}), 5)

    def test_vyslovne_zapsany_predek_nad_aliasem_ma_prednost(self):
        p = {**P, 14: {}}
        self.assertEqual(puvod(14, p, {7: 5}), 14)
        self.assertNotIn(14, zrcadla(p, {7: 5}))
        self.assertEqual(zrcadla(p, {7: 5})[15], 11)

    def test_omezeni_generaci(self):
        self.assertEqual(zrcadla(P, {7: 5}, max_gen=3), {7: 5, 14: 10, 15: 11})

    def test_chybna_smycka_skonci(self):
        self.assertIsNone(puvod(3, {1: {}, 2: {}}, {3: 7, 7: 3}))
        self.assertEqual(zrcadla({1: {}, 2: {}}, {3: 7, 7: 3}), {})


if __name__ == "__main__":
    unittest.main()
