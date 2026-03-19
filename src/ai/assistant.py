#!/usr/bin/env python3
"""
AI Assistant for Fertilizer Screening
Uses deterministic handlers for data queries and optional LLM for explanation.
"""

import json
import os
import re
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

_AZURE_ENDPOINT    = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip()
_AZURE_KEY         = os.getenv("AZURE_OPENAI_KEY", "").strip()
AZURE_DEPLOYMENT   = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o").strip()

ALLOWED_CATEGORIES = [
    "Large Demand",
    "Medium Demand",
    "Small Demand",
    "OK",
    "Small Surplus",
    "Surplus",
    "Medium Surplus",
    "Large Surplus",
]

CATEGORY_NEED_ORDER = {
    "large demand": 0,
    "medium demand": 1,
    "small demand": 2,
    "ok": 3,
    "small surplus": 4,
    "surplus": 5,
    "medium surplus": 6,
    "large surplus": 7,
}

NUTRIENT_SPECS = {
    "fosfor": {
        "aliases": ["fosfor", "p"],
        "measurement_key": "fosfor_mg_100g",
        "category_key": "fosfor",
        "unit": "mg/100g",
        "label": "Fosfor",
    },
    "kalium": {
        "aliases": ["kalium", "k"],
        "measurement_key": "kalium_mg_100g",
        "category_key": "kalium",
        "unit": "mg/100g",
        "label": "Kalium",
    },
    "magnesium": {
        "aliases": ["magnesium", "mg"],
        "measurement_key": "magnesium_mg_100g",
        "category_key": "magnesium",
        "unit": "mg/100g",
        "label": "Magnesium",
    },
    "rt": {
        "aliases": ["rt", "reaktionstal", "ph"],
        "measurement_key": "rt",
        "category_key": "rt",
        "unit": "rt",
        "label": "Rt",
    },
}

FORBIDDEN_TERMS = [
    "lovgiv",
    "bekendt",
    "compliance",
    "kg/ha",
    "fosforloft",
    "maks",
    "max",
    "loft",
    "grænse",
    "dosis",
    "tildel",
    "tilførsel",
    "kg p",
    "kg n",
    "timing",
]

PHASE1_BLOCK_MESSAGE = (
    "Lovgivning og dosisberegning er ikke en del af denne POC (fase 1). "
    "Output er screening og kræver faglig validering."
)


def _to_float(value: Any) -> Optional[float]:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.strip().replace(",", ".").replace("<", "")
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


def sanitize_output(text: str) -> str:
    lowered = text.lower()
    if any(term in lowered for term in FORBIDDEN_TERMS):
        return PHASE1_BLOCK_MESSAGE
    return text


def normalize_category(category: Any, whitelist: Optional[List[str]] = None) -> str:
    allowed = whitelist or ALLOWED_CATEGORIES
    allowed_map = {c.lower(): c for c in allowed}
    if isinstance(category, str):
        normalized = category.strip().lower()
        return allowed_map.get(normalized, "OK")
    return "OK"


def _normalize_categories_in_text(text: str, whitelist: List[str]) -> str:
    """Replace category-like tokens not in whitelist with OK."""
    whitelist_map = {c.lower(): c for c in whitelist}
    pattern = re.compile(
        r"\b(?:Large Demand|Medium Demand|Small Demand|OK|Small Surplus|Surplus|"
        r"Medium Surplus|Large Surplus|Suspicious Surplus)\b",
        flags=re.IGNORECASE,
    )

    def _replace(match: re.Match) -> str:
        token = match.group(0)
        normalized = token.lower()
        return whitelist_map.get(normalized, "OK")

    return pattern.sub(_replace, text)


def detect_nutrient(question: str) -> Optional[str]:
    q = question.lower()
    for nutrient_key, spec in NUTRIENT_SPECS.items():
        for alias in spec["aliases"]:
            if re.search(rf"\b{re.escape(alias.lower())}\b", q):
                return nutrient_key
    return None


def classify_intent(question: str) -> str:
    q = question.lower()
    data_keywords = [
        "mest",
        "højeste",
        "laveste",
        "top",
        "prioriter",
        "sum",
        "hvilke marker",
        "max",
        "min",
    ]
    explain_keywords = ["hvorfor", "hvad betyder", "forklar"]

    if any(keyword in q for keyword in data_keywords):
        return "DATA_QUERY"
    if any(keyword in q for keyword in explain_keywords):
        return "EXPLAIN_QUERY"
    return "OTHER"


