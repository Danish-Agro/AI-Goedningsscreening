"""
beregningsgrundlag.py
=====================
Alle beregningskonstanter til AI Gødningsscreening.

Kilde: AI_beregningsgrundlag_til_behovsberegning.xlsx (marts 2026)
       Jonas_Kategorier_for_næringsstofindhold.xlsx

Ingen Excel-filer læses runtime — alt er hardkodet her.
Opdater denne fil hvis faglige grænseværdier ændres.
"""

from __future__ import annotations
from typing import Optional


# ---------------------------------------------------------------------------
# 1. JB-NUMMER KLASSIFIKATION
#    Kilde: Jonas_Jord_klassificering_DK.docx
#    Parametre: ler < 2µm (%), silt 2-20µm (%), finsand 20-200µm (%), humus (kulstof %)
# ---------------------------------------------------------------------------

def beregn_jb_nummer(ler_pct: float, silt_pct: float, finsand_pct: float, humus_pct: float) -> int:
    """
    Beregn JB-nummer (1-11) fra teksturdata.
    Returnerer JB-nummer som heltal.
    """
    # JB11: Humusjord (organisk kulstof > 6%)
    if humus_pct > 6.0:
        return 11

    # JB10: Siltjord — silt > hvad ler-klassen ellers ville give
    if silt_pct >= 20:
        return 10

    # JB9: Meget svær lerjord
    if ler_pct >= 45:
        return 9

    # JB8: Svær lerjord
    if ler_pct >= 25:
        return 8

    # JB7: Lerjord
    if ler_pct >= 15:
        return 7

    # JB5/JB6: Sandblandet lerjord (10-14.9% ler)
    if ler_pct >= 10:
        if finsand_pct >= 40:
            return 6  # Fin sandbl. lerjord
        return 5      # Grov sandbl. lerjord

    # JB3/JB4: Lerblandet sandjord (5-9.9% ler)
    if ler_pct >= 5:
        if finsand_pct >= 40:
            return 4  # Fin lerbl. sandjord
        return 3      # Grov lerbl. sandjord

    # JB1/JB2: Sandjord (0-4.9% ler)
    if finsand_pct >= 50:
        return 2  # Finsandet jord
    return 1      # Grovsandet jord


def jb_gruppe_fosfor(jb: int) -> str:
    """Returner fosfor-gruppenavn baseret på JB-nummer."""
    if jb in (1, 3):
        return "JB1_JB3"
    if jb == 11:
        return "JB11"
    return "JB2_JB4_10"   # JB2, JB4-JB10 — standardgruppe


def jb_gruppe_kalium(jb: int) -> str:
    """Returner kalium-gruppenavn baseret på JB-nummer."""
    if jb <= 4:
        return "JB1_4"
    return "over_JB4"


# ---------------------------------------------------------------------------
# 2. NÆRINGSSTOFKATEGORIER
#    Kilde: AI_beregningsgrundlag_til_behovsberegning.xlsx — sheet "Næringsstofbehov"
#
#    Format per parameter/jordtype:
#      kategori -> (min_inkl, max_ekskl)  — float("inf") for ingen øvre grænse
#      "enhed_per_ha" -> kg næringsstof pr. ha for at flytte 1 enhed
# ---------------------------------------------------------------------------

KATEGORIER_MG = {
    # Magnesium — jordtype-uafhængig
    "alle": {
        "Large Demand":       (0.0,   2.0),
        "Medium Demand":      (2.0,   3.0),
        "Small Demand":       (3.0,   4.0),
        "OK":                 (4.0,   6.0),
        "Small Surplus":      (6.0,   8.0),
        "Large Surplus":      (8.0,  10.0),
        "Suspicious Surplus": (10.0, float("inf")),
        "enhed_per_ha": 25,
    }
}

KATEGORIER_FOSFOR = {
    # JB1 og JB3 — grovsandede jorde
    "JB1_JB3": {
        "Large Demand":       (0.0,  1.0),
        "Medium Demand":      (1.0,  2.0),
        "Small Demand":       (2.0,  3.0),
        "OK":                 (3.0,  5.0),
        "Small Surplus":      (5.0,  7.0),
        "Large Surplus":      (7.0,  8.0),
        "Suspicious Surplus": (8.0, float("inf")),
        "enhed_per_ha": 25,
    },
    # JB2, JB4-JB10 — finsandede og lerede jorde (standardgruppe)
    "JB2_JB4_10": {
        "Large Demand":       (0.0,  1.0),
        "Medium Demand":      (1.0,  1.5),
        "Small Demand":       (1.5,  2.0),
        "OK":                 (2.0,  4.0),
        "Small Surplus":      (4.0,  5.0),
        "Large Surplus":      (5.0,  6.0),
        "Suspicious Surplus": (6.0, float("inf")),
        "enhed_per_ha": 30,
    },
    # JB11 — humusjord
    "JB11": {
        "Large Demand":       (0.0,   0.75),
        "Medium Demand":      (0.75,  1.25),
        "Small Demand":       (1.25,  1.75),
        "OK":                 (1.75,  2.5),
        "Small Surplus":      (2.5,   3.25),
        "Large Surplus":      (3.25,  4.0),
        "Suspicious Surplus": (4.0,  float("inf")),
        "enhed_per_ha": 25,
    },
}

