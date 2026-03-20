#!/usr/bin/env python3
"""
AI Gødningsscreening — Flask webapp
Upload → gem → søg → vælg marker → analysér → rapport → PDF
"""

import json
import os
import re
import sys
import uuid
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

SRC_DIR = Path(__file__).parent
sys.path.insert(0, str(SRC_DIR))

from flask import Flask, jsonify, render_template, request, flash, redirect, url_for
from dotenv import load_dotenv
from openai import AzureOpenAI, OpenAI

from parsers.soiloptix_parser import SoilOptixParser
from parsers.format_detector import detect_and_create_parser, FormatNotRecognizedError
from analysis.nutrient_categorizer import NutrientCategorizer
from analysis.beregningsgrundlag import beregn_kalkbehov, beregn_jb_nummer
from ai.assistant import FertilizerAssistant

load_dotenv()

# ---------------------------------------------------------------------------
# Konfiguration
# ---------------------------------------------------------------------------

app = Flask(__name__)
app.secret_key = os.urandom(32)

PROJECT_ROOT = Path(__file__).parent.parent
KUNDER_DIR   = PROJECT_ROOT / "data" / "kunder"
UPLOAD_TMP   = PROJECT_ROOT / "tmp" / "uploads"

KUNDER_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_TMP.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".xlsx", ".xls"}

_azure_endpoint   = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip()
_azure_key        = os.getenv("AZURE_OPENAI_KEY", "").strip()
_openai_key       = os.getenv("OPENAI_API_KEY", "").strip()
AZURE_DEPLOYMENT  = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o").strip()

if _azure_endpoint and _azure_key:
    openai_client = AzureOpenAI(
        azure_endpoint=_azure_endpoint,
        api_key=_azure_key,
        api_version="2025-01-01-preview",
    )
elif _openai_key:
    openai_client = OpenAI(api_key=_openai_key)
else:
    openai_client = None

MÅNEDER_DK = [
    "januar","februar","marts","april","maj","juni",
    "juli","august","september","oktober","november","december",
]


# ---------------------------------------------------------------------------
# Kunde-helpers
# ---------------------------------------------------------------------------

def sanitize_navn(navn: str) -> str:
    """Rens kundenavn til et sikkert mappenavn."""
    navn = navn.strip().lower()
    for old, ny in [("æ","ae"),("ø","oe"),("å","aa"),("ä","ae"),("ö","oe"),("ü","ue")]:
        navn = navn.replace(old, ny)
    navn = re.sub(r"[^a-z0-9]+", "_", navn)
    return navn.strip("_") or "ukendt"


def kunde_mappe(mappe_navn: str) -> Path:
    return KUNDER_DIR / mappe_navn


def load_meta(mappe: Path) -> dict:
    f = mappe / "_meta.json"
    if not f.exists():
        return {}
    with open(f, encoding="utf-8") as fh:
        return json.load(fh)


def save_meta(mappe: Path, meta: dict):
    with open(mappe / "_meta.json", "w", encoding="utf-8") as fh:
        json.dump(meta, fh, ensure_ascii=False, indent=2)


def load_samples(mappe: Path) -> list:
    f = mappe / "samples.json"
    if not f.exists():
        return []
    with open(f, encoding="utf-8") as fh:
        return json.load(fh)


def save_samples(mappe: Path, nye: list) -> int:
    """
    Tilføj nye prøver til samples.json.
    Deduplicerer på analyse_nr. Returnerer antal tilføjede.
    """
    mappe.mkdir(parents=True, exist_ok=True)
    eksisterende = load_samples(mappe)

    eks_nrs = {
        s.get("metadata", {}).get("analyse_nr")
        for s in eksisterende
        if s.get("metadata", {}).get("analyse_nr") is not None
    }

    now = datetime.now().isoformat(timespec="seconds")
    added = 0
    for s in nye:
        anr = s.get("metadata", {}).get("analyse_nr")
        if anr is not None and anr in eks_nrs:
            continue
        s["_id"]       = str(uuid.uuid4())
        s["_uploaded"] = now
        eksisterende.append(s)
        added += 1

    with open(mappe / "samples.json", "w", encoding="utf-8") as fh:
        json.dump(eksisterende, fh, ensure_ascii=False, indent=2)
    return added


