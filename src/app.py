#!/usr/bin/env python3
"""
AI Gødningsscreening — Flask webapp
Upload SoilOptix lab-Excel → parse → kategoriser → GPT-4o anbefaling → HTML-rapport
"""

import json
import os
import sys
from pathlib import Path

# Gør src/-pakker importerbare uanset CWD
SRC_DIR = Path(__file__).parent
sys.path.insert(0, str(SRC_DIR))

from flask import Flask, render_template, request, flash, redirect, url_for
from dotenv import load_dotenv
from openai import OpenAI

from parsers.soiloptix_parser import SoilOptixParser
from analysis.nutrient_categorizer import NutrientCategorizer
from analysis.beregningsgrundlag import beregn_kalkbehov, beregn_jb_nummer

load_dotenv()

# ---------------------------------------------------------------------------
# App-konfiguration
# ---------------------------------------------------------------------------

app = Flask(__name__)
app.secret_key = os.urandom(32)

UPLOAD_FOLDER = Path(__file__).parent.parent / "tmp" / "uploads"
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".xlsx", ".xls"}

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) if os.getenv("OPENAI_API_KEY") else None


# ---------------------------------------------------------------------------
# Hjælpefunktioner
# ---------------------------------------------------------------------------

def _allowed(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def enrich_sample(sample: dict) -> dict:
    """
    Tilføj jb_nummer og kalkbehov til prøven.
    Parseren gemmer JB som measurements.jb; NutrientCategorizer forventer jb_nummer.
    """
    m = sample.setdefault("measurements", {})

    # Bridge: parseret 'jb' → 'jb_nummer'
    if m.get("jb") is not None:
        try:
            m["jb_nummer"] = int(float(m["jb"]))
        except (TypeError, ValueError):
            pass

    # Fallback: beregn JB fra teksturdata
    if m.get("jb_nummer") is None:
        ler = m.get("ler_pct")
        silt = m.get("silt_pct")
        finsand = m.get("finsand_pct")
        humus = m.get("organisk_stof_pct")
        if all(v is not None for v in [ler, silt, finsand, humus]):
            m["jb_nummer"] = beregn_jb_nummer(
                ler_pct=ler, silt_pct=silt, finsand_pct=finsand, humus_pct=humus
            )

    # Kalkbehov
    rt = m.get("rt")
    ler = m.get("ler_pct")
    humus = m.get("organisk_stof_pct")
    if rt is not None and ler is not None and humus is not None:
        sample["kalkbehov"] = beregn_kalkbehov(maalt_rt=rt, ler_pct=ler, humus_pct=humus)

    return sample


def process_samples(samples: list) -> list:
    """Berig, kategoriser og prioriter alle prøver."""
    for sample in samples:
        enrich_sample(sample)
        NutrientCategorizer.categorize_sample(sample)
        sample["priority_score"] = NutrientCategorizer.get_field_priority(sample)

    samples.sort(key=lambda s: s.get("priority_score", 0), reverse=True)
    return samples


def get_ai_recommendations(samples: list) -> list[str]:
    """
    Send alle marker til GPT-4o i ét kald.
    Returnerer liste af anbefalinger i samme rækkefølge som samples.
    Returnerer tomme strenge hvis API-nøgle mangler eller kald fejler.
    """
    if not samples or openai_client is None:
        return ["" for _ in samples]

    fields = []
    for i, s in enumerate(samples):
        meta = s.get("metadata", {})
        m = s.get("measurements", {})
        cats = s.get("categories", {})
        kalk = s.get("kalkbehov", {})
        fields.append({
            "index": i,
            "marknummer": meta.get("marknummer") or f"Mark {i + 1}",
            "jb_nummer": m.get("jb_nummer"),
            "rt_maal": m.get("rt"),
            "rt_kategori": cats.get("rt"),
            "oensket_rt": kalk.get("oensket_rt"),
            "kalk_ton_ha": kalk.get("kalk_ton_per_ha", 0),
            "fosfor_mg_100g": m.get("fosfor_mg_100g"),
            "fosfor_kategori": cats.get("fosfor"),
            "kalium_mg_100g": m.get("kalium_mg_100g"),
            "kalium_kategori": cats.get("kalium"),
            "magnesium_mg_100g": m.get("magnesium_mg_100g"),
            "magnesium_kategori": cats.get("magnesium"),
            "prioritet_score": s.get("priority_score", 0),
        })

    system = (
        "Du er faglig jordrådgiver hos Danish Agro. "
        "Skriv en kort screeeningsanbefaling på dansk for hver mark — max 3 sætninger. "
        "Fokuser på hvilke næringsstoffer der bør undersøges nærmere og om kalk er relevant. "
        "Nævn IKKE konkrete gødningsdoser, kg/ha, produktnavne, lovgivning eller compliance. "
        "Svar som JSON: {\"anbefalinger\": [\"tekst mark 0\", \"tekst mark 1\", ...]}"
    )

    user = (
        f"Jordanalysedata for {len(fields)} mark(er) — svar med præcis {len(fields)} anbefalinger:\n\n"
        + json.dumps(fields, ensure_ascii=False, indent=2)
    )

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.3,
            max_tokens=3000,
            response_format={"type": "json_object"},
        )
        data = json.loads(response.choices[0].message.content or "{}")
        anbefalinger = data.get("anbefalinger", [])
    except Exception as exc:
        app.logger.warning("GPT-4o kald fejlede: %s", exc)
        anbefalinger = []

    # Sørg for korrekt længde
    while len(anbefalinger) < len(samples):
        anbefalinger.append("Ingen AI-anbefaling tilgængelig.")
    return anbefalinger[: len(samples)]