KATEGORIER_KALIUM = {
    # JB1-JB4 — sandjorde
    "JB1_4": {
        "Large Demand":       (0.0,   3.0),
        "Medium Demand":      (3.0,   5.0),
        "Small Demand":       (5.0,   6.0),
        "OK":                 (6.0,   8.0),
        "Small Surplus":      (8.0,  10.0),
        "Large Surplus":      (10.0, 12.0),
        "Suspicious Surplus": (12.0, float("inf")),
        "enhed_per_ha": 25,
    },
    # Over JB4 — lerjorde
    "over_JB4": {
        "Large Demand":       (0.0,   4.0),
        "Medium Demand":      (4.0,   5.5),
        "Small Demand":       (5.5,   7.0),
        "OK":                 (7.0,  10.0),
        "Small Surplus":      (10.0, 12.5),
        "Large Surplus":      (12.5, 15.0),
        "Suspicious Surplus": (15.0, float("inf")),
        "enhed_per_ha": 30,
    },
}

KATEGORIER_RT = {
    # Reaktionstal — jordtype-uafhængig
    "alle": {
        "Large Demand":       (0.0,  4.5),
        "Medium Demand":      (4.5,  5.0),
        "Small Demand":       (5.0,  6.0),
        "OK":                 (6.0,  6.5),
        "Small Surplus":      (6.5,  7.0),
        "Large Surplus":      (7.0,  8.0),
        "Suspicious Surplus": (8.0, float("inf")),
    }
}

# Mikroelementer fra Jonas_Kategorier (Cu, B, Zn) — jordtype-uafhængig
KATEGORIER_CU = {
    "alle": {
        "Large Demand":       (0.0, 1.0),
        "Medium Demand":      (1.0, 1.5),
        "Small Demand":       (1.5, 2.0),
        "OK":                 (2.0, 3.0),
        "Small Surplus":      (3.0, 4.0),
        "Large Surplus":      (4.0, 5.0),
        "Suspicious Surplus": (5.0, float("inf")),
    }
}

KATEGORIER_B = {
    "alle": {
        "Large Demand":       (0.0,  1.5),
        "Medium Demand":      (1.5,  2.5),
        "Small Demand":       (2.5,  3.0),
        "OK":                 (3.0,  5.0),
        "Small Surplus":      (5.0,  6.5),
        "Large Surplus":      (6.5,  8.0),
        "Suspicious Surplus": (8.0, float("inf")),
    }
}


# ---------------------------------------------------------------------------
# 3. KATEGORISERINGSFUNKTIONER
# ---------------------------------------------------------------------------

def _kategoriser(value: float, tabel: dict) -> str:
    """Intern hjælpefunktion: find kategori for en værdi i en kategoritabel."""
    for kategori, (low, high) in tabel.items():
        if kategori == "enhed_per_ha":
            continue
        if low <= value < high:
            return kategori
    return "Suspicious Surplus"


def kategoriser_mg(value: float) -> str:
    return _kategoriser(value, KATEGORIER_MG["alle"])


def kategoriser_fosfor(value: float, jb: int) -> str:
    gruppe = jb_gruppe_fosfor(jb)
    return _kategoriser(value, KATEGORIER_FOSFOR[gruppe])


def kategoriser_kalium(value: float, jb: int) -> str:
    gruppe = jb_gruppe_kalium(jb)
    return _kategoriser(value, KATEGORIER_KALIUM[gruppe])


def kategoriser_rt(value: float) -> str:
    return _kategoriser(value, KATEGORIER_RT["alle"])


def enhed_per_ha_fosfor(jb: int) -> int:
    """Returner kg P/ha der skal til for at flytte Pt én enhed (til brug i behovsberegning)."""
    return KATEGORIER_FOSFOR[jb_gruppe_fosfor(jb)]["enhed_per_ha"]


def enhed_per_ha_kalium(jb: int) -> int:
    """Returner kg K/ha der skal til for at flytte Kt én enhed."""
    return KATEGORIER_KALIUM[jb_gruppe_kalium(jb)]["enhed_per_ha"]