def handle_max_nutrient(records: List[Dict[str, Any]], nutrient: str) -> Dict[str, Any]:
    spec = NUTRIENT_SPECS.get(nutrient)
    if not spec:
        return {"type": "max_nutrient", "nutrient": nutrient, "error": "unknown_nutrient"}

    best = None
    for record in records:
        measurements = record.get("measurements", {})
        value = _to_float(measurements.get(spec["measurement_key"]))
        if value is None:
            continue
        if best is None or value > best[0]:
            best = (value, record)

    if best is None:
        return {"type": "max_nutrient", "nutrient": nutrient, "error": "no_data"}

    value, record = best
    metadata = record.get("metadata", {})
    categories = record.get("categories", {})
    return {
        "type": "max_nutrient",
        "nutrient": nutrient,
        "label": spec["label"],
        "field_id": metadata.get("field_id"),
        "marknummer": metadata.get("marknummer"),
        "value": value,
        "unit": spec["unit"],
        "category": normalize_category(categories.get(spec["category_key"])),
    }


def has_any_demand(records: List[Dict[str, Any]], nutrient: str) -> bool:
    spec = NUTRIENT_SPECS.get(nutrient)
    if not spec:
        return False
    demand_values = {"large demand", "medium demand", "small demand"}
    for record in records:
        category = record.get("categories", {}).get(spec["category_key"])
        if isinstance(category, str) and category.strip().lower() in demand_values:
            return True
    return False


def handle_most_needed(records: List[Dict[str, Any]], nutrient: str) -> Dict[str, Any]:
    spec = NUTRIENT_SPECS.get(nutrient)
    if not spec:
        return {"type": "most_needed", "nutrient": nutrient, "error": "unknown_nutrient"}

    if not has_any_demand(records, nutrient):
        return {
            "type": "most_needed",
            "nutrient": nutrient,
            "no_demand": True,
            "message": (
                "Der findes ingen marker med påvist mangel (Demand) for "
                f"{spec['label'].lower()} i dette datasæt."
            ),
        }

    candidates = []
    for record in records:
        category = record.get("categories", {}).get(spec["category_key"])
        value = _to_float(record.get("measurements", {}).get(spec["measurement_key"]))
        if category is None or value is None:
            continue
        rank = CATEGORY_NEED_ORDER.get(str(category).strip().lower())
        if rank is None:
            continue
        metadata = record.get("metadata", {})
        stable = str(metadata.get("field_id") or metadata.get("marknummer") or "")
        candidates.append((rank, value, stable, record))

    if not candidates:
        return {"type": "most_needed", "nutrient": nutrient, "error": "no_data"}

    candidates.sort(key=lambda x: (x[0], x[1], x[2]))
    _, value, _, record = candidates[0]
    metadata = record.get("metadata", {})
    category = normalize_category(record.get("categories", {}).get(spec["category_key"]))
    return {
        "type": "most_needed",
        "nutrient": nutrient,
        "label": spec["label"],
        "field_id": metadata.get("field_id"),
        "marknummer": metadata.get("marknummer"),
        "value": value,
        "unit": spec["unit"],
        "category": category,
    }


def handle_top_priority(records: List[Dict[str, Any]], n: int = 5) -> Dict[str, Any]:
    best_per_field: Dict[tuple, Dict[str, Any]] = {}

    for record in records:
        metadata = record.get("metadata", {})
        key = (metadata.get("field_id"), metadata.get("marknummer"))
        current = best_per_field.get(key)

        if current is None:
            best_per_field[key] = record
            continue

        current_priority = current.get("priority_score", 0)
        new_priority = record.get("priority_score", 0)
        if new_priority > current_priority:
            best_per_field[key] = record
            continue
        if new_priority < current_priority:
            continue

        # Tie-breaker: highest analyse_nr if present
        current_analyse = _to_float(current.get("metadata", {}).get("analyse_nr")) or float("-inf")
        new_analyse = _to_float(metadata.get("analyse_nr")) or float("-inf")
        if new_analyse > current_analyse:
            best_per_field[key] = record

    sorted_records = sorted(
        best_per_field.values(),
        key=lambda r: r.get("priority_score", 0),
        reverse=True,
    )

    items = []
    for record in sorted_records[: max(0, n)]:
        metadata = record.get("metadata", {})
        items.append(
            {
                "field_id": metadata.get("field_id"),
                "marknummer": metadata.get("marknummer"),
                "priority_score": record.get("priority_score", 0),
            }
        )
    return {"type": "top_priority", "top_n": n, "items": items}


