# AI Gødningsscreening - Danish Agro

AI-baseret beslutningsstøtte til analyse af SoilOptix jordprøver.

## Quick Start
```bash
# Setup virtual environment
python -m venv venv
source venv/bin/activate  # Git Bash/Mac
# eller
venv\Scripts\activate  # Windows CMD

# Install dependencies
pip install -r requirements.txt

# Parse jordprøver
python src/parsers/soiloptix_parser.py data/raw/example.xlsx
```

## Status
- **Fase:** Proof-of-Concept
- **Deadline:** 31. marts 2026
- **Stakeholder:** Christian (Direktør planteavl)