# AI Gødningsscreening - Konkret Projektplan
**Opdateret: 10. februar 2026**

---

## Projektteam

**Udvikling:**
- Jonas (Webmaster): Teknisk implementering, AI-integration, prototype

**Dataindsamling:**
- Vibeke: Lovgivning og regelsæt
- Birgitte: Tekniske specifikationer

**Stakeholders:**
- Christian (Direktør for planteavl): Faglig validering og godkendelse
- Daniel (Salgsleder): Use case definition og test med sælgere

**IT:**
- Godkendelse af teknisk platform
- API access hvis nødvendigt

---

## KRITISK BESLUTNING: Platform

**Status: Afventer svar fra gruppen** ⏳

### Option 1: Microsoft Copilot Agent
**Fordele:**
- Godkendt af IT
- Integration med Teams/SharePoint
- Ingen API-godkendelse nødvendig

**Ulemper:**
- Lavere AI-kvalitet
- Mindre fleksibel
- Langsom ved komplekse queries

### Option 2: Webapp med Claude/GPT-4 API
**Fordele:**
- Meget bedre AI-kvalitet
- Fuld kontrol over logik
- Hurtigere udvikling
- Bedre brugeroplevelse

**Ulemper:**
- Kræver API-godkendelse fra IT
- Jonas skal bygge interface
- Hosting og deployment

**Action:** Jonas sender følgende til gruppen:
```
Hej team,

Vi har brug for at beslutte den tekniske platform inden vi kan komme videre.

To muligheder:
1. Microsoft Copilot Agent (godkendt af IT, men lavere kvalitet)
2. Webapp med Claude API (bedre kvalitet, men kræver godkendelse)

Jeg anbefaler Option 2 hvis IT kan godkende det, fordi AI-kvaliteten er 
markant bedre til agronomisk reasoning. Men jeg kan levere begge løsninger.

Kan vi få en beslutning inden fredag 14. feb?

Mvh Jonas
```

---

## Fase 1: Proof-of-Concept (UGE 6-8)
**Deadline: Ultimo februar**

### Status lige nu (10. feb):
✅ **DONE:**
- SoilOptix parser bygget og testet (115 prøver parsed)
- Kategorisering af næringsstoffer implementeret (Large Demand → Suspicious Surplus)
- Prioritering af marker efter samlet behov
- Kan identificere top 5 marker med størst behov

### Denne uge (uge 7: 10-16 feb):

**Mandag-Tirsdag (10-11 feb):**
- [ ] Send email til gruppe om platformvalg (se ovenfor)
- [ ] Byg AI-lag med Claude API lokalt på M4 Mini
- [ ] Test med 3-5 konkrete spørgsmål:
  - "Hvilke marker har størst behov for gødning?"
  - "Hvad anbefaler du til mark 6-0?"
  - "Hvilke marker mangler fosfor?"

**Onsdag-Torsdag (12-13 feb):**
- [ ] Implementer beregning af NPK-behov baseret på afgrøde
- [ ] Tilføj produktanbefalinger (YaraBela SULFAN 24 etc.)
- [ ] Test med vinterhvede middel udbytte scenario

**Fredag (14 feb):**
- [ ] Få beslutning om platform fra gruppen
- [ ] Demo til Christian (hvis muligt)
- [ ] Dokumenter findings og feedback

### Næste uge (uge 8: 17-23 feb):

**Hvis Copilot:**
- [ ] Port logik til Copilot Studio
- [ ] Test i SharePoint miljø
- [ ] Dokumenter begrænsninger

**Hvis Webapp:**
- [ ] Byg simpel web-interface
- [ ] Deploy til test-miljø
- [ ] Setup API keys hos IT

**Begge scenarier:**
- [ ] Test med resten af lab-resultaterne (alle 5 filer)
- [ ] Valider anbefalinger med Christian
- [ ] Dokumenter eventuelle afvigelser

**Output til demo (slut februar):**
- Fungerende prototype (Copilot eller webapp)
- Demo med 10-20 reelle jordprøver
- Dokumentation af testresultater
- Christians godkendelse af faglig kvalitet

---

## Fase 2: Iteration og Test (UGE 9-11)
**Marts 2026**

### Uge 9 (24 feb - 2 mar):
- [ ] Implementer feedback fra Christian
- [ ] Tilføj manglende features baseret på demo
- [ ] Skalér til alle 117+ jordprøver

### Uge 10 (3-9 mar):
- [ ] Test med 2-3 sælgere (udvalgt af Daniel)
- [ ] Indsaml feedback på brugervenlighed
- [ ] Identificer pain points

### Uge 11 (10-16 mar):
- [ ] Implementer sælger-feedback
- [ ] Performance optimering
- [ ] Dokumentation til sælgere (hvordan-guide)

---

