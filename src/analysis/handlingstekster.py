"""
handlingstekster.py
-------------------
"Hvad skal jeg gøre hvis..."-tekster per parameter og klasse.

Kilde: Agillix/SEGES Innovation analyserapport (januar 2026)
Samme faglige indhold som SEGES-publikationen "Jordbundsanalyser -
Hvad gemmer sig bag tallene?" (2021), men formuleret direkte til landmanden.

Anvendes i Danish Agros AI-gødningsscreening til at give Claude
det professionelle SEGES-sprog frem for at AI'en opfinder sit eget.

Struktur:
    HANDLINGSTEKSTER[parameter][klasse] = {
        "kort":   Kort sætning til tabel/oversigt
        "fuld":   Fuld handlingstekst til rapport og AI-prompt
        "symbol": Visuelt symbol (▼ ● ● ● ▲)
        "farve":  Farvekode til frontend (rød/orange/grøn/blå/mørkeblå)
    }
"""

# ---------------------------------------------------------------------------
# SYMBOLTABEL (fra Agillix-rapport)
# ---------------------------------------------------------------------------

SYMBOLER = {
    "Meget lav":  {"symbol": "▼", "farve": "#D32F2F"},   # rød
    "Lav":        {"symbol": "●", "farve": "#F57C00"},   # orange
    "Middel":     {"symbol": "●", "farve": "#388E3C"},   # grøn
    "Høj":        {"symbol": "●", "farve": "#1565C0"},   # blå
    "Meget høj":  {"symbol": "▲", "farve": "#1A237E"},   # mørkeblå
}

# Alias så begge stavemåder virker
KLASSE_ALIAS = {
    "Meget lavt":  "Meget lav",
    "Lavt":        "Lav",
    "Middel":      "Middel",
    "Højt":        "Høj",
    "Meget højt":  "Meget høj",
}

# ---------------------------------------------------------------------------
# REAKTIONSTAL (Rt)
# ---------------------------------------------------------------------------

RT_HANDLINGER = {
    "Meget lav": {
        "kort": "Reaktionstallene er meget lave og direkte begrænsende for udbyttet.",
        "fuld": (
            "Reaktionstallene er meget lave og er direkte begrænsende for udbyttet. "
            "Der skal derfor tilføres kalk inden næste vækstsæson. "
            "Vælg afgrøder som havre, vinterrug eller kartofler, der er tolerante over for lavt Rt. "
            "Undgå f.eks. vårbyg, roer eller lucerne, der er følsomme over for lavt Rt."
        ),
        "handling": "Kalk inden næste vækstsæson. Vælg tolerante afgrøder.",
    },
    "Lav": {
        "kort": "Reaktionstallene er lave. Kalk inden næste vækstsæson for at undgå udbyttetab.",
        "fuld": (
            "Reaktionstallene er lave. "
            "For ikke at risikere udbyttetab bør der kalkes inden næste vækstsæson."
        ),
        "handling": "Planlæg kalkning inden næste vækstsæson.",
    },
    "Middel": {
        "kort": "Reaktionstallene er middelhøje.",
        "fuld": "Reaktionstallene er middelhøje. Ingen akut handling nødvendig.",
        "handling": None,
    },
    "Høj": {
        "kort": "Reaktionstallene er høje. Kalk ikke før tidligst efter næste jordprøveudtagning.",
        "fuld": (
            "Reaktionstallene er høje. "
            "Hvis det er generelt for marken, skal der ikke kalkes før tidligst efter næste jordprøveudtagning."
        ),
        "handling": "Ingen kalkning — afvent næste jordprøveudtagning.",
    },
    "Meget høj": {
        "kort": "Reaktionstallene er meget høje. Pas på manganmangel og bormangel i raps og roer.",
        "fuld": (
            "Reaktionstallene er meget høje. "
            "Pas på manganmangel generelt og bormangel i raps og roer. "
            "Hvis der ikke forekommer lave reaktionstal i marken, "
            "skal der ikke kalkes før tidligst efter næste jordprøveudtagning."
        ),
        "handling": "Monitorer for manganmangel. Ingen kalkning.",
    },
}

