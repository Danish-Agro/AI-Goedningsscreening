#!/usr/bin/env python3
"""
NPK Requirements Calculator
Calculates fertilizer needs based on soil status, crop type, and yield level
Based on agronomic rules from Danish Agro documentation
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class CropRequirements:
    """NPK requirements for a specific crop and yield level"""
    crop_name: str
    yield_level: str  # 'low', 'medium', 'high'
    n_range: tuple  # (min, max) kg N/ha
    p_base: float  # Base P requirement kg/ha
    k_base: float  # Base K requirement kg/ha
    mg_base: float  # Base Mg requirement kg/ha
    s_per_n: float  # S requirement as ratio of N


class NPKCalculator:
    """Calculate NPK requirements based on soil status and crop"""
    
    # Crop requirements based on documentation
    # Format: (crop, yield_level): requirements
    CROP_DATA = {
        ('vinterhvede', 'low'): CropRequirements(
            crop_name='Vinterhvede',
            yield_level='Lavt (<60 hkg/ha)',
            n_range=(140, 160),
            p_base=20,
            k_base=50,
            mg_base=12,
            s_per_n=0.09  # 9-13 kg S per 100 kg N
        ),
        ('vinterhvede', 'medium'): CropRequirements(
            crop_name='Vinterhvede',
            yield_level='Mellem (60-75 hkg/ha)',
            n_range=(180, 200),
            p_base=25,
            k_base=60,
            mg_base=15,
            s_per_n=0.09
        ),
        ('vinterhvede', 'high'): CropRequirements(
            crop_name='Vinterhvede',
            yield_level='Højt (>75 hkg/ha)',
            n_range=(220, 240),
            p_base=30,
            k_base=70,
            mg_base=18,
            s_per_n=0.09
        ),
        ('vinterbyg', 'low'): CropRequirements(
            crop_name='Vinterbyg',
            yield_level='Lavt (<60 hkg/ha)',
            n_range=(140, 160),
            p_base=18,
            k_base=50,
            mg_base=12,
            s_per_n=0.08
        ),
        ('vinterbyg', 'medium'): CropRequirements(
            crop_name='Vinterbyg',
            yield_level='Mellem (60-75 hkg/ha)',
            n_range=(180, 200),
            p_base=22,
            k_base=60,
            mg_base=15,
            s_per_n=0.08
        ),
        ('vinterbyg', 'high'): CropRequirements(
            crop_name='Vinterbyg',
            yield_level='Højt (>75 hkg/ha)',
            n_range=(200, 220),
            p_base=28,
            k_base=70,
            mg_base=18,
            s_per_n=0.08
        ),
        ('vinterraps', 'low'): CropRequirements(
            crop_name='Vinterraps',
            yield_level='Lavt (<40 hkg/ha)',
            n_range=(160, 180),
            p_base=25,
            k_base=70,
            mg_base=15,
            s_per_n=0.12  # Raps har højere S-behov
        ),
        ('vinterraps', 'medium'): CropRequirements(
            crop_name='Vinterraps',
            yield_level='Mellem (40-50 hkg/ha)',
            n_range=(180, 200),
            p_base=30,
            k_base=80,
            mg_base=18,
            s_per_n=0.12
        ),
        ('vinterraps', 'high'): CropRequirements(
            crop_name='Vinterraps',
            yield_level='Højt (>50 hkg/ha)',
            n_range=(200, 220),
            p_base=35,
            k_base=90,
            mg_base=20,
            s_per_n=0.12
        ),
        ('vårbyg', 'low'): CropRequirements(
            crop_name='Vårbyg',
            yield_level='Lavt (<50 hkg/ha)',
            n_range=(100, 120),
            p_base=15,
            k_base=45,
            mg_base=10,
            s_per_n=0.08
        ),
        ('vårbyg', 'medium'): CropRequirements(
            crop_name='Vårbyg',
            yield_level='Mellem (50-65 hkg/ha)',
            n_range=(120, 140),
            p_base=20,
            k_base=55,
            mg_base=12,
            s_per_n=0.08
        ),
        ('vårbyg', 'high'): CropRequirements(
            crop_name='Vårbyg',
            yield_level='Højt (>65 hkg/ha)',
            n_range=(140, 160),
            p_base=25,
            k_base=65,
            mg_base=15,
            s_per_n=0.08
        ),
    }
    
    # Adjustments based on soil nutrient categories
    # How much to add/subtract based on category
    CATEGORY_ADJUSTMENTS = {
        'Large Demand': 1.5,      # 50% more
        'Medium Demand': 1.2,     # 20% more
        'Small Demand': 1.1,      # 10% more
        'OK': 1.0,                # Base amount
        'Small Surplus': 0.8,     # 20% less
        'Large Surplus': 0.5,     # 50% less
        'Suspicious Surplus': 0.0 # No additional needed
    }
    
    # P-loft according to legislation
    P_MAX = 30  # kg P/ha max
    
    @classmethod
    def calculate_requirements(
        cls,
        sample: Dict[str, Any],
        crop: str = 'vinterhvede',
        yield_level: str = 'medium'
    ) -> Dict[str, Any]:
        """
        Calculate NPK requirements for a field
        
        Args:
            sample: Categorized soil sample
            crop: Crop type (e.g., 'vinterhvede', 'vinterbyg')
            yield_level: 'low', 'medium', or 'high'
            
        Returns:
            Dictionary with calculated requirements
        """
        # Get crop requirements
        crop_key = (crop.lower(), yield_level.lower())
        if crop_key not in cls.CROP_DATA:
            raise ValueError(f"Unknown crop/yield combination: {crop}/{yield_level}")
        
        crop_req = cls.CROP_DATA[crop_key]
        categories = sample.get('categories', {})
        
        # Calculate N requirement (midpoint of range)
        n_requirement = sum(crop_req.n_range) / 2
        
        # Calculate P requirement with soil status adjustment
        p_category = categories.get('fosfor', 'OK')
        p_adjustment = cls.CATEGORY_ADJUSTMENTS.get(p_category, 1.0)
        p_requirement = crop_req.p_base * p_adjustment
        
        # Apply P-loft
        if p_requirement > cls.P_MAX:
            p_requirement = cls.P_MAX
            p_note = f"Begrænset til lovgivningsmæssigt P-loft ({cls.P_MAX} kg/ha)"
        else:
            p_note = None
        
        # Calculate K requirement with soil status adjustment
        k_category = categories.get('kalium', 'OK')
        k_adjustment = cls.CATEGORY_ADJUSTMENTS.get(k_category, 1.0)
        k_requirement = crop_req.k_base * k_adjustment
        
        # Calculate Mg requirement with soil status adjustment
        mg_category = categories.get('magnesium', 'OK')
        mg_adjustment = cls.CATEGORY_ADJUSTMENTS.get(mg_category, 1.0)
        mg_requirement = crop_req.mg_base * mg_adjustment
        
        # Calculate S requirement based on N
        s_requirement = n_requirement * crop_req.s_per_n
        
        # pH consideration
        rt_category = categories.get('rt')
        ph_note = None
        if rt_category in ['Large Demand', 'Medium Demand']:
            ph_note = "pH er lav - overvej kalkning for optimal næringsstofoptagelse"
        elif rt_category in ['Large Surplus', 'Suspicious Surplus']:
            ph_note = "pH er meget høj - kan reducere tilgængelighed af mikronæringsstoffer"
        
        return {
            'crop': crop_req.crop_name,
            'yield_level': crop_req.yield_level,
            'requirements': {
                'N': {
                    'amount_kg_ha': round(n_requirement, 1),
                    'range': crop_req.n_range,
                    'note': 'Baseret på afgrødenorm'
                },
                'P': {
                    'amount_kg_ha': round(p_requirement, 1),
                    'soil_category': p_category,
                    'adjustment': f"{int((p_adjustment - 1) * 100):+d}%" if p_adjustment != 1.0 else "Ingen",
                    'note': p_note
                },
                'K': {
                    'amount_kg_ha': round(k_requirement, 1),
                    'soil_category': k_category,
                    'adjustment': f"{int((k_adjustment - 1) * 100):+d}%" if k_adjustment != 1.0 else "Ingen",
                },
                'Mg': {
                    'amount_kg_ha': round(mg_requirement, 1),
                    'soil_category': mg_category,
                    'adjustment': f"{int((mg_adjustment - 1) * 100):+d}%" if mg_adjustment != 1.0 else "Ingen",
                },
                'S': {
                    'amount_kg_ha': round(s_requirement, 1),
                    'note': f'Beregnet som {int(crop_req.s_per_n * 100)}% af N-behov'
                }
            },
            'ph_consideration': ph_note
        }
    
    @classmethod
    def get_product_recommendations(cls, requirements: Dict[str, Any]) -> list:
        """
        Get product recommendations based on NPK requirements
        
        Args:
            requirements: Output from calculate_requirements()
            
        Returns:
            List of recommended products
        """
        products = []
        
        n_need = requirements['requirements']['N']['amount_kg_ha']
        s_need = requirements['requirements']['S']['amount_kg_ha']
        p_need = requirements['requirements']['P']['amount_kg_ha']
        k_need = requirements['requirements']['K']['amount_kg_ha']
        
        # N + S products
        if n_need > 0:
            # YaraBela SULFAN (27% N, 4% S)
            products.append({
                'name': 'YaraBela SULFAN 24',
                'composition': '27-0-0 (+4S)',
                'purpose': 'N og S behov',
                'amount_kg_ha': round(n_need / 0.27 * 1.15, 0),  # 15% buffer
                'note': f'Dækker ca. {round(n_need, 0)} kg N og {round(n_need * 0.04/0.27, 0)} kg S'
            })
        
        # NPK compound
        if p_need > 5 and k_need > 10:
            products.append({
                'name': 'NPK 15-3-15',
                'composition': '15-3-15',
                'purpose': 'Kombineret NPK',
                'amount_kg_ha': round(max(p_need / 0.03, k_need / 0.15), 0),
                'note': 'Grundgødning med balanceret NPK'
            })
        
        # P product if needed separately
        elif p_need > 10:
            products.append({
                'name': 'Superfos NP 18-20',
                'composition': '18-20-0',
                'purpose': 'Fosfor + N',
                'amount_kg_ha': round(p_need / 0.20 * 1.1, 0),
                'note': f'Primært til P-behov'
            })
        
        # K product if needed separately
        if k_need > 50:
            products.append({
                'name': 'Kaliumchlorid 60%',
                'composition': '0-0-60',
                'purpose': 'Kalium',
                'amount_kg_ha': round(k_need / 0.60, 0),
                'note': 'Højt K-behov'
            })
        
        return products


# CLI Usage
if __name__ == '__main__':
    import json
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python npk_calculator.py <categorized_samples.json> [crop] [yield_level]")
        print("\nCrops: vinterhvede, vinterbyg, vinterraps, vårbyg")
        print("Yield levels: low, medium, high")
        sys.exit(1)
    
    samples_file = sys.argv[1]
    crop = sys.argv[2] if len(sys.argv) > 2 else 'vinterhvede'
    yield_level = sys.argv[3] if len(sys.argv) > 3 else 'medium'
    
    # Load samples
    with open(samples_file, 'r', encoding='utf-8') as f:
        samples = json.load(f)
    
    print(f"\n=== NPK Behovsberegning ===")
    print(f"Afgrøde: {crop.title()}")
    print(f"Udbytteniveau: {yield_level.title()}\n")
    
    # Calculate for top 3 priority fields
    for i, sample in enumerate(samples[:3], 1):
        metadata = sample['metadata']
        
        print(f"\n{'='*60}")
        print(f"{i}. Mark {metadata['marknummer']} (Field ID: {metadata['field_id']})")
        print(f"{'='*60}")
        
        try:
            result = NPKCalculator.calculate_requirements(sample, crop, yield_level)
            
            print(f"\nAfgrøde: {result['crop']} - {result['yield_level']}")
            print(f"\nAnbefalede mængder:")
            print(f"  N (Kvælstof):  {result['requirements']['N']['amount_kg_ha']} kg/ha")
            print(f"  P (Fosfor):    {result['requirements']['P']['amount_kg_ha']} kg/ha (jordstatus: {result['requirements']['P']['soil_category']}, justering: {result['requirements']['P']['adjustment']})")
            print(f"  K (Kalium):    {result['requirements']['K']['amount_kg_ha']} kg/ha (jordstatus: {result['requirements']['K']['soil_category']}, justering: {result['requirements']['K']['adjustment']})")
            print(f"  Mg (Magnesium):{result['requirements']['Mg']['amount_kg_ha']} kg/ha (jordstatus: {result['requirements']['Mg']['soil_category']}, justering: {result['requirements']['Mg']['adjustment']})")
            print(f"  S (Svovl):     {result['requirements']['S']['amount_kg_ha']} kg/ha")
            
            if result['requirements']['P'].get('note'):
                print(f"\n⚠️  {result['requirements']['P']['note']}")
            
            if result.get('ph_consideration'):
                print(f"⚠️  {result['ph_consideration']}")
            
            # Product recommendations
            products = NPKCalculator.get_product_recommendations(result)
            if products:
                print(f"\nAnbefalede produkter:")
                for prod in products:
                    print(f"  • {prod['name']} ({prod['composition']})")
                    print(f"    {prod['amount_kg_ha']} kg/ha - {prod['note']}")
        
        except Exception as e:
            print(f"Fejl: {e}")
    
    print(f"\n{'='*60}\n")