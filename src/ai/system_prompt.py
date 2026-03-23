"""
system_prompt.py
----------------
Bygger den agronomiske system-prompt til AI-kaldet.
Al faglig kontekst hentes fra seges_normer.py — ingen hardkodede tekster her.
"""

from analysis.seges_normer import (
    KLASSE_BESKRIVELSER,
    PT_FAGLIG_NOTE,
    KT_FAGLIG_NOTE,
    MGT_FAGLIG_NOTE,
    BT_FAGLIG_NOTE,
    CUT_FAGLIG_NOTE,
    RT_FAGLIG_NOTE,
)

_KLASSIFIKATION_SEKTION = """\
## Klassifikationssystem (SEGES 2021)
Jordbundsanalyser vurderes på en skala med fem klasser:

{klasser}
Kilde: "Jordbundsanalyser — Hvad gemmer sig bag tallene?" (SEGES, Landbrug & Fødevarer, 2021).\
"""

_NAERING_SEKTION = """\
## Agronomisk baggrundsviden per næringsstof

**Reaktionstal (Rt)**
{rt}

**Fosfortal (Pt)**
{pt}

**Kaliumtal (Kt)**
{kt}

**Magnesiumtal (Mgt)**
{mgt}

**Kobbertal (Cut)**
{cut}

**Bortal (Bt)**
{bt}\
"""

_ROLLE_SEKTION = """\
Du er faglig jordrådgiver hos Danish Agro.
Du arbejder med jordprøvedata fra landbrugsbedrifter og hjælper med \
screeningsanbefalinger baseret på SEGES-normer.\
"""

_BEGRÆNSNINGER_SEKTION = """\
## Begrænsninger (fase 1 — screening)
- Skriv KUN screeningsanbefalinger — ikke endelige gødningsplaner.
- Nævn IKKE konkrete gødningsdoser, kg/ha, produktnavne, lovgivning eller compliance.
- Alle værdier er jordprøvegennemsnit og kræver faglig validering.
- Hvis antal_proever > 1, kan der være variation inden for marken.\
"""


def build_system_prompt() -> str:
    """
    Returnerer en samlet system-prompt-streng med al agronomisk kontekst
    klar til brug i et API-kald.
    """
    # Formatér klassifikationsklasserne
    klasse_linjer = "\n".join(
        f"- **{klasse}**: {beskrivelse}"
        for klasse, beskrivelse in KLASSE_BESKRIVELSER.items()
    )
    klassifikation = _KLASSIFIKATION_SEKTION.format(klasser=klasse_linjer + "\n")

    naering = _NAERING_SEKTION.format(
        rt=RT_FAGLIG_NOTE,
        pt=PT_FAGLIG_NOTE,
        kt=KT_FAGLIG_NOTE,
        mgt=MGT_FAGLIG_NOTE,
        cut=CUT_FAGLIG_NOTE,
        bt=BT_FAGLIG_NOTE,
    )

    return "\n\n".join([
        _ROLLE_SEKTION,
        klassifikation,
        naering,
        _BEGRÆNSNINGER_SEKTION,
    ])
