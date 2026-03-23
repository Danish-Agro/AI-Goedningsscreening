"""
seges_normer.py
---------------
Faglige konstanter fra SEGES-publikationen:
"Jordbundsanalyser - Hvad gemmer sig bag tallene?" (2021)

Kilde: Landbrug & Fødevarer F.m.b.A. / SEGES, PlanteInnovation
Anvendes som datagrundlag i Danish Agros AI-gødningsscreening.
"""

# ---------------------------------------------------------------------------
# KLASSE-DEFINITIONER (generelle for alle næringsstoffer)
# ---------------------------------------------------------------------------

KLASSE_BESKRIVELSER = {
    "Meget lavt": (
        "Akut mangel kan forventes. Absolut nødvendigt at hæve indholdet — "
        "f.eks. ved engangstilførsel af en større mængde næringsstof."
    ),
    "Lavt": (
        "Næringsstoffet kan være begrænsende for udbyttet. Indholdet bør hæves "
        "ved at tilføre mere end bortførslen med afgrøderne."
    ),
    "Middel": (
        "Det tilstræbte indhold. Gødningsanbefalingerne er afpasset efter dette niveau. "
        "Tilførsel afstemmes efter planternes bortførsel samt tab ved udvaskning."
    ),
    "Højt": (
        "Højere end nødvendigt for optimal plantevækst. "
        "Der kan tæres på jordens reserver ved at tilføre mindre end bortførslen."
    ),
    "Meget højt": (
        "Kan hæmme planteproduktionen og give unødvendigt tab til miljøet. "
        "Indholdet bør bringes ned — undlad næringsstoftilførsel."
    ),
}

KLASSE_RÆKKEFØLGE = ["Meget lavt", "Lavt", "Middel", "Højt", "Meget højt"]

# ---------------------------------------------------------------------------
# FOSFORTAL (Pt)
# Enhed: mg P / 100g jord  (= Pt-enheder, 1 Pt = 10 ppm = 25 kg P/ha)
# To rækker i SEGES-tabellen afhængig af JB-nummer
# ---------------------------------------------------------------------------

PT_KLASSER = {
    # JB 2,4–11,0 (de fleste sandede og lerede jorde)
    "standard": [
        {"klasse": "Meget lavt",  "min": 0.0,  "max": 1.0},
        {"klasse": "Lavt",        "min": 1.0,  "max": 2.0},
        {"klasse": "Middel",      "min": 2.1,  "max": 4.0},
        {"klasse": "Højt",        "min": 4.1,  "max": 6.0},
        {"klasse": "Meget højt",  "min": 6.0,  "max": float("inf")},
    ],
    # JB 1,3 (grovsandet / meget let jord)
    "jb1_3": [
        {"klasse": "Meget lavt",  "min": 0.0,  "max": 2.0},
        {"klasse": "Lavt",        "min": 2.0,  "max": 3.0},
        {"klasse": "Middel",      "min": 3.0,  "max": 5.0},
        {"klasse": "Højt",        "min": 5.0,  "max": 7.0},
        {"klasse": "Meget højt",  "min": 7.0,  "max": float("inf")},
    ],
}

PT_ENHEDER = {
    "ppm_per_enhed": 10,
    "kg_ha_per_enhed": 25,
    "beskrivelse": "1 Pt-enhed = 10 ppm = ca. 25 kg P/ha i pløjelaget",
}

PT_FAGLIG_NOTE = (
    "Fosfor bevæger sig meget langsomt i jorden og optages kun inden for 2 mm fra roden. "
    "Kravet til fosforindhold er størst på jorde med dårlig rodudvikling (grovsand, dårlig struktur). "
    "Ved middelhøje fosfortal tilføres ca. 15–30 kg P/ha/år svarende til afgrødernes bortførsel. "
    "Meget høje fosfortal øger risiko for tab til vandmiljøet."
)

# ---------------------------------------------------------------------------
# KALIUMTAL (Kt)
# Enhed: mg K / 100g jord  (1 Kt-enhed = 10 ppm = 25 kg K/ha)
# To rækker afhængig af JB < 4 eller JB >= 4
# ---------------------------------------------------------------------------

