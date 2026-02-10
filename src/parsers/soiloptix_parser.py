#!/usr/bin/env python3
"""
SoilOptix Data Parser
Parses Excel files from AGROLAB and converts to structured JSON format
"""

import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Any


class SoilOptixParser:
    """Parser for SoilOptix lab results in Excel format"""
    
    # Row indices (0-indexed) based on observed structure
    ROW_KUNDENR = 2
    ROW_ORDRENUMMER = 5
    ROW_ANALYSE_NR = 6
    ROW_PROVEBETEGNELSE = 7
    ROW_FIELD_ID = 8
    ROW_MARKNUMMER = 9
    ROW_PARAMETER_HEADER = 10
    ROW_DATA_START = 11
    
    # Expected parameters
    PARAMETERS = [
        'Rt',  # pH + 0.5
        'Fosfor',  # P in mg/100g
        'Kalium',  # K in mg/100g
        'Magnesium',  # Mg in mg/100g
        'Kobber',  # Cu in mg/kg
        'Bor',  # B in mg/10kg
        'Organisk stof',  # % organic matter
        'Ler DYN (<0,002 mm)',  # Clay %
        'Silt DYN (0,002-0,02 mm)',  # Silt %
        'Finsand DYN (0,02 - 0,2 mm)',  # Fine sand %
        'Grovsand DYN (0,2 - 2,0 mm)',  # Coarse sand %
        'JB'  # Soil classification number
    ]
    
    def __init__(self, filepath: str):
        """Initialize parser with path to Excel file"""
        self.filepath = Path(filepath)
        self.df = None
        self.samples = []
        
    def load(self):
        """Load Excel file without header"""
        self.df = pd.read_excel(self.filepath, header=None)
        return self
        
    def parse(self) -> List[Dict[str, Any]]:
        """Parse all soil samples from the Excel file"""
        if self.df is None:
            raise ValueError("Must call load() before parse()")
            
        self.samples = []
        
        # Get metadata rows
        kundenr = self.df.iloc[self.ROW_KUNDENR, 1]
        
        # Find the first data column (column 3 typically)
        first_data_col = 3
        
        # Iterate through each sample column
        for col_idx in range(first_data_col, len(self.df.columns)):
            # Check if this column has data (ordrenummer should be present)
            ordrenummer = self.df.iloc[self.ROW_ORDRENUMMER, col_idx]
            
            if pd.isna(ordrenummer):
                # No more samples
                break
                
            sample = self._parse_sample(col_idx, kundenr)
            if sample:
                self.samples.append(sample)
                
        return self.samples
    
    def _parse_sample(self, col_idx: int, kundenr: Any) -> Dict[str, Any]:
        """Parse a single sample from a column"""
        try:
            # Extract metadata
            ordrenummer = self.df.iloc[self.ROW_ORDRENUMMER, col_idx]
            analyse_nr = self.df.iloc[self.ROW_ANALYSE_NR, col_idx]
            provebetegnelse = self.df.iloc[self.ROW_PROVEBETEGNELSE, col_idx]
            field_id = self.df.iloc[self.ROW_FIELD_ID, col_idx]
            marknummer = self.df.iloc[self.ROW_MARKNUMMER, col_idx]
            
            # Extract measurements
            measurements = {}
            for param_idx, param_name in enumerate(self.PARAMETERS):
                row_idx = self.ROW_DATA_START + param_idx
                value = self.df.iloc[row_idx, col_idx]
                
                # Convert to float if possible, keep as-is otherwise
                if not pd.isna(value):
                    try:
                        # Handle both comma and dot as decimal separator
                        if isinstance(value, str):
                            value = value.replace(',', '.')
                        measurements[param_name] = float(value)
                    except (ValueError, TypeError):
                        measurements[param_name] = value
                else:
                    measurements[param_name] = None
            
            # Build sample object
            sample = {
                'metadata': {
                    'kundenr': kundenr,
                    'ordrenummer': int(ordrenummer) if not pd.isna(ordrenummer) else None,
                    'analyse_nr': int(analyse_nr) if not pd.isna(analyse_nr) else None,
                    'provebetegnelse': int(provebetegnelse) if not pd.isna(provebetegnelse) else None,
                    'field_id': str(field_id) if not pd.isna(field_id) else None,
                    'marknummer': str(marknummer) if not pd.isna(marknummer) else None,
                },
                'measurements': {
                    'rt': measurements.get('Rt'),  # pH + 0.5
                    'fosfor_mg_100g': measurements.get('Fosfor'),  # P
                    'kalium_mg_100g': measurements.get('Kalium'),  # K
                    'magnesium_mg_100g': measurements.get('Magnesium'),  # Mg
                    'kobber_mg_kg': measurements.get('Kobber'),  # Cu
                    'bor_mg_10kg': measurements.get('Bor'),  # B
                    'organisk_stof_pct': measurements.get('Organisk stof'),
                    'ler_pct': measurements.get('Ler DYN (<0,002 mm)'),
                    'silt_pct': measurements.get('Silt DYN (0,002-0,02 mm)'),
                    'finsand_pct': measurements.get('Finsand DYN (0,02 - 0,2 mm)'),
                    'grovsand_pct': measurements.get('Grovsand DYN (0,2 - 2,0 mm)'),
                    'jb': measurements.get('JB'),
                }
            }
            
            return sample
            
        except Exception as e:
            print(f"Warning: Failed to parse sample at column {col_idx}: {e}")
            return None
    
    def to_json(self, indent=2) -> str:
        """Convert samples to JSON string"""
        return json.dumps(self.samples, indent=indent, ensure_ascii=False)
    
    def save_json(self, output_path: str):
        """Save samples as JSON file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(self.to_json())


# CLI Usage
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python soiloptix_parser.py <excel_file> [output.json]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Parse the file
    parser = SoilOptixParser(input_file)
    parser.load()
    samples = parser.parse()
    
    print(f"Parsed {len(samples)} soil samples")
    
    # Output
    if output_file:
        parser.save_json(output_file)
        print(f"Saved to {output_file}")
    else:
        # Print first sample as example
        if samples:
            print("\n=== EXAMPLE SAMPLE ===")
            print(json.dumps(samples[0], indent=2, ensure_ascii=False))