def search_kunder(q: str) -> list:
    """Find kunder hvis mappenavn eller originalnavn matcher q."""
    q_lower = q.strip().lower()
    if not q_lower or not KUNDER_DIR.exists():
        return []
    result = []
    for d in sorted(KUNDER_DIR.iterdir()):
        if not d.is_dir():
            continue
        meta = load_meta(d)
        navn_orig  = meta.get("navn_original", d.name).lower()
        if q_lower in navn_orig or q_lower in d.name.lower():
            samples = load_samples(d)
            # Letvægts-version til søge-API (ingen measurements)
            samples_light = [
                {
                    "_id":       s.get("_id"),
                    "_uploaded": s.get("_uploaded"),
                    "marknummer": s.get("metadata", {}).get("marknummer"),
                    "field_id":   s.get("metadata", {}).get("field_id"),
                    "analyse_nr": s.get("metadata", {}).get("analyse_nr"),
                }
                for s in samples
            ]
            result.append({
                "mappe":   d.name,
                "navn":    meta.get("navn_original", d.name),
                "samples": samples_light,
            })
    return result


# ---------------------------------------------------------------------------
# Analyse-helpers
# ---------------------------------------------------------------------------

def enrich_sample(sample: dict) -> dict:
    m = sample.setdefault("measurements", {})

    if m.get("jb") is not None:
        try:
            m["jb_nummer"] = int(float(m["jb"]))
        except (TypeError, ValueError):
            pass

    if m.get("jb_nummer") is None:
        ler, silt, finsand, humus = (
            m.get(k) for k in ["ler_pct","silt_pct","finsand_pct","organisk_stof_pct"]
        )
        if all(v is not None for v in [ler, silt, finsand, humus]):
            m["jb_nummer"] = beregn_jb_nummer(
                ler_pct=ler, silt_pct=silt, finsand_pct=finsand, humus_pct=humus
            )

    rt   = m.get("rt")
    ler  = m.get("ler_pct")
    humus = m.get("organisk_stof_pct")
    if rt is not None and ler is not None and humus is not None:
        sample["kalkbehov"] = beregn_kalkbehov(maalt_rt=rt, ler_pct=ler, humus_pct=humus)

    return sample


def process_samples(samples: list) -> list:
    for s in samples:
        try:
            enrich_sample(s)
        except Exception as exc:
            app.logger.warning("enrich_sample fejlede for prøve %s: %s",
                               s.get("metadata", {}).get("analyse_nr"), exc)
        try:
            NutrientCategorizer.categorize_sample(s)
        except Exception as exc:
            app.logger.warning("categorize_sample fejlede: %s", exc)
        s["priority_score"] = NutrientCategorizer.get_field_priority(s)
    samples.sort(key=lambda s: s.get("priority_score", 0), reverse=True)
    return samples