KT_KLASSER = {
    # Lette jorde: JB < 4 (sandjord med lav lerindhold)
    "let_jord": [
        {"klasse": "Meget lavt",  "min": 0.0,   "max": 3.0},
        {"klasse": "Lavt",        "min": 3.0,   "max": 5.0},
        {"klasse": "Middel",      "min": 5.1,   "max": 8.0},
        {"klasse": "Højt",        "min": 8.1,   "max": 12.0},
        {"klasse": "Meget højt",  "min": 12.0,  "max": float("inf")},
    ],
    # Tungere jorde: JB >= 4
    "tung_jord": [
        {"klasse": "Meget lavt",  "min": 0.0,   "max": 4.0},
        {"klasse": "Lavt",        "min": 4.0,   "max": 7.0},
        {"klasse": "Middel",      "min": 7.1,   "max": 10.0},
        {"klasse": "Højt",        "min": 10.1,  "max": 15.0},
        {"klasse": "Meget højt",  "min": 15.0,  "max": float("inf")},
    ],
}

KT_ENHEDER = {
    "ppm_per_enhed": 10,
    "kg_ha_per_enhed": 25,
    "beskrivelse": "1 Kt-enhed = 10 ppm = ca. 25 kg K/ha i pløjelaget",
}

KT_FAGLIG_NOTE = (
    "Kalium udvaskes på sandjord (JB 1–2) fra efterår til forår — efterårsudtagne prøver "
    "på sandjord afspejler primært det aktuelle års gødskning. "
    "Størst bortførsel i græs, lucerne og roer (300–400 kg K/ha/år). "
    "Ca. 0,75 kg kalium pr. 100 kg halm — halmfjernelse øger K-behovet markant."
)

# ---------------------------------------------------------------------------
# MAGNESIUMTAL (Mgt)
# Enhed: mg Mg / 100g jord  (1 Mgt-enhed = 10 ppm = 25 kg Mg/ha)
# ---------------------------------------------------------------------------

MGT_KLASSER = [
    {"klasse": "Meget lavt",  "min": 0.0,   "max": 2.0},
    {"klasse": "Lavt",        "min": 2.0,   "max": 4.0},
    {"klasse": "Middel",      "min": 4.1,   "max": 8.0},
    {"klasse": "Højt",        "min": 8.1,   "max": 12.0},
    {"klasse": "Meget højt",  "min": 12.0,  "max": float("inf")},
]

MGT_ENHEDER = {
    "ppm_per_enhed": 10,
    "kg_ha_per_enhed": 25,
    "beskrivelse": "1 Mgt-enhed = 10 ppm = ca. 25 kg Mg/ha i pløjelaget",
}

MGT_FAGLIG_NOTE = (
    "Særlig opmærksomhed på sandjord ved lave Rt og ved høje kaliumtal — "
    "K hæmmer Mg-optagelsen. Typisk bortførsel 5–30 kg Mg/ha/år. "
    "Meget lave Mgt kan afhjælpes med dolomitkalk (10% Mg) eller magnesiumkalk (2,5% Mg)."
)

# ---------------------------------------------------------------------------
# KOBBERTAL (Cut)
# Enhed: mg Cu / kg jord  (1 Cut-enhed = 1 ppm = 2,5 kg Cu/ha)
# ---------------------------------------------------------------------------

CUT_KLASSER = [
    {"klasse": "Lavt",        "min": 0.0,  "max": 0.8},
    {"klasse": "Middel",      "min": 0.8,  "max": 2.0},   # "Lavt" i SEGES-tabel = her "lavt-middel"
    {"klasse": "Middel",      "min": 2.1,  "max": 5.0},
    {"klasse": "Højt",        "min": 5.1,  "max": 8.0},
    {"klasse": "Meget højt",  "min": 8.0,  "max": float("inf")},
]

