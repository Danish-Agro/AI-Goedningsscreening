#!/usr/bin/env python3
"""
Nutrient Status Categorizer
Categorizes soil nutrient levels based on threshold values
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class CategoryThresholds:
    """Threshold values for categorizing a nutrient"""
    large_demand_max: float
    medium_demand_max: float
    small_demand_max: float
    ok_max: float
    small_surplus_max: float
    large_surplus_max: float
    # suspicious_surplus starts after large_surplus_max


class NutrientCategorizer:
    """Categorizes soil nutrients based on threshold values"""
    
    # Based on "Jonas Kategorier for næringsstofindhold.xlsx"
    # Format: [Large Demand, Medium Demand, Small Demand, OK, Small Surplus, Large Surplus[
    # Suspicious Surplus is everything above Large Surplus
    
    THRESHOLDS = {
        'rt': CategoryThresholds(
            large_demand_max=4.5,
            medium_demand_max=5.0,
            small_demand_max=6.0,
            ok_max=6.5,
            small_surplus_max=7.0,
            large_surplus_max=8.0
            # >= 8.0 is Suspicious Surplus
        ),
        'fosfor': CategoryThresholds(  # in units of 10 ppm = 1 mg/100g
            large_demand_max=1.0,
            medium_demand_max=1.5,
            small_demand_max=2.0,
            ok_max=4.0,
            small_surplus_max=5.0,
            large_surplus_max=6.0
            # >= 6.0 is Suspicious Surplus
        ),
        'kalium': CategoryThresholds(  # in units of 10 ppm = 1 mg/100g
            large_demand_max=4.0,
            medium_demand_max=5.5,
            small_demand_max=7.0,
            ok_max=10.0,
            small_surplus_max=12.5,
            large_surplus_max=15.0
            # >= 15.0 is Suspicious Surplus
        ),
        'magnesium': CategoryThresholds(  # in units of 10 ppm = 1 mg/100g
            large_demand_max=2.0,
            medium_demand_max=3.0,
            small_demand_max=4.0,
            ok_max=6.0,
            small_surplus_max=8.0,
            large_surplus_max=10.0
            # >= 10.0 is Suspicious Surplus
        )
    }
    
    CATEGORY_NAMES = [
        'Large Demand',
        'Medium Demand',
        'Small Demand',
        'OK',
        'Small Surplus',
        'Large Surplus',
        'Suspicious Surplus'
    ]
    
    @classmethod
    def categorize_value(cls, nutrient: str, value: Optional[float]) -> Optional[str]:
        """
        Categorize a nutrient value
        
        Args:
            nutrient: Name of nutrient ('rt', 'fosfor', 'kalium', 'magnesium')
            value: Measured value
            
        Returns:
            Category name or None if value is None
        """
        if value is None:
            return None
            
        if nutrient not in cls.THRESHOLDS:
            raise ValueError(f"Unknown nutrient: {nutrient}")
            
        thresholds = cls.THRESHOLDS[nutrient]
        
        if value < thresholds.large_demand_max:
            return 'Large Demand'
        elif value < thresholds.medium_demand_max:
            return 'Medium Demand'
        elif value < thresholds.small_demand_max:
            return 'Small Demand'
        elif value < thresholds.ok_max:
            return 'OK'
        elif value < thresholds.small_surplus_max:
            return 'Small Surplus'
        elif value < thresholds.large_surplus_max:
            return 'Large Surplus'
        else:
            return 'Suspicious Surplus'
    
    @classmethod
    def categorize_sample(cls, sample: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add nutrient categories to a sample
        
        Args:
            sample: Parsed sample dict with 'measurements' key
            
        Returns:
            Sample dict with added 'categories' key
        """
        measurements = sample.get('measurements', {})
        
        categories = {
            'rt': cls.categorize_value('rt', measurements.get('rt')),
            'fosfor': cls.categorize_value('fosfor', measurements.get('fosfor_mg_100g')),
            'kalium': cls.categorize_value('kalium', measurements.get('kalium_mg_100g')),
            'magnesium': cls.categorize_value('magnesium', measurements.get('magnesium_mg_100g')),
        }
        
        # Add to sample
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