# ---------------------------------------------------------------------------
# FOSFORTAL (Pt)
# ---------------------------------------------------------------------------

PT_HANDLINGER = {
    "Meget lav": {
        "kort": "Fosfortallene er meget lave og fosformangel begrænser udbyttet.",
        "fuld": (
            "Fosfortallene er meget lave og fosformangel begrænser udbyttet. "
            "Der bør derfor tilføres en 50 til 100 kg fosfor som engangsgødskning. "
            "Derudover skal der årligt suppleres med fosforgødning."
        ),
        "handling": "Engangstilførsel 50–100 kg P/ha + årlig supplement.",
    },
    "Lav": {
        "kort": "Fosfortallene er lave. Tilføres mere fosfor end afgrøden fjerner.",
        "fuld": (
            "Fosfortallene er lave. "
            "Hvert år skal der tilføres mere fosfor, end afgrøden fjerner. "
            "Diskuter dette med planteavlskonsulenten ved gødningsplanlægningen."
        ),
        "handling": "Tilføres mere P end bortførslen. Drøft med konsulent.",
    },
    "Middel": {
        "kort": "Fosfortallene er middelhøje. Ingen speciel hensyn til fosfor.",
        "fuld": (
            "Fosfortallene er middelhøje. "
            "Der skal derfor ikke tages specielt hensyn til fosfor ved gødningsplanlægningen."
        ),
        "handling": None,
    },
    "Høj": {
        "kort": "Fosfortallene er høje. Fosfortildelingen bør ikke overskride afgrødernes bortførsel.",
        "fuld": (
            "Fosfortallene er høje. "
            "Derfor bør fosfortildelingen i gennemsnit over årene ikke overskride afgrødernes bortførsel."
        ),
        "handling": "Reducer P-tilførsel til bortførselsniveau.",
    },
    "Meget høj": {
        "kort": "Fosfortallene er meget høje. Fosfortildelingen skal minimeres af hensyn til miljøet.",
        "fuld": (
            "Fosfortallene er meget høje. "
            "Her skal fosfortildelingen minimeres af hensyn til miljøet."
        ),
        "handling": "Minimer P-tilførsel. Hensyn til vandmiljøet.",
    },
}

# ---------------------------------------------------------------------------
# KALIUMTAL (Kt)
# ---------------------------------------------------------------------------

KT_HANDLINGER = {
    "Meget lav": {
        "kort": "Kaliumtallene er meget lave og kaliummangel begrænser udbyttet.",
        "fuld": (
            "Kaliumtallene er meget lave og kaliummangel begrænser udbyttet. "
            "Der skal derfor årligt tilføres ca. 30% mere kalium, end afgrøderne bortfører. "
            "Tal med planteavlskonsulenten om det ved gødningsplanlægningen."
        ),
        "handling": "Tilføres ca. 30% mere K end bortførslen. Drøft med konsulent.",
    },
    "Lav": {
        "kort": "Kaliumtallene er lave. Tilføres minimum den mængde kalium afgrøden fjerner.",
        "fuld": (
            "Kaliumtallene er lave. "
            "Der skal årligt tilføres minimum den mængde kalium, som afgrøden fjerner. "
            "Diskuter dette med planteavlskonsulenten ved gødningsplanlægningen."
        ),
        "handling": "Tilføres minimum bortførselsmængden. Drøft med konsulent.",
    },
    "Middel": {
        "kort": "Kaliumtallene er middelhøje. Ingen speciel hensyn til kalium.",
        "fuld": (
            "Kaliumtallene er middelhøje. "
            "Der skal derfor ikke tages specielt hensyn til kalium ved gødningsplanlægningen."
        ),
        "handling": None,
    },
    "Høj": {
        "kort": "Kaliumtallene er høje. Der kan spares på kaliumgødningen.",
        "fuld": (
            "Kaliumtallene er høje. "
            "Her kan der spares på kaliumgødningen."
        ),
        "handling": "Reducer K-tilførsel.",
    },
    "Meget høj": {
        "kort": "Kaliumtallene er meget høje. Kaliumgødskning kan undlades de nærmeste år.",
        "fuld": (
            "Kaliumtallene er meget høje. "
            "Her kan kaliumgødskning undlades i de nærmeste år, "
            "med mindre der dyrkes slætgræs eller lucerne i flere år. "
            "Pas på afgrødens magnesiumforsyning."
        ),
        "handling": "Undlad K-gødskning. Obs: magnesiumforsyning ved meget høje K-tal.",
    },
}