# Forenklet version til opslag (to klasser kun)
CUT_KLASSER_SIMPEL = [
    {"klasse": "Meget lavt",  "min": 0.0,  "max": 0.8},
    {"klasse": "Lavt",        "min": 0.8,  "max": 2.0},
    {"klasse": "Middel",      "min": 2.1,  "max": 5.0},
    {"klasse": "Højt",        "min": 5.1,  "max": 8.0},
    {"klasse": "Meget højt",  "min": 8.0,  "max": float("inf")},
]

CUT_ENHEDER = {
    "ppm_per_enhed": 1,
    "kg_ha_per_enhed": 2.5,
    "beskrivelse": "1 Cut-enhed = 1 ppm = ca. 2,5 kg Cu/ha i pløjelaget",
}

CUT_FAGLIG_NOTE = (
    "Kobbermangel primært problem på sandjord, især med højt organisk stof. "
    "Kornafgrøder, bælgplanter, lucerne og spinat er mest følsomme. "
    "Afhjælpes ved engangstilførsel af 2,5–5 kg Cu/ha (10–20 kg blåsten). "
    "Humusrige jorde kan kræve 10–15 kg Cu/ha. Opblandes godt i jorden pga. ringe mobilitet."
)

# ---------------------------------------------------------------------------
# BORTAL (Bt)
# Enhed: mg B / 10 kg jord  (1 Bt-enhed = 0,1 ppm = 0,25 kg B/ha)
# ---------------------------------------------------------------------------

BT_KLASSER = [
    {"klasse": "Meget lavt",  "min": 0.0,  "max": 1.5},
    {"klasse": "Lavt",        "min": 1.5,  "max": 3.0},
    {"klasse": "Middel",      "min": 3.1,  "max": 5.0},
    {"klasse": "Højt",        "min": 5.1,  "max": 8.0},
    {"klasse": "Meget højt",  "min": 8.0,  "max": float("inf")},
]

BT_ENHEDER = {
    "ppm_per_enhed": 0.1,
    "kg_ha_per_enhed": 0.25,
    "beskrivelse": "1 Bt-enhed = 0,1 ppm = ca. 0,25 kg B/ha i pløjelaget",
}

BT_FAGLIG_NOTE = (
    "Bormangel primært på sandjord med højt Rt — optræder mest i tørre år. "
    "Bortallet er ikke en entydig indikation for behov. "
    "Roer og korsblomstrede afgrøder (raps) er mest følsomme — korn er ikke følsomt. "
    "Forebygges med borholdige N- eller NPK-gødninger eller solubor tidligt i sæsonen."
)

# ---------------------------------------------------------------------------
# REAKTIONSTAL (Rt = pH + 0,5)
# Opdelt efter jordtype (JB-nummer) og afgrødefølsomhed
# ---------------------------------------------------------------------------

# Afgrøder fordelt på følsomhedsgrupper
RT_AFGRØDE_GRUPPER = {
    "tolerante": ["kartofler", "rug", "havre", "græs"],
    "middel": ["vinterhvede", "vinterbyg", "majs", "rødkløver", "hvidkløver", "raps", "markært"],
    "følsomme": ["lucerne", "sukkerroer", "sneglebælg", "vårbyg"],
}