## Fase 3: Deployment (UGE 12-13)
**Marts 2026**

### Uge 12 (17-23 mar):
- [ ] Final test med Daniel og team
- [ ] Deployment til produktion
- [ ] Onboarding session for sælgere

### Uge 13 (24-30 mar):
- [ ] Monitoring af faktisk brug
- [ ] Hurtige bugfixes hvis nødvendigt
- [ ] Indsaml success metrics

**31. marts: PROJEKT LEVERET** ✅

---

## Risiko-Mitigation Plan

### Risiko 1: Platformbeslutning forsinket
**Sandsynlighed:** Medium  
**Impact:** Høj (blokerer udvikling)  
**Mitigation:** 
- Byg begge løsninger parallelt (1 dag ekstra arbejde)
- Eskalér til Christian hvis ingen beslutning fredag 14. feb

### Risiko 2: AI-kvalitet ikke god nok (hvis Copilot)
**Sandsynlighed:** Medium  
**Impact:** Høj (faglig kvalitet truet)  
**Mitigation:**
- Test grundigt i uge 8
- Hvis utilfredsstillende: skift til webapp med Claude API
- Få IT til at prioritere API-godkendelse

### Risiko 3: Christians validering fejler
**Sandsynlighed:** Lav  
**Impact:** Kritisk (kan ikke deploye)  
**Mitigation:**
- Involvér Christian tidligt og ofte (hver uge)
- Få faglig input INDEN implementation
- Dokumentér alle agronomiske antagelser

### Risiko 4: Sælgere bruger ikke værktøjet
**Sandsynlighed:** Medium  
**Impact:** Høj (forretningsmål opnås ikke)  
**Mitigation:**
- Involvér sælgere i test fase (uge 10)
- Lav super simpel interface
- Gør værdi krystalklart ("Dette sparer dig 2 timer per kunde")

### Risiko 5: Data-kvalitet varierer
**Sandsynlighed:** Høj  
**Impact:** Medium (nogle marker kan ikke analyseres)  
**Mitigation:**
- Definer minimumskrav klart
- Vis fejlmeddelelser tydeligt til bruger
- Log manglende data for opfølgning

---

## Success Metrics

**Tekniske:**
- ✅ Parse rate: >95% af SoilOptix filer læses korrekt
- ⏳ Response tid: <5 sekunder per forespørgsel
- ⏳ Uptime: >99% i produktionsmiljø

**Forretningsmæssige:**
- ⏳ Tid sparet: 50% reduktion fra jordanalyse til salgstilbud
- ⏳ Brugeradoption: >80% af sælgere bruger værktøjet
- ⏳ Feedback score: >4/5 fra sælgere

**Faglige:**
- ⏳ Christians godkendelse: ✓
- ⏳ Anbefalinger matcher MarkOnline: ±10% margin
- ⏳ Compliance: 100% overholdelse af P-loft

---

## Næste Handlinger (Prioriteret)

**🔥 KRITISK (nu):**
1. Send email til gruppe om platformvalg
2. Byg AI-lag med Claude API
3. Test med første 3 spørgsmål

**📅 DENNE UGE:**
4. Implementer NPK-beregning
5. Få platformbeslutning fredag 14. feb
6. Book demo med Christian til uge 8

**🔮 NÆSTE UGE:**
7. Skalér til alle 5 lab-filer
8. Demo til Christian
9. Start Copilot/webapp implementation

---

## Kommunikationsplan

**Ugentlig status til Christian:**
- Hver mandag kl. 10:00
- Email med bullets: Done, Doing, Blockers
- 5 min opfølgning hvis nødvendigt

**Feedback fra gruppe:**
- Slack kanal: #goedningsscreening
- Quick questions: instant messaging
- Større beslutninger: email med deadline

**Demo-møder:**
- Uge 8 (slut feb): Christian - faglig validering
- Uge 10 (start mar): Daniel + 2 sælgere - brugertest
- Uge 12 (mid mar): Større gruppe - final approval

---

## Notes til Jonas

**Når du arbejder på projektet:**
- Start altid med at checke denne plan
- Opdatér checkboxes når noget er færdigt
- Tilføj nye risici hvis de dukker op
- Log beslutninger i bundtekst (Decision Log)

**Når du sidder fast:**
1. Check om det er en known risk → se mitigation
2. Check om du afventer beslutning → eskalér
3. Check om det er scope creep → push tilbage

**Når noget ændrer sig:**
1. Opdatér denne plan
2. Kommunikér til relevant stakeholder
3. Juster milestones hvis nødvendigt

---

## Decision Log

**10. feb 2026:**
- Besluttet at bygge proof-of-concept med Python + Claude API først
- Parser og kategorisering implementeret og testet
- Afventer platformbeslutning fra gruppe

*Tilføj nye beslutninger her...*