# ---------------------------------------------------------------------------
# MAGNESIUMTAL (Mgt)
# ---------------------------------------------------------------------------

MGT_HANDLINGER = {
    "Meget lav": {
        "kort": "Magnesiumtallene er meget lave og begrænser udbyttet.",
        "fuld": (
            "Magnesiumtallene er meget lave og begrænser udbyttet. "
            "Det er mest kritisk i rodfrugter og raps. "
            "Magnesiumtallene skal hæves f.eks. ved brug af dolomit- eller magnesiumkalk. "
            "Tal med planteavlskonsulenten om det."
        ),
        "handling": "Hæv Mgt med dolomitkalk eller magnesiumkalk. Særlig kritisk i raps og rodfrugter.",
    },
    "Lav": {
        "kort": "Magnesiumtallene er lave. Tilføres mere magnesium end afgrøden fjerner.",
        "fuld": (
            "Magnesiumtallene er lave. "
            "Der skal derfor hvert år tilføres mere magnesium, end afgrøden fjerner. "
            "Anvend magnesiumkalk ved næste kalkning. "
            "Diskuter dette med planteavlskonsulenten ved gødningsplanlægningen."
        ),
        "handling": "Tilføres mere Mg end bortførslen. Brug magnesiumkalk ved næste kalkning.",
    },
    "Middel": {
        "kort": "Magnesiumtallene er middelhøje. Ingen speciel hensyn til magnesium.",
        "fuld": (
            "Magnesiumtallene er middelhøje. "
            "Der skal derfor ikke tages specielt hensyn til magnesium ved gødningsplanlægningen."
        ),
        "handling": None,
    },
    "Høj": {
        "kort": "Magnesiumtallene er høje. Gødninger uden magnesium kan vælges.",
        "fuld": (
            "Magnesiumtalene er høje. "
            "Der kan vælges gødninger uden indhold af magnesium i de nærmeste år."
        ),
        "handling": "Vælg gødninger uden Mg.",
    },
    "Meget høj": {
        "kort": "Magnesiumtallene er meget høje. Gødninger uden magnesium kan vælges.",
        "fuld": (
            "Magnesiumtallene er meget høje. "
            "Der kan vælges gødninger uden indhold af magnesium i de nærmeste år."
        ),
        "handling": "Vælg gødninger uden Mg.",
    },
}

# ---------------------------------------------------------------------------
# KOBBERTAL (Cut)
# ---------------------------------------------------------------------------

CUT_HANDLINGER = {
    "Meget lav": {
        "kort": "Kobbertallene er meget lave og kobbermangel kan reducere kornudbyttet.",
        "fuld": (
            "Kobbertallene er meget lave og kobbermangel kan reducere kornudbyttet. "
            "Hvor der er målt meget lave kobbertal, kan mangel i de følgende år forebygges "
            "ved en engangstilførsel af minimum 2,5–5 kg kobber pr. ha (10–20 kg blåsten pr. ha). "
            "Blåsten kan udspredes med gødningsspreder med mikrogranulatudstyr eller marksprøjten. "
            "På humusrige jorde kan 10–15 kg kobber pr. ha (40–60 kg blåsten) være nødvendigt. "
            "På grund af kobbers ringe mobilitet i jorden bør det opblandes godt i jorden."
        ),
        "handling": "Engangstilførsel 2,5–5 kg Cu/ha (10–20 kg blåsten). Opbland godt i jorden.",
    },
    "Lav": {
        "kort": "Kobbertallene er lave. Korn er mest følsom over for kobbermangel.",
        "fuld": (
            "Kobbertallene er lave. "
            "Korn er mest følsom over for kobbermangel. "
            "Kobbertallet kan hæves ved brug af blåsten — "
            "eller der kan årligt udsprøjtes kobberoxychlorid eller lignende. "
            "Diskuter dette med planteavlskonsulenten ved gødningsplanlægningen."
        ),
        "handling": "Tilføres Cu via blåsten eller kobberoxychlorid. Drøft med konsulent.",
    },
    "Middel": {
        "kort": "Kobbertallene er middelhøje. Ingen speciel hensyn til kobber.",
        "fuld": (
            "Kobbertallene er middelhøje. "
            "Der skal derfor ikke tages specielt hensyn til kobber ved gødningsplanlægningen."
        ),
        "handling": None,
    },
    "Høj": {
        "kort": "Kobbertallene er høje. Årsagen bør identificeres.",
        "fuld": (
            "Kobbertallene er høje. "
            "Årsagen bør identificeres. "
            "Diskuter det med planteavlskonsulenten."
        ),
        "handling": "Identificer årsag til højt kobbertal. Drøft med konsulent.",
    },
    "Meget høj": {
        "kort": "Kobbertallene er meget høje. Højt kobbertal kan være giftigt for planter.",
        "fuld": (
            "Kobbertallene er meget høje. "
            "Årsagen bør identificeres med henblik på at undgå yderligere stigning. "
            "For høje kobbertal kan være giftige for planter, herunder specielt bælgplanter."
        ),
        "handling": "Undersøg årsag — meget højt Cu kan være giftigt for bælgplanter.",
    },
}