# Rt-grænseværdier: {jb_gruppe: {følsomhed: {klasse: (min, max)}}}
RT_KLASSER = {
    "jb1_4": {
        "tolerante": [
            {"klasse": "Meget lavt", "min": 0.0,  "max": 5.2},
            {"klasse": "Lavt",       "min": 5.2,  "max": 5.7},
            {"klasse": "Middel",     "min": 5.8,  "max": 6.1},
            {"klasse": "Højt",       "min": 6.2,  "max": 6.5},
            {"klasse": "Meget højt", "min": 6.5,  "max": float("inf")},
        ],
        "middel": [
            {"klasse": "Meget lavt", "min": 0.0,  "max": 5.5},
            {"klasse": "Lavt",       "min": 5.5,  "max": 5.9},
            {"klasse": "Middel",     "min": 6.0,  "max": 6.3},
            {"klasse": "Højt",       "min": 6.4,  "max": 6.7},
            {"klasse": "Meget højt", "min": 6.7,  "max": float("inf")},
        ],
        "følsomme": [
            {"klasse": "Meget lavt", "min": 0.0,  "max": 5.7},
            {"klasse": "Lavt",       "min": 5.7,  "max": 5.9},
            {"klasse": "Middel",     "min": 6.0,  "max": 6.5},
            {"klasse": "Højt",       "min": 6.6,  "max": 6.9},
            {"klasse": "Meget højt", "min": 6.9,  "max": float("inf")},
        ],
    },
    "jb5_6": {
        "tolerante": [
            {"klasse": "Meget lavt", "min": 0.0,  "max": 5.3},
            {"klasse": "Lavt",       "min": 5.3,  "max": 6.0},
            {"klasse": "Middel",     "min": 6.1,  "max": 6.5},
            {"klasse": "Højt",       "min": 6.6,  "max": 6.9},
            {"klasse": "Meget højt", "min": 6.9,  "max": float("inf")},
        ],
        "middel": [
            {"klasse": "Meget lavt", "min": 0.0,  "max": 5.5},
            {"klasse": "Lavt",       "min": 5.5,  "max": 6.2},
            {"klasse": "Middel",     "min": 6.3,  "max": 6.7},
            {"klasse": "Højt",       "min": 6.8,  "max": 7.1},
            {"klasse": "Meget højt", "min": 7.1,  "max": float("inf")},
        ],
        "følsomme": [
            {"klasse": "Meget lavt", "min": 0.0,  "max": 5.7},
            {"klasse": "Lavt",       "min": 5.7,  "max": 6.4},
            {"klasse": "Middel",     "min": 6.5,  "max": 6.9},
            {"klasse": "Højt",       "min": 7.0,  "max": 7.3},
            {"klasse": "Meget højt", "min": 7.3,  "max": float("inf")},
        ],
    },
    "jb7_9": {
        "tolerante": [
            {"klasse": "Meget lavt", "min": 0.0,  "max": 5.3},
            {"klasse": "Lavt",       "min": 5.3,  "max": 6.3},
            {"klasse": "Middel",     "min": 6.4,  "max": 6.7},
            {"klasse": "Højt",       "min": 6.8,  "max": 7.2},
            {"klasse": "Meget højt", "min": 7.2,  "max": float("inf")},
        ],
        "middel": [
            {"klasse": "Meget lavt", "min": 0.0,  "max": 5.5},
            {"klasse": "Lavt",       "min": 5.5,  "max": 6.5},
            {"klasse": "Middel",     "min": 6.6,  "max": 6.9},
            {"klasse": "Højt",       "min": 7.0,  "max": 7.4},
            {"klasse": "Meget højt", "min": 7.4,  "max": float("inf")},
        ],
        "følsomme": [
            {"klasse": "Meget lavt", "min": 0.0,  "max": 5.7},
            {"klasse": "Lavt",       "min": 5.7,  "max": 6.7},
            {"klasse": "Middel",     "min": 6.8,  "max": 7.1},
            {"klasse": "Højt",       "min": 7.2,  "max": 7.6},
            {"klasse": "Meget højt", "min": 7.6,  "max": float("inf")},
        ],
    },
    "jb11": {  # Humusjord
        "tolerante": [
            {"klasse": "Meget lavt", "min": 0.0,  "max": 4.3},
            {"klasse": "Lavt",       "min": 4.3,  "max": 4.7},
            {"klasse": "Middel",     "min": 4.8,  "max": 5.2},
            {"klasse": "Højt",       "min": 5.3,  "max": 5.7},
            {"klasse": "Meget højt", "min": 5.7,  "max": float("inf")},
        ],
        "middel": [
            {"klasse": "Meget lavt", "min": 0.0,  "max": 4.5},
            {"klasse": "Lavt",       "min": 4.5,  "max": 4.9},
            {"klasse": "Middel",     "min": 5.0,  "max": 5.4},
            {"klasse": "Højt",       "min": 5.5,  "max": 5.9},
            {"klasse": "Meget højt", "min": 5.9,  "max": float("inf")},
        ],
        "følsomme": [
            {"klasse": "Meget lavt", "min": 0.0,  "max": 4.7},
            {"klasse": "Lavt",       "min": 4.7,  "max": 5.1},
            {"klasse": "Middel",     "min": 5.2,  "max": 5.6},
            {"klasse": "Højt",       "min": 5.7,  "max": 6.1},
            {"klasse": "Meget højt", "min": 6.1,  "max": float("inf")},
        ],
    },
}

