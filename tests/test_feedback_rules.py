import unittest

import pandas as pd

from src.analysis.agronomiske_advarsler import generer_advarsler
from src.analysis.beregningsgrundlag import beregn_kalkbehov
from src.analysis.seges_normer import MGT_KLASSER, klassificer_naering
from src.parsers.soiloptix_parser import SoilOptixParser


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

    def test_kalkmodel_does_not_explode_for_small_rt_lift(self):
        result = beregn_kalkbehov(maalt_rt=6.0, ler_pct=10.0, humus_pct=3.0)

        self.assertEqual(result["status"], "bagatel")
        self.assertEqual(result["kalk_ton_per_ha"], 0.0)
        self.assertLess(result["beregnet_kalk_ton_per_ha"], 2.0)

    def test_kalkmodel_caps_large_amount_for_screening(self):
        result = beregn_kalkbehov(maalt_rt=6.0, ler_pct=20.0, humus_pct=2.0)

        self.assertEqual(result["status"], "behov")
        self.assertLessEqual(result["kalk_ton_per_ha"], 3.0)

    def test_out_of_range_classification_returns_none(self):
        self.assertIsNone(klassificer_naering(-1, MGT_KLASSER))
        self.assertEqual(klassificer_naering(4.0, MGT_KLASSER), "Lavt")
        self.assertEqual(klassificer_naering(4.05, MGT_KLASSER), "Middel")

    def test_soiloptix_parser_reads_area_metadata_when_present(self):
        df = pd.DataFrame([[None for _ in range(5)] for _ in range(23)])
        df.iloc[2, 1] = "450610"
        df.iloc[5, 3] = "Ordrenummer"
        df.iloc[5, 4] = 1178045
        df.iloc[6, 4] = 711922
        df.iloc[7, 4] = 21584940
        df.iloc[8, 4] = "bb9901eb"
        df.iloc[9, 4] = "6-0"
        df.iloc[4, 3] = "Areal (ha)"
        df.iloc[4, 4] = "12,4"

        for offset, param in enumerate(SoilOptixParser.PARAMETERS):
            df.iloc[SoilOptixParser.ROW_DATA_START + offset, 0] = param
            df.iloc[SoilOptixParser.ROW_DATA_START + offset, 4] = 1

        parser = SoilOptixParser("dummy.xlsx")
        parser.df = df

        sample = parser.parse()[0]
        self.assertEqual(sample["metadata"]["areal_ha"], 12.4)


if __name__ == "__main__":
    unittest.main()