# ---------------------------------------------------------------------------
# BORTAL (Bt)
# ---------------------------------------------------------------------------

BT_HANDLINGER = {
    "Meget lav": {
        "kort": "Bortallene er meget lave og kan begrænse udbyttet i raps og roer.",
        "fuld": (
            "Bortallene er meget lave og kan begrænse udbyttet i navnlig bredbladede afgrøder "
            "som raps og roer. "
            "Til disse afgrøder skal tilføres bor sammen med andre gødninger eller ved udsprøjtning. "
            "Vær meget opmærksom på bormangel i vækstsæsonen."
        ),
        "handling": "Tilføres bor i raps og roer — via gødning eller udsprøjtning.",
    },
    "Lav": {
        "kort": "Bortallene er lave og kan begrænse udbyttet i raps og roer.",
        "fuld": (
            "Bortallene er lave og kan begrænse udbyttet i navnlig bredbladede afgrøder "
            "som raps og roer. "
            "Til disse afgrøder skal tilføres bor sammen med andre gødninger eller ved udsprøjtning."
        ),
        "handling": "Tilføres bor i raps og roer.",
    },
    "Middel": {
        "kort": "Bortallene er middel. Overvej bortilførsel til raps og roer ved højt Rt.",
        "fuld": (
            "Bortallene er middel. "
            "Der kan godt være behov for at tilføre bor til bredbladede afgrøder som raps og roer, "
            "hvis reaktionstal er høje i forhold til jordtypen, "
            "eller hvis der tidligere har været bormangel."
        ),
        "handling": "Overvej bor til raps/roer ved højt Rt eller tidligere bormangel.",
    },
    "Høj": {
        "kort": "Bortallene er høje. Behovet for bortilførsel er begrænset.",
        "fuld": (
            "Bortallene er høje og behovet for tilførsel af bor er derfor begrænset. "
            "Bortallet kan dog ændre sig relativt hurtigt, og der kan godt være behov "
            "for at tilføre bor til bredbladede afgrøder som raps og roer, "
            "hvis reaktionstal er høje i forhold til jordtypen, "
            "eller hvis der tidligere har været bormangel."
        ),
        "handling": "Begrænset behov — men monitor raps/roer ved højt Rt.",
    },
    "Meget høj": {
        "kort": "Bortallene er meget høje. Behovet for bortilførsel er begrænset.",
        "fuld": (
            "Bortallene er meget høje og behovet for tilførsel af bor er derfor begrænset. "
            "Bortallet kan dog ændre sig relativt hurtigt, og der kan godt være behov "
            "for at tilføre bor til bredbladede afgrøder som raps og roer, "
            "hvis reaktionstal er høje i forhold til jordtypen, "
            "eller hvis der tidligere har været bormangel."
        ),
        "handling": "Ingen aktuel handling — men bortallet kan ændre sig hurtigt.",
    },
}

# ---------------------------------------------------------------------------
# SAMLET DICTIONARY
# ---------------------------------------------------------------------------

