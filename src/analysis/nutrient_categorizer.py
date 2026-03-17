#!/usr/bin/env python3
"""
Nutrient Status Categorizer
Categorizes soil nutrient levels based on threshold values.
Grænseværdier og jordtype-afhængig logik er importeret fra beregningsgrundlag.py.
"""

from typing import Dict, Any, Optional
from analysis.beregningsgrundlag import (
    kategoriser_rt,
    kategoriser_mg,
    kategoriser_fosfor,
    kategoriser_kalium,
)

# Standard JB-nummer bruges som fallback hvis jordtypedata mangler i prøven.
# JB5 (sandblandet lerjord) hører til gruppen "JB2_JB4_10" (standardgruppen).
_FALLBACK_JB = 5


class NutrientCategorizer:
    """Kategoriserer jordprøvers næringsstofniveauer via beregningsgrundlag.py."""

    CATEGORY_NAMES = [
        'Large Demand',
        'Medium Demand',
        'Small Demand',
        'OK',
        'Small Surplus',
        'Large Surplus',
        'Suspicious Surplus',
    ]

    @classmethod
    def categorize_value(
        cls,
        nutrient: str,
        value: Optional[float],
        jb: Optional[int] = None,
    ) -> Optional[str]:
        """
        Kategoriser en næringsstofværdi.

        Args:
            nutrient: 'rt', 'fosfor', 'kalium' eller 'magnesium'
            value:    Målt værdi
            jb:       JB-nummer (1-11). Bruges kun for fosfor og kalium.
                      Hvis None, bruges _FALLBACK_JB.

        Returns:
            Kategorinavn eller None hvis value er None.
        """
        if value is None:
            return None

        if nutrient == 'rt':
            return kategoriser_rt(value)
        elif nutrient == 'magnesium':
            return kategoriser_mg(value)
        elif nutrient == 'fosfor':
            return kategoriser_fosfor(value, jb if jb is not None else _FALLBACK_JB)
        elif nutrient == 'kalium':
            return kategoriser_kalium(value, jb if jb is not None else _FALLBACK_JB)
        else:
            raise ValueError(f"Ukendt næringsstof: {nutrient}")

    @classmethod
    def categorize_sample(cls, sample: Dict[str, Any]) -> Dict[str, Any]:
        """
        Tilføj næringsstofkategorier til en prøve.

        Args:
            sample: Parset prøve-dict med 'measurements'-nøgle.
                    Kan indeholde 'measurements.jb_nummer' for jordtype-afhængig kategorisering.

        Returns:
            Prøve-dict med tilføjet 'categories'-nøgle.
        """
        measurements = sample.get('measurements', {})
        jb = measurements.get('jb_nummer')  # None → fallback anvendes i categorize_value

        categories = {
            'rt':       cls.categorize_value('rt',       measurements.get('rt')),
            'fosfor':   cls.categorize_value('fosfor',   measurements.get('fosfor_mg_100g'),   jb),
            'kalium':   cls.categorize_value('kalium',   measurements.get('kalium_mg_100g'),   jb),
            'magnesium': cls.categorize_value('magnesium', measurements.get('magnesium_mg_100g')),
        }

        sample['categories'] = categories
        return sample
    
    @classmethod
    def get_priority_score(cls, category: Optional[str]) -> int:
        """
        Get priority score for a category (higher = more urgent need)
        
        Large Demand = 6 (most urgent)
        Suspicious Surplus = 0 (no action needed, potentially problematic)
        """
        if category is None:
            return 0
            
        priority_map = {
            'Large Demand': 6,
            'Medium Demand': 5,
            'Small Demand': 4,
            'OK': 3,
            'Small Surplus': 2,
            'Large Surplus': 1,
            'Suspicious Surplus': 0
        }
        
        return priority_map.get(category, 0)
    
    @classmethod
    def get_field_priority(cls, sample: Dict[str, Any]) -> int:
        """
        Calculate overall priority score for a field based on all nutrients
        
        Returns sum of priority scores
        """
        categories = sample.get('categories', {})
        
        total_score = 0
        for nutrient in ['rt', 'fosfor', 'kalium', 'magnesium']:
            category = categories.get(nutrient)
            total_score += cls.get_priority_score(category)
            
        return total_score


# CLI Usage
if __name__ == '__main__':
    import json
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python nutrient_categorizer.py <parsed_samples.json> [output.json]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Load samples
    with open(input_file, 'r', encoding='utf-8') as f:
        samples = json.load(f)
    
    print(f"Loaded {len(samples)} samples")
    
    # Categorize all samples
    for sample in samples:
        NutrientCategorizer.categorize_sample(sample)
    
    # Sort by priority (highest first)
    samples_with_priority = [
        {
            **sample,
            'priority_score': NutrientCategorizer.get_field_priority(sample)
        }
        for sample in samples
    ]
    samples_with_priority.sort(key=lambda x: x['priority_score'], reverse=True)
    
    # Output
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(samples_with_priority, f, indent=2, ensure_ascii=False)
        print(f"Saved to {output_file}")
    else:
        # Print top 5 unique fields
        best_sample_per_field = {}
        for sample in samples_with_priority:
            metadata = sample.get('metadata', {})
            field_key = metadata.get('field_id') or metadata.get('marknummer')
            if not field_key:
                continue
            existing = best_sample_per_field.get(field_key)
            if existing is None or sample.get('priority_score', 0) > existing.get('priority_score', 0):
                best_sample_per_field[field_key] = sample

        unique_fields = sorted(
            best_sample_per_field.values(),
            key=lambda s: s.get('priority_score', 0),
            reverse=True
        )

        print("\n=== TOP 5 FIELDS BY PRIORITY ===")
        for i, sample in enumerate(unique_fields[:5], 1):
            metadata = sample['metadata']
            categories = sample['categories']
            priority = sample['priority_score']
            
            print(f"\n{i}. Mark {metadata['marknummer']} (Field ID: {metadata['field_id']})")
            print(f"   Priority Score: {priority}")
            print(f"   Rt (pH+0.5): {categories['rt']}")
            print(f"   Fosfor: {categories['fosfor']}")
            print(f"   Kalium: {categories['kalium']}")
            print(f"   Magnesium: {categories['magnesium']}")