def get_most_needed(records: List[Dict[str, Any]], nutrient_key: str) -> Optional[Dict[str, Any]]:
    """Backward-compatible helper used by existing tests/calls."""
    result = handle_most_needed(records, nutrient_key)
    if result.get("no_demand") or result.get("error"):
        return None
    field_id = result.get("field_id")
    marknummer = result.get("marknummer")
    for record in records:
        metadata = record.get("metadata", {})
        if metadata.get("field_id") == field_id and metadata.get("marknummer") == marknummer:
            return record
    return None


class FertilizerAssistant:
    """AI assistant that routes data questions to deterministic handlers."""

    def __init__(self, samples_file: str):
        self.client = (
            AzureOpenAI(
                azure_endpoint=_AZURE_ENDPOINT,
                api_key=_AZURE_KEY,
                api_version="2025-01-01-preview",
            )
            if _AZURE_ENDPOINT and _AZURE_KEY
            else None
        )
        with open(samples_file, "r", encoding="utf-8") as f:
            self.samples = json.load(f)
        print(f"Loaded {len(self.samples)} soil samples")

    @classmethod
    def from_samples(cls, samples: List[Dict[str, Any]], api_key: Optional[str] = None) -> "FertilizerAssistant":
        """Opret assistent direkte fra en liste af (allerede berigede) samples."""
        obj = object.__new__(cls)
        obj.client = (
            AzureOpenAI(
                azure_endpoint=_AZURE_ENDPOINT,
                api_key=_AZURE_KEY,
                api_version="2025-01-01-preview",
            )
            if _AZURE_ENDPOINT and _AZURE_KEY
            else None
        )
        obj.samples = samples
        return obj

    def _category_whitelist(self) -> List[str]:
        return list(ALLOWED_CATEGORIES)

    def _parse_json_response(self, content: str) -> Optional[Dict[str, Any]]:
        text = content.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
            text = re.sub(r"\s*```$", "", text)
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            return None
        return None

    def _fallback_explain(self, result_dict: Dict[str, Any]) -> Dict[str, Any]:
        result_type = result_dict.get("type")
        if result_type == "max_nutrient":
            answer = (
                f"Topmark er {result_dict.get('field_id')} ({result_dict.get('marknummer')}) med "
                f"{result_dict.get('label')} {result_dict.get('value')} {result_dict.get('unit')}."
            )
        elif result_type == "most_needed":
            if result_dict.get("no_demand"):
                answer = result_dict.get("message", "Ingen marker med påvist Demand i datasættet.")
            else:
                answer = (
                    f"Topmark for størst behov er {result_dict.get('field_id')} ({result_dict.get('marknummer')}) "
                    f"med kategori {result_dict.get('category')} og måleværdi {result_dict.get('value')} "
                    f"{result_dict.get('unit')}."
                )
        elif result_type == "top_priority":
            answer = "Toplisten er beregnet deterministisk fra priority_score i datasættet."
        else:
            answer = "Svar er afgrænset til deterministisk screening i fase 1."
        return {"answer": answer, "assumptions": [], "out_of_scope": []}

    def explain_result(self, result_dict: Dict[str, Any], question: str) -> Dict[str, Any]:
        whitelist = self._category_whitelist()

        if self.client is None:
            return self._fallback_explain(result_dict)

        messages = [
            {
                "role": "system",
                "content": (
                    "Svar kun i JSON med felterne: answer, assumptions, out_of_scope. "
                    "Brug kun data fra result_dict. Opfind ikke nye kategorier. "
                    "Nævn ikke lovgivning, doser, kg/ha, max/loft, compliance eller timing."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "question": question,
                        "result_dict": result_dict,
                        "allowed_categories": whitelist,
                        "response_schema": {
                            "answer": "string",
                            "assumptions": ["string"],
                            "out_of_scope": ["string"],
                        },
                    },
                    ensure_ascii=False,
                ),
            },
        ]

        try:
            response = self.client.chat.completions.create(
                model=AZURE_DEPLOYMENT,
                messages=messages,
                temperature=0.0,
                max_tokens=500,
            )
            content = response.choices[0].message.content or ""
            parsed = self._parse_json_response(content)
            if not parsed:
                return self._fallback_explain(result_dict)
        except Exception:
            return self._fallback_explain(result_dict)

        answer = _normalize_categories_in_text(str(parsed.get("answer", "")), whitelist)
        assumptions = [
            _normalize_categories_in_text(str(item), whitelist)
            for item in parsed.get("assumptions", [])
            if isinstance(item, (str, int, float))
        ]
        out_of_scope = [
            _normalize_categories_in_text(str(item), whitelist)
            for item in parsed.get("out_of_scope", [])
            if isinstance(item, (str, int, float))
        ]

        answer = sanitize_output(answer)
        assumptions = [sanitize_output(item) for item in assumptions]
        out_of_scope = [sanitize_output(item) for item in out_of_scope]

        return {"answer": answer, "assumptions": assumptions, "out_of_scope": out_of_scope}

    def _format_data_response(self, result: Dict[str, Any], explanation: Dict[str, Any]) -> str:
        result_type = result.get("type")
        lines = []

        if result_type in {"max_nutrient", "most_needed"}:
            if result.get("no_demand"):
                lines.append(result.get("message"))
            elif result.get("error"):
                lines.append("Topmark: Ikke fundet")
            else:
                lines.append(
                    f"Topmark: field_id={result.get('field_id')} | marknummer={result.get('marknummer')} | "
                    f"{result.get('label')}={result.get('value')} {result.get('unit')} | "
                    f"kategori={result.get('category')}"
                )
        elif result_type == "top_priority":
            lines.append("Topliste:")
            for idx, item in enumerate(result.get("items", []), 1):
                lines.append(
                    f"{idx}. field_id={item.get('field_id')} | marknummer={item.get('marknummer')} | "
                    f"priority_score={item.get('priority_score')}"
                )
        else:
            lines.append("Resultat: Ikke understøttet i fase 1.")

        answer = explanation.get("answer", "").strip()
        if answer:
            lines.append(f"Forklaring: {answer}")
        lines.append("Forbehold: Screening, ikke en endelig gødningsplan.")
        return sanitize_output("\n".join(lines))

    def _build_explain_context(self) -> Dict[str, Any]:
        return {
            "type": "explain_context",
            "available_categories": self._category_whitelist(),
            "top_priority": handle_top_priority(self.samples, n=3).get("items", []),
        }

    @staticmethod
    def _extract_top_n(question: str, default: int = 5) -> int:
        match = re.search(r"\b(\d+)\b", question)
        if not match:
            return default
        value = int(match.group(1))
        return value if value > 0 else default

    def ask(self, question: str) -> str:
        q = question.strip()
        intent = classify_intent(q)
        nutrient = detect_nutrient(q)
        q_lower = q.lower()

        if re.search(r"hvilken\s+mark.*har\s+mest", q_lower) and nutrient:
            result = handle_max_nutrient(self.samples, nutrient)
            explanation = self.explain_result(result, q)
            return self._format_data_response(result, explanation)

        if re.search(
            r"hvilken\s+mark.*((kræver|mangler)\s+mest|størst\s+behov|mest\s+behov|højeste\s+behov)",
            q_lower,
        ) and nutrient:
            result = handle_most_needed(self.samples, nutrient)
            explanation = self.explain_result(result, q)
            return self._format_data_response(result, explanation)

        if (
            "prioriter" in q_lower
            or "top" in q_lower
            or re.search(r"hvilke\s+marker.*(størst|højeste|mest)\s+behov", q_lower)
        ):
            top_n = self._extract_top_n(q, default=5)
            result = handle_top_priority(self.samples, n=top_n)
            explanation = self.explain_result(result, q)
            return self._format_data_response(result, explanation)

        if intent == "DATA_QUERY":
            fallback = (
                "Spørgsmålet er klassificeret som DATA_QUERY, men er ikke understøttet i denne fase. "
                "Prøv fx: 'Hvilken mark har størst behov for fosfor?', "
                "'Hvilke marker har størst behov?', eller 'Prioriter de 3 marker'.\n"
                "Forbehold: Screening, ikke en endelig gødningsplan."
            )
            return sanitize_output(fallback)

        if intent == "EXPLAIN_QUERY":
            result = self._build_explain_context()
            explanation = self.explain_result(result, q)
            return sanitize_output(
                f"Svar: {explanation.get('answer')}\n"
                "Forbehold: Screening, ikke en endelig gødningsplan."
            )

        return (
            "Dette spørgsmål ligger uden for fase 1. Jeg kan svare på deterministisk screening "
            "af max/mest behov/top-prioritet.\n"
            "Forbehold: Screening, ikke en endelig gødningsplan."
        )


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python assistant.py <categorized_samples.json>")
        sys.exit(1)

    samples_file = sys.argv[1]
    assistant = FertilizerAssistant(samples_file)

    print("\n=== AI Gødningsassistent ===")
    print("Stil spørgsmål om jordprøverne (eller 'quit' for at afslutte)\n")

    while True:
        question = input("Spørgsmål: ").strip()
        if question.lower() in ["quit", "exit", "q"]:
            break
        if not question:
            continue

        print("\nSvarer...\n")
        print(assistant.ask(question))
        print("\n" + "=" * 60 + "\n")