# Korrektion for organisk stof i Rt-vurdering
RT_ORGANISK_STOF_KORREKTIONER = {
    "lavt_os": {
        "betingelse": "organisk_stof_pct < 1.5",
        "korrektion": +0.2,
        "beskrivelse": "Tillæg 0,2 Rt-enheder ved organisk stof under 1,5%",
    },
    "højt_os": {
        "betingelse": "organisk_stof_pct > 3.5",
        "korrektion": -0.2,
        "beskrivelse": "Fradrag 0,2 Rt-enheder ved organisk stof over 3,5%",
    },
}

RT_FAGLIG_NOTE = (
    "Høje/meget høje Rt øger risiko for mangan- og bormangel. "
    "Meget lave Rt kan give akutte vækstproblemer. "
    "Lave Rt øger risiko for kålbrok i korsblomstrede og rodbrand i roer. "
    "Rt hæves med kalk (jordbrugskalk, magnesiumkalk, dolomitkalk, carbokalk). "
    "Normalt 2–4 ton kalk/ha hvert 3.–6. år."
)

# ---------------------------------------------------------------------------
# HUMUS OG KULSTOFINDHOLD
# ---------------------------------------------------------------------------

HUMUS_KLASSER = {
    "jb1_3": {
        "humus_lav_max": 2.1, "humus_høj_min": 4.5,
        "kulstof_lav_max": 1.2, "kulstof_høj_min": 2.6,
    },
    "jb4": {
        "humus_lav_max": 1.7, "humus_høj_min": 4.4,
        "kulstof_lav_max": 1.0, "kulstof_høj_min": 2.6,
    },
    "jb5_6": {
        "humus_lav_max": 1.8, "humus_høj_min": 3.5,
        "kulstof_lav_max": 1.0, "kulstof_høj_min": 2.0,
    },
    "jb7": {
        "humus_lav_max": 1.9, "humus_høj_min": 3.0,
        "kulstof_lav_max": 1.1, "kulstof_høj_min": 1.7,
    },
}

HUMUS_KONVERTERING = {
    "kulstof_til_humus": 1.0 / 0.58,   # humus = kulstof / 0,58
    "humus_til_kulstof": 0.58,
    "beskrivelse": "Humus = Kulstof / 0,58  |  Kulstof = Humus × 0,58",
}

# ---------------------------------------------------------------------------
# HJÆLPEFUNKTIONER
# ---------------------------------------------------------------------------

def klassificer_naering(værdi: float, klasse_liste: list) -> str:
    """
    Returnerer klasse-navn for en given måleværdi ud fra en liste af
    {klasse, min, max} dicts. Grænser er inklusive nedre, eksklusiv øvre.
    """
    for k in klasse_liste:
        if k["min"] <= værdi < k["max"]:
            return k["klasse"]
    # Fangnet: returner højeste klasse hvis over alle grænser
    return klasse_liste[-1]["klasse"]


def get_jb_gruppe(jb_nr: int) -> str:
    """Mapper JB-nummer til Rt-gruppe-nøgle."""
    if jb_nr in [1, 2, 3, 4]:
        return "jb1_4"
    elif jb_nr in [5, 6]:
        return "jb5_6"
    elif jb_nr in [7, 8, 9]:
        return "jb7_9"
    elif jb_nr == 11:
        return "jb11"
    else:
        return "jb5_6"  # fallback til middelkategori


