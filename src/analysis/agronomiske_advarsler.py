"""
warnings.py
-----------
Agronomiske advarsler baseret på kombinationer af jordparametre.

Reglerne er udledt fra SEGES-publikationen:
"Jordbundsanalyser - Hvad gemmer sig bag tallene?" (2021)

Disse advarsler er IKKE simple tærskelværdier (dem håndterer seges_normer.py),
men derimod "hvis X og Y så risiko for Z"-kombinationsregler som kræver
at flere parametre ses i sammenhæng.

Anvendes i Danish Agros AI-gødningsscreening til at berige AI-promptet
med specifikke risikoflag før Claude genererer anbefalinger.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# DATASTRUKTURER
# ---------------------------------------------------------------------------

class Alvorlighedsgrad(str, Enum):
    KRITISK = "kritisk"      # Akut problem — kræver handling nu
    ADVARSEL = "advarsel"    # Potentielt problem — overvej handling
    INFO = "info"            # Agronomisk kontekst — godt at vide


@dataclass
class Advarsel:
    kode: str                          # Maskinlæsbar kode, fx "HØJ_RT_MN_MANGEL"
    titel: str                         # Kort titel til visning
    besked: str                        # Forklaring til sælger
    alvorlighedsgrad: Alvorlighedsgrad
    parameter: str                     # Hvilken parameter der triggede
    handling: Optional[str] = None     # Konkret anbefalet handling


@dataclass
class AdvarselsResultat:
    mark_nr: str
    advarsler: list = field(default_factory=list)

    @property
    def har_kritiske(self) -> bool:
        return any(a.alvorlighedsgrad == Alvorlighedsgrad.KRITISK for a in self.advarsler)

    @property
    def antal(self) -> int:
        return len(self.advarsler)

    def til_prompt_tekst(self) -> str:
        """Formaterer advarsler til indsættelse i AI system prompt."""
        if not self.advarsler:
            return f"Mark {self.mark_nr}: Ingen særlige advarsler."

        linjer = [f"ADVARSLER FOR MARK {self.mark_nr}:"]
        for a in self.advarsler:
            linjer.append(
                f"  [{a.alvorlighedsgrad.value.upper()}] {a.titel}: {a.besked}"
                + (f" → {a.handling}" if a.handling else "")
            )
        return "\n".join(linjer)


# ---------------------------------------------------------------------------
# ADVARSELSFUNKTIONER
# Hver funktion checker én kombinations-regel og returnerer Advarsel eller None
# ---------------------------------------------------------------------------

def check_høj_rt_mikronæringsstoffer(rt: float, jb_nr: int = None) -> Optional[Advarsel]:
    """
    Høj/meget høj Rt øger risiko for mangan- og bormangel.
    Særligt relevant på sandjord (JB 1-4) med høj pH.
    Kilde: SEGES 2021, s. 4
    """
    if rt >= 7.5:
        sandjord_note = " Risikoen er særlig høj på sandjord." if jb_nr and jb_nr <= 4 else ""
        return Advarsel(
            kode="HØJ_RT_MN_B_MANGEL",
            titel="Risiko for mangan- og bormangel",
            besked=(
                f"Rt på {rt} er meget højt, hvilket kan reducere tilgængeligheden "
                f"af mangan og bor for afgrøden.{sandjord_note}"
            ),
            alvorlighedsgrad=Alvorlighedsgrad.ADVARSEL,
            parameter="Rt",
            handling=(
                "Overvej bladsprøjtning med mangan tidligt i sæsonen. "
                "Tjek bortallet hvis raps eller roer er i sædskiftet."
            ),
        )
    elif rt >= 7.0:
        return Advarsel(
            kode="FORHØJET_RT_MIKRO_RISIKO",
            titel="Forhøjet Rt — let risiko for mikronæringsstofmangel",
            besked=f"Rt på {rt} er i den høje ende. Monitorer afgrøden for mangansymptomer.",
            alvorlighedsgrad=Alvorlighedsgrad.INFO,
            parameter="Rt",
            handling="Vær opmærksom på gulstribning i korn — tegn på manganmangel.",
        )
    return None


def check_lav_rt_sygdomsrisiko(rt: float, afgrøde: str = None) -> Optional[Advarsel]:
    """
    Lav Rt øger risiko for kålbrok i korsblomstrede og rodbrand i roer.
    Kilde: SEGES 2021, s. 4
    """
    korsblomstrede = ["raps", "sennep", "kål", "korsblomst"]
    roer = ["sukkerroe", "foderroe", "roe"]

    afgrøde_lower = (afgrøde or "").lower()
    er_korsblomstret = any(k in afgrøde_lower for k in korsblomstrede)
    er_roe = any(r in afgrøde_lower for r in roer)

    if rt < 5.5:
        if er_korsblomstret:
            return Advarsel(
                kode="LAV_RT_KÅLBROK",
                titel="Høj risiko for kålbrok",
                besked=(
                    f"Rt på {rt} er lavt — kombineret med {afgrøde} er der "
                    f"betydelig risiko for kålbrok."
                ),
                alvorlighedsgrad=Alvorlighedsgrad.KRITISK,
                parameter="Rt",
                handling="Kalk marken inden såning. Overvej resistente sorter.",
            )
        elif er_roe:
            return Advarsel(
                kode="LAV_RT_RODBRAND",
                titel="Risiko for rodbrand",
                besked=f"Rt på {rt} er lavt — øget risiko for rodbrand i roer.",
                alvorlighedsgrad=Alvorlighedsgrad.ADVARSEL,
                parameter="Rt",
                handling="Kalk marken. Mål Rt igen efter kalkning.",
            )
        else:
            return Advarsel(
                kode="LAV_RT_GENEREL",
                titel="Lavt reaktionstal",
                besked=f"Rt på {rt} kan give dårlig vækst og næringsstofoptagelse.",
                alvorlighedsgrad=Alvorlighedsgrad.ADVARSEL,
                parameter="Rt",
                handling="Planlæg kalkning. Kontakt planteavlskonsulent for kalkningsstrategi.",
            )
    return None


def check_høj_k_hæmmer_mg(kt: float, mgt: float) -> Optional[Advarsel]:
    """
    Højt kaliumindhold hæmmer magnesiumoptagelsen (ionkonkurrence).
    Særlig relevant når Mgt allerede er lavt.
    Kilde: SEGES 2021, s. 6
    """
    if kt >= 8.0 and mgt <= 4.0:
        alvor = Alvorlighedsgrad.KRITISK if mgt < 2.0 else Alvorlighedsgrad.ADVARSEL
        return Advarsel(
            kode="HØJ_K_LAV_MG_ANTAGONISME",
            titel="K/Mg-antagonisme — risiko for Mg-mangel",
            besked=(
                f"Højt kaliumtal (Kt {kt}) kombineret med lavt magnesiumtal (Mgt {mgt}) "
                f"kan hæmme afgrødens optagelse af magnesium."
            ),
            alvorlighedsgrad=alvor,
            parameter="Kt/Mgt",
            handling=(
                "Tilsæt magnesium via magnesiumkalk eller MgSO4-gødning. "
                "Undgå at øge K-tilførslen yderligere."
            ),
        )
    elif kt >= 10.0 and mgt <= 6.0:
        return Advarsel(
            kode="MEGET_HØJ_K_MG_RISIKO",
            titel="Meget højt K — Mg-optagelse kan påvirkes",
            besked=(
                f"Kt på {kt} er meget højt. Selv ved middel Mgt ({mgt}) "
                f"kan K-overskud reducere Mg-optagelsen."
            ),
            alvorlighedsgrad=Alvorlighedsgrad.INFO,
            parameter="Kt",
            handling="Monitorer afgrøden for magnesiummangel (intervenal gulning).",
        )
    return None


def check_kobber_sandjord(cut: float, jb_nr: int, organisk_stof_pct: float = None) -> Optional[Advarsel]:
    """
    Kobbermangel er primært et problem på sandjord — særlig med højt org. stof.
    Kilde: SEGES 2021, s. 6
    """
    er_sandjord = jb_nr in [1, 2, 3, 4]
    højt_os = organisk_stof_pct is not None and organisk_stof_pct > 3.5

    if cut < 0.8 and er_sandjord:
        if højt_os:
            return Advarsel(
                kode="LAV_CU_SANDJORD_HØJ_OS",
                titel="Kritisk kobberrisiko — sandjord med højt organisk stof",
                besked=(
                    f"Lavt kobbertal (Cut {cut}) på sandjord (JB {jb_nr}) med højt "
                    f"organisk stof ({organisk_stof_pct}%) giver høj risiko for kobbermangel."
                ),
                alvorlighedsgrad=Alvorlighedsgrad.KRITISK,
                parameter="Cut",
                handling=(
                    "Engangstilførsel af 10–15 kg kobber/ha (40–60 kg blåsten). "
                    "Opblandes godt i jorden — kobber har ringe mobilitet."
                ),
            )
        else:
            return Advarsel(
                kode="LAV_CU_SANDJORD",
                titel="Lavt kobbertal på sandjord",
                besked=f"Cut på {cut} er lavt. Kobbermangel er primært et problem på sandjord (JB {jb_nr}).",
                alvorlighedsgrad=Alvorlighedsgrad.ADVARSEL,
                parameter="Cut",
                handling=(
                    "Engangstilførsel af 2,5–5 kg kobber/ha (10–20 kg blåsten). "
                    "Kornafgrøder, bælgplanter og lucerne er mest følsomme."
                ),
            )
    return None


def check_bor_raps_roer(bt: float, rt: float, afgrøde: str = None) -> Optional[Advarsel]:
    """
    Bormangel primært på sandjord med højt Rt. Raps og roer er følsomme.
    Kilde: SEGES 2021, s. 6
    """
    følsomme_afgrøder = ["raps", "sukkerroe", "foderroe", "roe", "kål"]
    afgrøde_lower = (afgrøde or "").lower()
    er_følsom = any(f in afgrøde_lower for f in følsomme_afgrøder)

    if bt < 1.5 and rt > 6.5 and er_følsom:
        return Advarsel(
            kode="LAV_BT_HØJ_RT_FØLSOM_AFGRØDE",
            titel="Bormangel-risiko i følsom afgrøde",
            besked=(
                f"Lavt bortal (Bt {bt}) kombineret med højt Rt ({rt}) og {afgrøde} "
                f"giver høj risiko for bormangel."
            ),
            alvorlighedsgrad=Alvorlighedsgrad.ADVARSEL,
            parameter="Bt",
            handling=(
                "Anvend borholdige N- eller NPK-gødninger, eller udsprøjt "
                "Solubor tidligt i sæsonen."
            ),
        )
    elif bt < 1.5 and rt > 6.5:
        return Advarsel(
            kode="LAV_BT_HØJ_RT",
            titel="Let bormangel-risiko ved højt Rt",
            besked=f"Lavt bortal (Bt {bt}) og højt Rt ({rt}). Bormangel optræder mest i tørre år.",
            alvorlighedsgrad=Alvorlighedsgrad.INFO,
            parameter="Bt",
            handling="Særlig opmærksomhed ved tørt vejr — overvej borholdig gødning til raps/roer.",
        )
    return None


def check_humus_lerforhold(ler_pct: float, kulstof_pct: float) -> Optional[Advarsel]:
    """
    På lerjord: ler/kulstof-forholdet over 10 giver dårlig jordstruktur.
    Dvs. 15% ler kræver minimum 1,5% kulstof.
    Kilde: SEGES 2021, s. 7
    """
    if ler_pct >= 15.0 and kulstof_pct > 0:
        forhold = ler_pct / kulstof_pct
        if forhold > 10:
            min_kulstof = ler_pct / 10
            return Advarsel(
                kode="DÅRLIG_JORDSTRUKTUR_LER_KULSTOF",
                titel="Risiko for dårlig jordstruktur",
                besked=(
                    f"Ler/kulstof-forholdet er {forhold:.1f} (ler: {ler_pct}%, "
                    f"kulstof: {kulstof_pct}%). Over 10 giver typisk dårlig jordstruktur."
                ),
                alvorlighedsgrad=Alvorlighedsgrad.INFO,
                parameter="Ler/Kulstof",
                handling=(
                    f"Kulstofindholdet bør være mindst {min_kulstof:.1f}% ved {ler_pct}% ler. "
                    f"Overvej tiltag til at øge organisk stof (nedmuldning af halm, grøngødning)."
                ),
            )
    return None


def check_molybdæn_rt(mot: float, rt: float) -> Optional[Advarsel]:
    """
    Molybdæntolkning afhænger af Rt — lavt Rt kræver højere Mot.
    Kilde: SEGES 2021, s. 7
    """
    if rt > 6.0 and mot < 2.0:
        return Advarsel(
            kode="LAV_MOT",
            titel="Lavt molybdæntal",
            besked=f"Molybdæntal ({mot}) under 2,0 ved Rt over 6 indikerer mulig mangel.",
            alvorlighedsgrad=Alvorlighedsgrad.INFO,
            parameter="Mot",
            handling="Relevant ved bælgsæd, lucerne og kløver — disse er mest følsomme.",
        )
    elif rt < 5.0 and mot < 3.0:
        return Advarsel(
            kode="LAV_MOT_LAV_RT",
            titel="Lavt molybdæntal ved surt jordfald",
            besked=(
                f"Ved lavt Rt ({rt}) bør molybdæntallet være minimum 3,0 — "
                f"aktuelt er det {mot}."
            ),
            alvorlighedsgrad=Alvorlighedsgrad.ADVARSEL,
            parameter="Mot/Rt",
            handling="Kalk marken — kalkning øger molybdæntilgængeligheden markant.",
        )
    return None


def check_fosfor_loft(pt_anbefalet_kg_ha: float) -> Optional[Advarsel]:
    """
    Lovgivningsmæssigt P-loft på maks. 29-30 kg P/ha.
    Kilde: Projektdokumentation + gødningslovgivning
    """
    if pt_anbefalet_kg_ha > 30:
        return Advarsel(
            kode="P_LOFT_OVERSKREDET",
            titel="⚠️ P-loft overskredet",
            besked=(
                f"Beregnet P-behov ({pt_anbefalet_kg_ha:.1f} kg P/ha) overskrider "
                f"det lovgivningsmæssige P-loft på maks. 29–30 kg P/ha."
            ),
            alvorlighedsgrad=Alvorlighedsgrad.KRITISK,
            parameter="P-loft",
            handling=(
                "Reducer P-anbefalingen til maks. 29 kg P/ha. "
                "Kontakt planteavlskonsulent for at justere gødningsplanen."
            ),
        )
    elif pt_anbefalet_kg_ha > 25:
        return Advarsel(
            kode="P_LOFT_NÆR_GRÆNSE",
            titel="P-anbefaling tæt på lovgivningsmæssigt loft",
            besked=(
                f"Beregnet P-behov ({pt_anbefalet_kg_ha:.1f} kg P/ha) nærmer sig "
                f"P-loftet på 29–30 kg P/ha."
            ),
            alvorlighedsgrad=Alvorlighedsgrad.ADVARSEL,
            parameter="P-loft",
            handling="Vær opmærksom ved endelig gødningsplan — P-loftet må ikke overskrides.",
        )
    return None


# ---------------------------------------------------------------------------
# HOVEDFUNKTION — kør alle checks for én mark
# ---------------------------------------------------------------------------

def generer_advarsler(
    mark_nr: str,
    rt: float = None,
    pt: float = None,
    kt: float = None,
    mgt: float = None,
    cut: float = None,
    bt: float = None,
    mot: float = None,
    jb_nr: int = None,
    organisk_stof_pct: float = None,
    kulstof_pct: float = None,
    ler_pct: float = None,
    afgrøde: str = None,
    pt_anbefalet_kg_ha: float = None,
) -> AdvarselsResultat:
    """
    Kører alle advarselschecks for én mark og returnerer et AdvarselsResultat.

    Parametre der ikke er tilgængelige sendes som None — de relevante
    checks springes automatisk over.
    """
    resultat = AdvarselsResultat(mark_nr=mark_nr)
    checks = []

    # Rt-baserede checks
    if rt is not None:
        checks.append(check_høj_rt_mikronæringsstoffer(rt, jb_nr))
        checks.append(check_lav_rt_sygdomsrisiko(rt, afgrøde))

    # Kombinationschecks
    if kt is not None and mgt is not None:
        checks.append(check_høj_k_hæmmer_mg(kt, mgt))

    if cut is not None and jb_nr is not None:
        checks.append(check_kobber_sandjord(cut, jb_nr, organisk_stof_pct))

    if bt is not None and rt is not None:
        checks.append(check_bor_raps_roer(bt, rt, afgrøde))

    if ler_pct is not None and kulstof_pct is not None:
        checks.append(check_humus_lerforhold(ler_pct, kulstof_pct))

    if mot is not None and rt is not None:
        checks.append(check_molybdæn_rt(mot, rt))

    # Lovgivning
    if pt_anbefalet_kg_ha is not None:
        checks.append(check_fosfor_loft(pt_anbefalet_kg_ha))

    # Tilføj kun ikke-None resultater
    resultat.advarsler = [a for a in checks if a is not None]

    # Sorter: kritiske først, derefter advarsler, så info
    rækkefølge = {
        Alvorlighedsgrad.KRITISK: 0,
        Alvorlighedsgrad.ADVARSEL: 1,
        Alvorlighedsgrad.INFO: 2,
    }
    resultat.advarsler.sort(key=lambda a: rækkefølge[a.alvorlighedsgrad])

    return resultat


# ---------------------------------------------------------------------------
# QUICK-TEST
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== Advarselstest — Mark 6-0 fra projekteksempel ===\n")

    resultat = generer_advarsler(
        mark_nr="6-0",
        rt=7.8,
        pt=2.6,
        kt=12.0,
        mgt=5.5,
        jb_nr=7,
        organisk_stof_pct=2.13,
        kulstof_pct=2.13 * 0.58,
        ler_pct=15.9,
        afgrøde="vinterhvede",
    )

    print(f"Antal advarsler: {resultat.antal}")
    print(f"Har kritiske: {resultat.har_kritiske}\n")
    for a in resultat.advarsler:
        print(f"[{a.alvorlighedsgrad.value.upper()}] {a.kode}")
        print(f"  {a.titel}")
        print(f"  {a.besked}")
        if a.handling:
            print(f"  → {a.handling}")
        print()

    print("\n--- Prompt-tekst til Claude ---")
    print(resultat.til_prompt_tekst())

    print("\n\n=== Test med raps på sur sandjord ===\n")
    resultat2 = generer_advarsler(
        mark_nr="TEST-2",
        rt=5.2,
        bt=1.2,
        kt=9.0,
        mgt=2.5,
        cut=0.6,
        jb_nr=2,
        organisk_stof_pct=4.1,
        afgrøde="vinterraps",
        pt_anbefalet_kg_ha=31.5,
    )
    print(resultat2.til_prompt_tekst())