def get_ai_recommendations(samples: list) -> list:
    if not samples or openai_client is None:
        return ["" for _ in samples]

    fields = []
    for i, s in enumerate(samples):
        meta = s.get("metadata", {})
        m    = s.get("measurements", {})
        cats = s.get("categories", {})
        kalk = s.get("kalkbehov", {})
        fields.append({
            "index":            i,
            "marknummer":       meta.get("marknummer") or f"Ukendt",
            "analyse_nr":       meta.get("analyse_nr"),
            "jb_nummer":        m.get("jb_nummer"),
            "rt_maal":          m.get("rt"),
            "rt_kategori":      cats.get("rt"),
            "oensket_rt":       kalk.get("oensket_rt"),
            "kalk_ton_ha":      kalk.get("kalk_ton_per_ha", 0),
            "fosfor_mg_100g":   m.get("fosfor_mg_100g"),
            "fosfor_kategori":  cats.get("fosfor"),
            "kalium_mg_100g":   m.get("kalium_mg_100g"),
            "kalium_kategori":  cats.get("kalium"),
            "magnesium_mg_100g": m.get("magnesium_mg_100g"),
            "magnesium_kategori": cats.get("magnesium"),
        })

    system = (
        "Du er faglig jordrådgiver hos Danish Agro. "
        "Skriv en kort screeeningsanbefaling på dansk for hver mark — max 3 sætninger. "
        "Fokuser på hvilke næringsstoffer der bør undersøges nærmere og om kalk er relevant. "
        "Nævn IKKE konkrete gødningsdoser, kg/ha, produktnavne, lovgivning eller compliance. "
        "Brug altid det faktiske marknummer fra feltet 'marknummer' når du omtaler en mark. "
        "Hvis flere prøver har samme marknummer, skelnes de med prøvenummer (analyse_nr). "
        f'Svar som JSON: {{"anbefalinger": ["tekst for index 0", ..., "tekst for index {len(fields)-1}"]}}'
    )
    user = (
        f"Jordanalysedata for {len(fields)} mark(er):\n\n"
        + json.dumps(fields, ensure_ascii=False, indent=2)
    )

    try:
        max_tok = min(300 * len(fields) + 500, 8000)
        resp = openai_client.chat.completions.create(
            model=AZURE_DEPLOYMENT,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ],
            temperature=0.3,
            max_tokens=max_tok,
            response_format={"type": "json_object"},
        )
        data = json.loads(resp.choices[0].message.content or "{}")
        anbefalinger = data.get("anbefalinger", [])
        if not isinstance(anbefalinger, list):
            anbefalinger = []
    except Exception as exc:
        app.logger.warning("GPT-4o fejlede: %s", exc)
        anbefalinger = []

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
def badge_farve(cat: str) -> str:
    return KATEGORI_BADGE.get(cat, "light")


@app.template_filter("kategori_dk")
def kategori_dk(cat: str) -> str:
    return KATEGORI_DK.get(cat, cat or "—")


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
    if score >= 18: return "danger"
    if score >= 12: return "warning"
    if score >= 6:  return "info"
    return "success"


@app.template_filter("dato_fmt")
def dato_fmt(iso_str: str) -> str:
    if not iso_str:
        return "—"
    try:
        dt = datetime.fromisoformat(iso_str)
        return f"{dt.day}. {MÅNEDER_DK[dt.month - 1]} {dt.year}"
    except (ValueError, IndexError):
        return iso_str[:10]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/")
def index():
    q = request.args.get("q", "")
    return render_template("index.html", ai_aktiv=openai_client is not None, q=q)


@app.get("/api/kunder")
def api_kunder():
    q = request.args.get("q", "").strip()
    return jsonify(search_kunder(q))


@app.post("/upload")
def upload():
    kundenavn_raw = request.form.get("kundenavn", "").strip()
    if not kundenavn_raw:
        flash("Angiv venligst et kundenavn.", "danger")
        return redirect(url_for("index"))

    if "fil" not in request.files:
        flash("Ingen fil valgt.", "danger")
        return redirect(url_for("index"))

    fil = request.files["fil"]
    if not fil.filename or Path(fil.filename).suffix.lower() not in ALLOWED_EXTENSIONS:
        flash("Filen skal være .xlsx eller .xls.", "danger")
        return redirect(url_for("index"))

    mappe_navn = sanitize_navn(kundenavn_raw)
    mappe      = kunde_mappe(mappe_navn)

    tmp_path = UPLOAD_TMP / fil.filename
    fil.save(tmp_path)

    try:
        parser = detect_and_create_parser(str(tmp_path))
        samples = parser.parse()
    except FormatNotRecognizedError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("index"))
    except Exception as exc:
        flash(f"Kunne ikke parse Excel-filen: {exc}", "danger")
        return redirect(url_for("index"))
    finally:
        tmp_path.unlink(missing_ok=True)

    if not samples:
        flash("Ingen prøver fundet i filen. Tjek at det er en SoilOptix-fil.", "warning")
        return redirect(url_for("index"))

    added = save_samples(mappe, samples)

    meta = load_meta(mappe)
    if not meta:
        meta["oprettet"] = datetime.now().isoformat(timespec="seconds")
    meta["navn_original"]    = kundenavn_raw
    meta["sidst_opdateret"]  = datetime.now().isoformat(timespec="seconds")
    save_meta(mappe, meta)

    flash(
        f"{added} ny(e) mark(er) gemt for <strong>{kundenavn_raw}</strong>.",
        "success",
    )
    return redirect(url_for("index") + "?q=" + quote(kundenavn_raw))