# ---------------------------------------------------------------------------
# 4. KALKMODEL
#    Kilde: AI_beregningsgrundlag_til_behovsberegning.xlsx — sheet "Kalkmodel"
#
#    To polynomiske regressionsmodeller (3. grad, bivariat: humus og ler):
#      Model A: beregner ønsket Rt ud fra ler% og humus%
#      Model B: beregner mængde kalk (ton CaCO3/ha) til at hæve Rt 0.1 enhed
#
#    Generel polynom: f(h, l) = a1 + a2·h + a3·l + a4·h² + a5·h·l + a6·l²
#                              + a7·h³ + a8·h²·l + a9·h·l² + a10·l³
#    hvor h = humus%, l = ler%
# ---------------------------------------------------------------------------

# Model A — ønsket Rt
KALK_KOEFF_OENSKET_RT = [
    5.953765588288088,
    -0.09979267833872163,
    0.05901992772237292,
    -3.212608547869953e-05,
    -0.0002969818760893357,
    -0.00017144955982255624,
    1.4052691771363737e-05,
    -6.265521470965284e-06,
    1.3204434209953755e-05,
    3.5087203896020195e-06,
]

# Model B — ton CaCO3/ha for at hæve Rt 0.1 enhed
KALK_KOEFF_MAENGDE = [
    0.307076054088537,
    0.06737739260063064,
    0.015897893362788008,
    0.0026915586583327322,
    -0.0006998658884219493,
    6.192057614409439e-05,
    -0.00019639785725971128,
    6.331880016917565e-05,
    -6.291828139642122e-06,
    1.19244514714228e-05,
]

KALK_MAX_LER_PCT = 30.0
KALK_MIN_RT_DIFF = 0.10
KALK_MIN_TON_PER_HA = 2.0


def _polynom(humus: float, ler: float, koeff: list) -> float:
    """Evaluer bivariat polynomisk model af 3. grad."""
    h, l = humus, ler
    a = koeff
    return (
        a[0]
        + a[1] * h
        + a[2] * l
        + a[3] * h**2
        + a[4] * h * l
        + a[5] * l**2
        + a[6] * h**3
        + a[7] * h**2 * l
        + a[8] * h * l**2
        + a[9] * l**3
    )


def _ler_pct_til_kalkmodel(ler_pct: float) -> float:
    """Begræns lerprocenten til kalkmodellens validerede område."""
    return min(max(float(ler_pct), 0.0), KALK_MAX_LER_PCT)


def beregn_oensket_rt(ler_pct: float, humus_pct: float) -> float:
    """Beregn ønsket Rt baseret på jordtype (ler% og humus%)."""
    return _polynom(humus_pct, _ler_pct_til_kalkmodel(ler_pct), KALK_KOEFF_OENSKET_RT)


def beregn_kalk_maengde_per_0_1_rt(ler_pct: float, humus_pct: float) -> float:
    """Beregn ton CaCO3/ha der skal til for at hæve Rt med 0.1 enhed."""
    return _polynom(humus_pct, _ler_pct_til_kalkmodel(ler_pct), KALK_KOEFF_MAENGDE)


def beregn_kalkbehov(maalt_rt: float, ler_pct: float, humus_pct: float) -> dict:
    """
    Beregn samlet kalkbehov.

    Returner dict med:
      - oensket_rt: float — målværdi for Rt
      - rt_difference: float — forskel mellem ønsket og målt
      - kalk_ton_per_ha: float — ton CaCO3/ha der skal tilføres
      - kategori: str — Rt-kategori for den målte værdi
    """
    ler_pct_anvendt = _ler_pct_til_kalkmodel(ler_pct)
    ler_pct_begraenset = ler_pct_anvendt != float(ler_pct)
    oensket_rt = beregn_oensket_rt(ler_pct_anvendt, humus_pct)
    rt_diff = oensket_rt - maalt_rt
    note = None

    if rt_diff < KALK_MIN_RT_DIFF:
        kalk = 0.0
        status = "intet_behov"
        if rt_diff > 0:
            note = (
                f"Forskel på Rt er under bagatelgrænsen på {KALK_MIN_RT_DIFF:.1f}; "
                "der vises derfor ikke kalkbehov."
            )
    else:
        maengde_per_0_1 = beregn_kalk_maengde_per_0_1_rt(ler_pct_anvendt, humus_pct)
        beregnet_kalk = max((rt_diff / 0.1) * maengde_per_0_1, 0.0)
        if beregnet_kalk < KALK_MIN_TON_PER_HA:
            kalk = 0.0
            status = "bagatel"
            note = (
                f"Beregnet kalkbehov er under {KALK_MIN_TON_PER_HA:.1f} t/ha "
                "og behandles som bagatel i screeningen."
            )
        else:
            kalk = beregnet_kalk
            status = "behov"

    if rt_diff < KALK_MIN_RT_DIFF:
        beregnet_kalk = 0.0

    if ler_pct_begraenset:
        ler_note = f"Lerprocenten er begrænset til {KALK_MAX_LER_PCT:.0f}% i kalkmodellen."
        note = f"{ler_note} {note}" if note else ler_note

    return {
        "maalt_rt": round(maalt_rt, 1),
        "oensket_rt": round(oensket_rt, 1),
        "rt_difference": round(rt_diff, 2),
        "beregnet_kalk_ton_per_ha": round(max(beregnet_kalk, 0.0), 2),
        "kalk_ton_per_ha": round(max(kalk, 0.0), 2),
        "kategori_rt": kategoriser_rt(maalt_rt),
        "status": status,
        "note": note,
        "ler_pct_anvendt": round(ler_pct_anvendt, 1),
        "ler_pct_begraenset": ler_pct_begraenset,
    }