HANDLINGSTEKSTER = {
    "Rt":  RT_HANDLINGER,
    "Pt":  PT_HANDLINGER,
    "Kt":  KT_HANDLINGER,
    "Mgt": MGT_HANDLINGER,
    "Cut": CUT_HANDLINGER,
    "Bt":  BT_HANDLINGER,
}

# ---------------------------------------------------------------------------
# HJÆLPEFUNKTIONER
# ---------------------------------------------------------------------------

def get_handlingstekst(parameter: str, klasse: str) -> dict:
    """
    Returnerer handlingstekst-dict for en given parameter og klasse.

    Håndterer begge stavemåder:
      "Meget lavt" / "Meget lav", "Lavt" / "Lav" osv.

    Returnerer tom dict hvis parameter eller klasse ikke findes.
    """
    # Normaliser klasse-navn
    klasse_norm = KLASSE_ALIAS.get(klasse, klasse)

    param_data = HANDLINGSTEKSTER.get(parameter, {})
    return param_data.get(klasse_norm, {})


def get_symbol(klasse: str) -> dict:
    """Returnerer symbol og farve for en klasse."""
    klasse_norm = KLASSE_ALIAS.get(klasse, klasse)
    return SYMBOLER.get(klasse_norm, {"symbol": "?", "farve": "#9E9E9E"})


def byg_prompt_sektion(parameter: str, klasse: str, værdi: float = None) -> str:
    """
    Bygger en færdig tekstsektion til AI-promptet for ét næringsstof.

    Eksempel output:
        KALIUMTAL (Kt): 12.0 — Høj
        Kaliumtallene er høje. Her kan der spares på kaliumgødningen.
        Anbefaling: Reducer K-tilførsel.
    """
    tekst = get_handlingstekst(parameter, klasse)
    if not tekst:
        return f"{parameter}: {klasse} (ingen handlingstekst tilgængelig)"

    symbol_info = get_symbol(klasse)
    værdi_str = f" {værdi}" if værdi is not None else ""
    klasse_norm = KLASSE_ALIAS.get(klasse, klasse)

    linjer = [
        f"{symbol_info['symbol']} {parameter}:{værdi_str} — {klasse_norm}",
        tekst["fuld"],
    ]
    if tekst.get("handling"):
        linjer.append(f"→ {tekst['handling']}")

    return "\n".join(linjer)


def byg_fuld_prompt_kontekst(næringsstoffer: dict) -> str:
    """
    Bygger komplet prompt-kontekst for alle næringsstoffer i én mark.

    Input:
        næringsstoffer = {
            "Rt":  {"værdi": 5.9, "klasse": "Lavt"},
            "Pt":  {"værdi": 3.3, "klasse": "Middel"},
            "Kt":  {"værdi": 8.5, "klasse": "Høj"},
            "Mgt": {"værdi": 3.7, "klasse": "Lavt"},
        }
    """
    sektioner = []
    for param, data in næringsstoffer.items():
        sektion = byg_prompt_sektion(
            parameter=param,
            klasse=data.get("klasse", ""),
            værdi=data.get("værdi"),
        )
        sektioner.append(sektion)
    return "\n\n".join(sektioner)


# ---------------------------------------------------------------------------
# QUICK-TEST
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== Handlingstekster — quick test ===\n")

    # Simuler en mark fra Agillix-rapporten (Mark 8-0: Rt 5.9, Pt 3.3, Kt 8.5, Mgt 3.7)
    mark_data = {
        "Rt":  {"værdi": 5.9, "klasse": "Lavt"},
        "Pt":  {"værdi": 3.3, "klasse": "Middel"},
        "Kt":  {"værdi": 8.5, "klasse": "Høj"},
        "Mgt": {"værdi": 3.7, "klasse": "Lavt"},
    }

    print("Mark 8-0 (Hans Christiansen — generiske tekster, ikke persondata):\n")
    print(byg_fuld_prompt_kontekst(mark_data))

    print("\n\n=== Enkelt opslag ===")
    print(get_handlingstekst("Kt", "Meget lavt"))

    print("\n=== Symbol ===")
    print(get_symbol("Meget høj"))