# ---------------------------------------------------------------------------
# Template-filtre
# ---------------------------------------------------------------------------

KATEGORI_BADGE = {
    "Large Demand":       "danger",
    "Medium Demand":      "warning",
    "Small Demand":       "info",
    "OK":                 "success",
    "Small Surplus":      "secondary",
    "Large Surplus":      "secondary",
    "Suspicious Surplus": "dark",
}

KATEGORI_DK = {
    "Large Demand":       "Stort behov",
    "Medium Demand":      "Middel behov",
    "Small Demand":       "Lille behov",
    "OK":                 "OK",
    "Small Surplus":      "Lille overskud",
    "Large Surplus":      "Stort overskud",
    "Suspicious Surplus": "Mistænkt overskud",
}


@app.template_filter("badge_farve")
def badge_farve(category: str) -> str:
    return KATEGORI_BADGE.get(category, "light")


@app.template_filter("kategori_dk")
def kategori_dk(category: str) -> str:
    return KATEGORI_DK.get(category, category or "—")


@app.template_filter("fmt")
def fmt_float(value, decimals: int = 1) -> str:
    if value is None:
        return "—"
    try:
        return f"{float(value):.{decimals}f}"
    except (TypeError, ValueError):
        return str(value)


@app.template_filter("prioritet_farve")
def prioritet_farve(score: int) -> str:
    if score >= 18:
        return "danger"
    if score >= 12:
        return "warning"
    if score >= 6:
        return "info"
    return "success"


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/")
def upload_form():
    return render_template("upload.html")


@app.post("/analyse")
def analyse():
    if "fil" not in request.files:
        flash("Ingen fil valgt.", "danger")
        return redirect(url_for("upload_form"))

    fil = request.files["fil"]
    if not fil.filename or not _allowed(fil.filename):
        flash("Filen skal være en Excel-fil (.xlsx eller .xls).", "danger")
        return redirect(url_for("upload_form"))

    # Gem filen midlertidigt
    dest = UPLOAD_FOLDER / fil.filename
    fil.save(dest)

    try:
        parser = SoilOptixParser(str(dest))
        parser.load()
        samples = parser.parse()
    except Exception as exc:
        flash(f"Kunne ikke parse Excel-filen: {exc}", "danger")
        return redirect(url_for("upload_form"))
    finally:
        dest.unlink(missing_ok=True)  # Slet uploaded fil med det samme

    if not samples:
        flash("Ingen prøver fundet i filen. Tjek at det er en SoilOptix-fil.", "warning")
        return redirect(url_for("upload_form"))

    samples = process_samples(samples)
    anbefalinger = get_ai_recommendations(samples)

    # Antal marker med kalkbehov > 0
    kalk_count = sum(
        1 for s in samples if (s.get("kalkbehov") or {}).get("kalk_ton_per_ha", 0) > 0
    )

    return render_template(
        "report.html",
        samples=samples,
        anbefalinger=anbefalinger,
        filnavn=fil.filename,
        kalk_count=kalk_count,
        ai_aktiv=openai_client is not None,
    )


# ---------------------------------------------------------------------------
# Start
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if openai_client is None:
        print("⚠️  OPENAI_API_KEY ikke sat — AI-anbefalinger deaktiveret")
    print("🌱 AI Gødningsscreening starter på http://127.0.0.1:5001")
    app.run(debug=True, host="127.0.0.1", port=5001)