@app.post("/analyse")
def analyse():
    # Checkbox-værdier: "<mappe_navn>/<_id>"
    valgte = request.form.getlist("ids")
    if not valgte:
        flash("Vælg mindst én mark.", "warning")
        return redirect(url_for("index"))

    # Gruppér per kunde-mappe
    kunde_ids: dict[str, set] = {}
    for val in valgte:
        if "/" in val:
            mappe_navn, sid = val.split("/", 1)
            kunde_ids.setdefault(mappe_navn, set()).add(sid)

    samples = []
    kundenavn_display = ""
    first_mappe = ""
    for mappe_navn, ids in kunde_ids.items():
        mappe   = kunde_mappe(mappe_navn)
        meta_k  = load_meta(mappe)
        alle    = load_samples(mappe)
        if not kundenavn_display:
            kundenavn_display = meta_k.get("navn_original", mappe_navn)
            first_mappe = mappe_navn
        for s in alle:
            if s.get("_id") in ids:
                samples.append(s)

    if not samples:
        flash("Kunne ikke finde de valgte marker.", "danger")
        return redirect(url_for("index"))

    try:
        samples = process_samples(samples)
    except Exception as exc:
        app.logger.error("process_samples fejlede: %s", exc, exc_info=True)
        flash(f"Fejl ved behandling af prøver: {exc}", "danger")
        return redirect(url_for("index"))

    anbefalinger = get_ai_recommendations(samples)

    kalk_count = sum(
        1 for s in samples
        if (s.get("kalkbehov") or {}).get("kalk_ton_per_ha", 0) > 0
    )

    dt   = datetime.now()
    dato = f"{dt.day}. {MÅNEDER_DK[dt.month - 1]} {dt.year}"

    return render_template(
        "report.html",
        samples=samples,
        anbefalinger=anbefalinger,
        kundenavn=kundenavn_display,
        kundenavn_mappe=first_mappe,
        kalk_count=kalk_count,
        ai_aktiv=openai_client is not None,
        dato=dato,
    )


@app.post("/chat")
def chat():
    data = request.get_json(silent=True) or {}
    question      = (data.get("question") or "").strip()
    mappe_navn    = (data.get("kundenavn_mappe") or "").strip()

    if not question:
        return jsonify({"error": "Spørgsmål mangler."}), 400
    if not mappe_navn:
        return jsonify({"error": "Kundenavn mangler."}), 400

    mappe   = kunde_mappe(mappe_navn)
    samples = load_samples(mappe)
    if not samples:
        return jsonify({"error": "Ingen marker fundet for denne kunde."}), 404

    samples = process_samples(samples)
    assistant = FertilizerAssistant.from_samples(
        samples, api_key=os.getenv("OPENAI_API_KEY")
    )
    answer = assistant.ask(question)
    return jsonify({"answer": answer})


# ---------------------------------------------------------------------------
# Start
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if openai_client is None:
        print("⚠️  OPENAI_API_KEY ikke sat — AI-anbefalinger deaktiveret")
    print("🌱 AI Gødningsscreening starter på http://127.0.0.1:5001")
    app.run(debug=True, host="127.0.0.1", port=5001)
