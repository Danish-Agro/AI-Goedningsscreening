import unittest

from src.ai.assistant import get_most_needed, has_any_demand


class RankingTests(unittest.TestCase):
    def test_fosfor_prefers_higher_need_category(self):
        records = [
            {
                "metadata": {"field_id": "A", "marknummer": "1"},
                "categories": {"fosfor": "OK"},
                "measurements": {"fosfor_mg_100g": 1.0},
            },
            {
                "metadata": {"field_id": "B", "marknummer": "2"},
                "categories": {"fosfor": "Large Demand"},
                "measurements": {"fosfor_mg_100g": 4.0},
            },
        ]
        winner = get_most_needed(records, "fosfor")
        self.assertIsNotNone(winner)
        self.assertEqual(winner["metadata"]["field_id"], "B")

    def test_fosfor_tiebreaker_uses_lowest_measurement(self):
        records = [
            {
                "metadata": {"field_id": "A", "marknummer": "1"},
                "categories": {"fosfor": "Medium Demand"},
                "measurements": {"fosfor_mg_100g": 1.8},
            },
            {
                "metadata": {"field_id": "B", "marknummer": "2"},
                "categories": {"fosfor": "Medium Demand"},
                "measurements": {"fosfor_mg_100g": 1.2},
            },
        ]
        winner = get_most_needed(records, "fosfor")
        self.assertIsNotNone(winner)
        self.assertEqual(winner["metadata"]["field_id"], "B")

    def test_missing_category_or_measurement_is_ignored(self):
        records = [
            {
                "metadata": {"field_id": "A", "marknummer": "1"},
                "categories": {},
                "measurements": {"fosfor_mg_100g": 1.0},
            },
            {
                "metadata": {"field_id": "B", "marknummer": "2"},
                "categories": {"fosfor": "Small Demand"},
                "measurements": {"fosfor_mg_100g": 2.0},
            },
            {
                "metadata": {"field_id": "C", "marknummer": "3"},
                "categories": {"fosfor": "Large Demand"},
                "measurements": {},
            },
        ]
        winner = get_most_needed(records, "fosfor")
        self.assertIsNotNone(winner)
        self.assertEqual(winner["metadata"]["field_id"], "B")

    def test_has_any_demand_false_when_only_ok_or_surplus(self):
        records = [
            {
                "metadata": {"field_id": "A", "marknummer": "1"},
                "categories": {"fosfor": "OK"},
                "measurements": {"fosfor_mg_100g": 3.0},
            },
            {
                "metadata": {"field_id": "B", "marknummer": "2"},
                "categories": {"fosfor": "Small Surplus"},
                "measurements": {"fosfor_mg_100g": 4.0},
            },
        ]
        self.assertFalse(has_any_demand(records, "fosfor"))


if __name__ == "__main__":
    unittest.main()
