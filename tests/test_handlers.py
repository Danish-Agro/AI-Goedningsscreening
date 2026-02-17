import unittest

from src.ai.assistant import handle_max_nutrient, handle_most_needed, sanitize_output


class HandlerTests(unittest.TestCase):
    def test_max_kalium_finds_highest_value(self):
        records = [
            {
                "metadata": {"field_id": "A", "marknummer": "1"},
                "measurements": {"kalium_mg_100g": 3.5},
                "categories": {"kalium": "Small Demand"},
            },
            {
                "metadata": {"field_id": "B", "marknummer": "2"},
                "measurements": {"kalium_mg_100g": 5.2},
                "categories": {"kalium": "OK"},
            },
        ]
        result = handle_max_nutrient(records, "kalium")
        self.assertEqual(result["field_id"], "B")
        self.assertEqual(result["value"], 5.2)

    def test_most_needed_fosfor_uses_rank_and_tiebreaker(self):
        records = [
            {
                "metadata": {"field_id": "A", "marknummer": "1"},
                "measurements": {"fosfor_mg_100g": 2.0},
                "categories": {"fosfor": "Medium Demand"},
            },
            {
                "metadata": {"field_id": "B", "marknummer": "2"},
                "measurements": {"fosfor_mg_100g": 1.2},
                "categories": {"fosfor": "Medium Demand"},
            },
            {
                "metadata": {"field_id": "C", "marknummer": "3"},
                "measurements": {"fosfor_mg_100g": 0.8},
                "categories": {"fosfor": "Small Demand"},
            },
        ]
        result = handle_most_needed(records, "fosfor")
        self.assertEqual(result["field_id"], "B")

    def test_sanitize_output_blocks_law_and_kg_ha(self):
        blocked = sanitize_output("Ifølge lovgivning anbefales 30 kg/ha.")
        self.assertIn("ikke en del af denne POC", blocked)


if __name__ == "__main__":
    unittest.main()