def get_afgrøde_følsomhed(afgrøde: str) -> str:
    """Returnerer følsomhedsgruppe for en given afgrøde."""
    afgrøde_lower = afgrøde.lower()
    for gruppe, afgrøder in RT_AFGRØDE_GRUPPER.items():
        if any(a in afgrøde_lower for a in afgrøder):
            return gruppe
    return "middel"  # fallback


def klassificer_rt(rt_værdi: float, jb_nr: int, afgrøde: str,
                   organisk_stof_pct: float = None) -> dict:
    """
    Klassificerer Rt med korrektion for organisk stof.
    Returnerer dict med klasse, korrigeret Rt og JB/afgrøde-info.
    """
    # Korrektion for organisk stof
    korrigeret_rt = rt_værdi
    os_note = ""
    if organisk_stof_pct is not None:
        if organisk_stof_pct < 1.5:
            korrigeret_rt += 0.2
            os_note = "Rt korrigeret +0,2 (lavt org. stof < 1,5%)"
        elif organisk_stof_pct > 3.5:
            korrigeret_rt -= 0.2
            os_note = "Rt korrigeret -0,2 (højt org. stof > 3,5%)"

    jb_gruppe = get_jb_gruppe(jb_nr)
    følsomhed = get_afgrøde_følsomhed(afgrøde)
    klasse_liste = RT_KLASSER[jb_gruppe][følsomhed]
    klasse = klassificer_naering(korrigeret_rt, klasse_liste)

    return {
        "klasse": klasse,
        "rt_original": rt_værdi,
        "rt_korrigeret": korrigeret_rt,
        "jb_gruppe": jb_gruppe,
        "afgrøde_følsomhed": følsomhed,
        "os_note": os_note,
        "beskrivelse": KLASSE_BESKRIVELSER[klasse],
    }


def klassificer_pt(pt_værdi: float, jb_nr: int = None) -> dict:
    """Klassificerer fosfortal (Pt). Bruger jb1_3-skala for JB 1 og 3."""
    if jb_nr in [1, 3]:
        klasse_liste = PT_KLASSER["jb1_3"]
        skala = "jb1_3"
    else:
        klasse_liste = PT_KLASSER["standard"]
        skala = "standard"
    klasse = klassificer_naering(pt_værdi, klasse_liste)
    return {
        "klasse": klasse,
        "pt_værdi": pt_værdi,
        "skala": skala,
        "beskrivelse": KLASSE_BESKRIVELSER[klasse],
    }


def klassificer_kt(kt_værdi: float, jb_nr: int) -> dict:
    """Klassificerer kaliumtal (Kt) afhængig af JB-type."""
    if jb_nr < 4:
        klasse_liste = KT_KLASSER["let_jord"]
        jordtype = "let_jord (JB < 4)"
    else:
        klasse_liste = KT_KLASSER["tung_jord"]
        jordtype = "tung_jord (JB >= 4)"
    klasse = klassificer_naering(kt_værdi, klasse_liste)
    return {
        "klasse": klasse,
        "kt_værdi": kt_værdi,
        "jordtype": jordtype,
        "beskrivelse": KLASSE_BESKRIVELSER[klasse],
    }


def klassificer_mgt(mgt_værdi: float) -> dict:
    """Klassificerer magnesiumtal (Mgt)."""
    klasse = klassificer_naering(mgt_værdi, MGT_KLASSER)
    return {
        "klasse": klasse,
        "mgt_værdi": mgt_værdi,
        "beskrivelse": KLASSE_BESKRIVELSER[klasse],
    }


# ---------------------------------------------------------------------------
# QUICK-TEST
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== SEGES normer — quick test ===\n")

    # Eksempel fra projektdokumentationen: Mark 6-0
    print("Mark 6-0 (vinterhvede, JB 7, org. stof 2,13%):")
    print("  Pt =", klassificer_pt(2.6, jb_nr=7))
    print("  Kt =", klassificer_kt(12.0, jb_nr=7))
    print("  Mgt =", klassificer_mgt(5.5))
    print("  Rt =", klassificer_rt(7.8, jb_nr=7, afgrøde="vinterhvede",
                                   organisk_stof_pct=2.13))
