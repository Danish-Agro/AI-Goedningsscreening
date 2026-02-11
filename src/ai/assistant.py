#!/usr/bin/env python3
"""
AI Assistant for Fertilizer Screening
Uses OpenAI GPT-4 to answer questions about soil samples
"""

import json
import os
from typing import List, Dict, Any
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class FertilizerAssistant:
    """AI Assistant for analyzing soil samples and providing recommendations"""
    
    def __init__(self, samples_file: str):
        """
        Initialize assistant with categorized soil samples
        
        Args:
            samples_file: Path to JSON file with categorized samples
        """
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Load soil samples
        with open(samples_file, 'r', encoding='utf-8') as f:
            self.samples = json.load(f)
        
        print(f"Loaded {len(self.samples)} soil samples")
        
    def _build_system_prompt(self) -> str:
        """Build system prompt with agronomic knowledge"""
        return """Du er en agronomisk AI-assistent hos Danish Agro.

Din opgave er at hjælpe sælgere med at identificere næringsstofbehov 
baseret på SoilOptix-jordanalyser og give konkrete gødningsanbefalinger.

KATEGORIER FOR NÆRINGSSTOFFER:
- Large Demand: Akut mangel, høj prioritet
- Medium Demand: Moderat mangel
- Small Demand: Let mangel
- OK: Tilstrækkeligt niveau
- Small Surplus: Let overskud
- Large Surplus: Betydeligt overskud
- Suspicious Surplus: Meget højt niveau (muligt problem)

REGLER:
- Vær præcis og faktuel
- Forklar altid din reasoning
- Angiv anbefalinger i kg/ha når relevant
- Advar om lovgivningsmæssige begrænsninger (fx P-loft på max 30 kg P/ha)
- Vær ærlig hvis data mangler eller er usikker

TONE:
- Professionel men tilgængelig
- Hjælpsom overfor sælgere uden agronomisk baggrund
- Konkret og actionable"""

    def _prepare_samples_context(self) -> str:
        """Prepare samples data as context for AI"""
        # Create summary of samples
        summary = []
        
        for sample in self.samples[:50]:  # Limit to avoid token limits
            metadata = sample['metadata']
            categories = sample['categories']
            measurements = sample['measurements']
            priority = sample.get('priority_score', 0)
            
            summary.append(f"""
Mark: {metadata['marknummer']} (Field ID: {metadata['field_id']})
Priority Score: {priority}
Næringsstof status:
- Rt (pH+0.5): {categories['rt']} (værdi: {measurements['rt']})
- Fosfor: {categories['fosfor']} (værdi: {measurements['fosfor_mg_100g']} mg/100g)
- Kalium: {categories['kalium']} (værdi: {measurements['kalium_mg_100g']} mg/100g)
- Magnesium: {categories['magnesium']} (værdi: {measurements['magnesium_mg_100g']} mg/100g)
Jordtype: {measurements['ler_pct']}% ler, {measurements['finsand_pct']}% finsand
""")
        
        return "\n---\n".join(summary)
    
    def ask(self, question: str) -> str:
        """
        Ask the assistant a question about the soil samples
        
        Args:
            question: Question from the user/salesperson
            
        Returns:
            AI-generated answer
        """
        # Build messages
        messages = [
            {"role": "system", "content": self._build_system_prompt()},
            {"role": "user", "content": f"""Her er jordprøve data fra alle marker:

{self._prepare_samples_context()}

---

Sælgers spørgsmål: {question}

Giv et konkret, forklarende svar baseret på dataen."""}
        ]
        
        # Call OpenAI
        response = self.client.chat.completions.create(
            model="gpt-4o",  # eller "gpt-4-turbo"
            messages=messages,
            temperature=0.7,
            max_tokens=1500
        )
        
        return response.choices[0].message.content
    
    def get_priority_fields(self, top_n: int = 5) -> List[Dict[str, Any]]:
        """Get top N fields by priority score"""
        sorted_samples = sorted(
            self.samples, 
            key=lambda x: x.get('priority_score', 0), 
            reverse=True
        )
        return sorted_samples[:top_n]


# CLI Usage
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python assistant.py <categorized_samples.json>")
        sys.exit(1)
    
    samples_file = sys.argv[1]
    
    # Initialize assistant
    assistant = FertilizerAssistant(samples_file)
    
    # Interactive mode
    print("\n=== AI Gødningsassistent ===")
    print("Stil spørgsmål om jordprøverne (eller 'quit' for at afslutte)\n")
    
    while True:
        question = input("Spørgsmål: ").strip()
        
        if question.lower() in ['quit', 'exit', 'q']:
            break
            
        if not question:
            continue
        
        print("\nSvarer...\n")
        answer = assistant.ask(question)
        print(answer)
        print("\n" + "="*60 + "\n")