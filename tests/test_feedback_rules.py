import unittest

from src.analysis.agronomiske_advarsler import generer_advarsler
from src.analysis.beregningsgrundlag import beregn_kalkbehov
from src.analysis.seges_normer import MGT_KLASSER, klassificer_naering


class FeedbackRuleTests(unittest.TestCase):
    def test_cut_and_bt_zero_do_not_trigger_advarsler(self):
        result = generer_advarsler(
            mark_nr="99-0b",
            cut=0,
            bt=0,
            rt=6.8,
            jb_nr=4,
            organisk_stof_pct=3.79,
        )

        self.assertEqual(result.advarsler, [])

    def test_kobber_comment_uses_jb4_and_no_exact_organic_matter_value(self):
        result = generer_advarsler(
            mark_nr="99-0b",
            cut=0.7,
            rt=6.8,
            jb_nr=4,
            organisk_stof_pct=3.79,
        )

        text = result.til_prompt_tekst()
        self.assertIn("JB4 og nedefter", text)
        self.assertNotIn("3.79", text)
        self.assertNotIn("3,79", text)

    def test_kalkmodel_caps_clay_at_30_percent(self):
        capped = beregn_kalkbehov(maalt_rt=5.8, ler_pct=60.0, humus_pct=2.0)
        at_limit = beregn_kalkbehov(maalt_rt=5.8, ler_pct=30.0, humus_pct=2.0)

        self.assertTrue(capped["ler_pct_begraenset"])
        self.assertEqual(capped["ler_pct_anvendt"], 30.0)
        self.assertEqual(capped["oensket_rt"], at_limit["oensket_rt"])
        self.assertEqual(capped["kalk_ton_per_ha"], at_limit["kalk_ton_per_ha"])

    def test_kalkmodel_ignores_tiny_rt_difference(self):
        result = beregn_kalkbehov(maalt_rt=5.9, ler_pct=6.0, humus_pct=3.79)

        self.assertEqual(result["status"], "intet_behov")
        self.assertEqual(result["kalk_ton_per_ha"], 0.0)
        self.assertLess(result["rt_difference"], 0.1)

    def test_out_of_range_classification_returns_none(self):
        self.assertIsNone(klassificer_naering(-1, MGT_KLASSER))
        self.assertEqual(klassificer_naering(4.0, MGT_KLASSER), "Lavt")
        self.assertEqual(klassificer_naering(4.05, MGT_KLASSER), "Middel")


if __name__ == "__main__":
    unittest.main()