# ---------------------------------------------------------------------------
# 5. AFGRØDEDATA
#    Kilde: Exel_Danish_Agro_screening_AI_gødningsplan.xlsx
# ---------------------------------------------------------------------------

UDBYTTENIVEAUER = {
    "Vinterkorn":          {"Lavt": "<60 hkg",  "Mellem": "60-75 hkg", "Højt": ">75 hkg"},
    "Vårkorn":             {"Lavt": "<50 hkg",  "Mellem": "50-65 hkg", "Højt": ">65 hkg"},
    "Alm. rajgræs (frø)": {"Lavt": "<10 hkg",  "Mellem": "10-15 hkg", "Højt": ">15 hkg"},
    "Vinterraps":          {"Lavt": "<40 hkg",  "Mellem": "40-50 hkg", "Højt": ">50 hkg"},
    "Bælgsæd":             {"Lavt": "<40 hkg",  "Mellem": "40-55 hkg", "Højt": ">55 hkg"},
}

# N-tilførsel ranges (kg N/ha) per afgrøde — listede i stigende rækkefølge
N_RANGES = {
    "Vinterkorn":          ["140-160", "160-180", "180-200", "200-220", "220-240"],
    "Vårkorn":             ["100-120", "120-140", "140-160"],
    "Alm. rajgræs (frø)": ["100-120", "120-140", "140-160", "160-180"],
    "Vinterraps":          ["160-180", "180-200", "200-220"],
    "Bælgsæd":             ["0 kg"],
}

# S-behov (kg S/ha) per N-range
# Format: N-range -> S-behov (min, max)
S_BEHOV = {
    "100-120": (9,  15),
    "120-140": (11, 17),
    "140-160": (13, 19),
    "160-180": (15, 21),
    "180-200": (17, 23),
    "200-220": (19, 25),
    "220-240": (21, 27),
    "0 kg":    (0,  0),
}


def s_behov_for_n(n_range: str) -> tuple[int, int]:
    """Returner (min, max) kg S/ha for et givet N-range."""
    return S_BEHOV.get(n_range.strip(), (0, 0))


# ---------------------------------------------------------------------------
# 6. HURTIG SELVTEST — kør filen direkte for at validere konstanter
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== Selvtest af beregningsgrundlag ===\n")

    # JB-nummer
    jb = beregn_jb_nummer(ler_pct=15.9, silt_pct=13.9, finsand_pct=55.4, humus_pct=2.13)
    print(f"Mark 6-0 (15.9% ler, 55.4% finsand, 2.13% humus) → JB{jb}")

    # Fosfor kategorisering
    p_kat = kategoriser_fosfor(2.6, jb)
    print(f"Fosfor 2.6 mg/100g på JB{jb} → {p_kat}")

    # Kalium kategorisering
    k_kat = kategoriser_kalium(12.0, jb)
    print(f"Kalium 12.0 mg/100g på JB{jb} → {k_kat}")

    # Rt kategorisering
    rt_kat = kategoriser_rt(7.8)
    print(f"Rt 7.8 → {rt_kat}")

    # Kalkbehov
    kalk = beregn_kalkbehov(maalt_rt=5.8, ler_pct=15.9, humus_pct=2.13)
    print(f"\nKalkbehov (Rt=5.8, 15.9% ler, 2.13% humus):")
    for k, v in kalk.items():
        print(f"  {k}: {v}")

    # S-behov
    s_min, s_max = s_behov_for_n("160-180")
    print(f"\nS-behov ved 160-180 kg N/ha: {s_min}-{s_max} kg S/ha")

    print("\n✓ Alle beregninger gennemført uden fejl")
