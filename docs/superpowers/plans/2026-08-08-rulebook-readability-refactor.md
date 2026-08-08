# FEBUS Rulebook Readability Refactor — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prerobiť FEBUS rulebook tak, aby bol citovateľný (globálne číslovanie článkov s prefixmi), jazykovo konzistentný (must/may/should, jednotná terminológia) a použiteľný pre tri publiká (šermiar, rozhodca, organizátor) — bez zmeny významu pravidiel, pokiaľ úloha výslovne neoznačí zmenu ako **OBSAHOVÁ ZMENA**.

**Architecture:** Dokumentačný refactor v 12 sekvenčných úlohách: najprv stabilizácia štruktúry (premenovanie súborov na kanonické poradie, reorganizácia 03-general, deduplikácia), potom jazykové vrstvy (kritické opravy, normatívne slovesá, zámená, terminológia), potom číslovanie článkov a od neho závislé artefakty (tabuľka trestov, prehľadové tabuľky, príklady, quick-reference), nakoniec verziovanie a QA. Poradie je záväzné — číslovanie (Úloha 8) sa smie robiť až keď sa už nemení počet a poradie pravidiel.

**Tech Stack:** Markdown, git, bash (grep/sed na verifikáciu), Python 3 + WeasyPrint (generate_pdf.py).

## Global Constraints

- Text pravidiel je **anglický**; britský pravopis (`organise`, `penalise`, `offence`, `centre`).
- **Žiadna zmena významu pravidla** bez explicitného označenia kroku ako **OBSAHOVÁ ZMENA** — tie vyžadujú schválenie federácie a sú sústredené v Úlohe 11 a 12.
- Normatívne slovesá: **must / must not** = povinnosť/zákaz, **may** = dovolenie, **should** = odporúčanie, **can** = schopnosť. Slová `shall` a väzba `is going to` sa v pravidlách nesmú vyskytovať (deklarované v Úlohe 5).
- Kanonické termíny (zavádza Úloha 7): `fencer`, `bout`, `exchange`, `priority`, `point` (bod v skóre) vs `hit` (fyzický zásah), `arena`, `on-guard line`, `Assistant Referee`, `Organising Team`, `Head of the Refereeing Team`, `cross-guard`, `stop-hit`, `off-target` vs `forbidden target`.
- Formát ID článku: tučné na začiatku odseku — `**G.12** The exchange stops when…`; pod-body ako `a)`, `b)`; citácia `G.12(a)`. Prefixy: E, G, RoW, LS, R, S, SB, O, D (tabuľka v Úlohe 8).
- Informatívny text výhradne v blockquote `> **Note:** …` alebo `> **Example:** …` — nikdy vo vete pravidla.
- Čísla riadkov v tomto pláne platia pre stav repa k 2026-08-08 (commit c2478b2 + necommitnuté zmeny). Po Úlohe 1 sa menia názvy súborov a po každej úlohe sa čísla posúvajú — **vyhľadávaj podľa citovaného textu, nie podľa čísla riadku**.
- Súbory miešajú typografické (’ ‘ “ ”) a rovné (' ") úvodzovky. BEFORE citáty v pláne uvádzajú známy skutočný tvar; ak presný reťazec nenájdeš, skús variant s opačným typom úvodzoviek, než usúdiš, že text neexistuje.
- Po každej úlohe: PDF sa musí dať vygenerovať (postup vo Verifikácii Úlohy 1) a link-check (Úloha 1, krok 6) musí prejsť.
- Commituj po každej úlohe. Správy commitov v angličtine, ukončené `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.
- Pracuj na novej vetve `readability-refactor`. Repo má necommitnuté zmeny z konzistenčného auditu (kapitoly, appendices, README, smernica, netrackovaný generátor PDF) — **pred vytvorením vetvy ich commitni samostatne** na `master`, napr.: `git add -u && git add 10-sword-and-buckler.md FEBUS_smernica_o_rozhodcoch_navrh.md generate.sh generate_pdf.py requirements.txt febus_logo.jpg && git commit -m "chore: consistency fixes, new chapters and PDF generator"`. Predtým over `git status` a z prípravného commitu vyhoď (`git reset <súbor>`), čo tam nepatrí. Binárne/generované súbory (.DS_Store, vygenerované PDF, staré logo) necommituj — Úloha 1 pridáva .gitignore.

---

### Úloha 1: Kanonické poradie kapitol — premenovanie súborov, odkazy, README, generate_pdf.py

**Files:**
- Rename: 7 súborov kapitol (git mv, pozri kroky)
- Modify: `README.md`, `CLAUDE.md`, `05-longsword.md`, `07-sabre.md`, `04-right-of-way.md`, `08-sword-and-buckler.md` (odkazy), `generate_pdf.py`
- Create: `scripts/check_links.sh`

**Interfaces:**
- Produces: kanonické názvy súborov, na ktoré sa odkazujú všetky ďalšie úlohy: `01-intro.md`, `02-equipment.md`, `03-general.md`, `04-right-of-way.md`, `05-longsword.md`, `06-rapier.md`, `07-sabre.md`, `08-sword-and-buckler.md`, `09-organisational.md`, `10-disciplinary.md`; `scripts/check_links.sh` (exit 0 = žiadne rozbité odkazy); `generate_pdf.py` s `self.num_root_files`.

- [ ] **Krok 1: Vytvor vetvu a premenuj súbory (dva permutačné cykly cez temp názvy)**

```bash
git checkout -b readability-refactor
# Cyklus A: 04→05→06→09→04
git mv 09-right-of-way.md tmp-row.md
git mv 06-organisational.md 09-organisational.md
git mv 05-rapier.md 06-rapier.md
git mv 04-longsword.md 05-longsword.md
git mv tmp-row.md 04-right-of-way.md
# Cyklus B: 07→10→08→07 (10-sword-and-buckler.md musí byť trackovaný —
# zabezpečuje prípravný commit z Global Constraints, inak git mv zlyhá)
git mv 10-sword-and-buckler.md tmp-snb.md
git mv 07-disciplinary.md 10-disciplinary.md
git mv 08-sabre.md 07-sabre.md
git mv tmp-snb.md 08-sword-and-buckler.md
```

- [ ] **Krok 2: Oprav medzisúborové odkazy v kapitolách**

| Súbor (nový názov) | Nájsť | Nahradiť |
|---|---|---|
| `05-longsword.md` | `(09-right-of-way.md)` | `(04-right-of-way.md)` |
| `07-sabre.md` | `(09-right-of-way.md)` | `(04-right-of-way.md)` |
| `04-right-of-way.md` | `(04-longsword.md)` | `(05-longsword.md)` |
| `04-right-of-way.md` | `(08-sabre.md)` | `(07-sabre.md)` |
| `08-sword-and-buckler.md` | `(05-rapier.md)` | `(06-rapier.md)` |

- [ ] **Krok 3: Prepíš README.md v kanonickom poradí**

```markdown
# FEBUS Tournament Rulebook

## Introduction

- [Introduction](01-intro.md)

## Equipment Regulations

- [Technical & Equipment Standards](02-equipment.md)

## The Principles of Scoring

- [General rules for all weapons](03-general.md)
- [Right of Way and Priority Rules](04-right-of-way.md)
- [Longsword specific rules](05-longsword.md)
- [Rapier and side weapons specific rules (rapier, dagger, cloak)](06-rapier.md)
- [Sabre specific rules](07-sabre.md)
- [Sword and Buckler specific rules](08-sword-and-buckler.md)

## Organisation and Bout Management

- [Organisational Rules](09-organisational.md)
- [Fencing etiquette and disciplinary rules](10-disciplinary.md)

## Appendix

- [Glossary](appendices/01-glossary.md)
- [Table of Offences and Penalties](appendices/02-penalties.md)
```

(Názvy odkazov zámerne zodpovedajú H1 nadpisom cieľových súborov — `Technical & Equipment Standards`, `Organisational Rules` — aby prozaické odkazy v texte sedeli s názvami kapitol.)

- [ ] **Krok 4: Aktualizuj CLAUDE.md** — v sekcii „Repository Structure" prepíš zoznam súborov podľa nového mapovania (04=right-of-way, 05=longsword, 06=rapier, 07=sabre, 08=sword-and-buckler, 09=organisational, 10=disciplinary).

- [ ] **Krok 5: Oprav zber súborov a číslovanie príloh v generate_pdf.py.** Dve chyby: (a) glob zbiera aj `FEBUS_smernica_o_rozhodcoch_navrh.md` ako 11. kapitolu PDF (slovenský návrh smernice nie je súčasť rulebooku); (b) číslo prílohy je natvrdo `chapter_num - 9`, takže prílohy dnes vychádzajú A3/A4.

V `collect_markdown_files` uprav filter root súborov:

```python
            if file.name not in ['README.md', 'CLAUDE.md'] \
                    and not file.name.startswith('FEBUS_smernica'):
```

za `root_files.sort(key=lambda x: x[0])` pridaj:

```python
        self.num_root_files = len(root_files)
```

a v `__init__` inicializuj `self.num_root_files = 0`. Potom nahraď **všetkých 7 výskytov** `A{chapter_num - 9}` za `A{chapter_num - self.num_root_files}` — 3× v `extract_headers_for_toc` a 4× v `add_header_numbering` (vrátane vetvy `is_first_header`, ktorá čísluje H1 nadpis každej prílohy). Mechanicky:

```bash
sed -i '' 's/chapter_num - 9/chapter_num - self.num_root_files/g' generate_pdf.py
```

- [ ] **Krok 6: Vytvor scripts/check_links.sh a .gitignore**

```bash
#!/bin/bash
# Overí, že každý [text](*.md) odkaz smeruje na existujúci súbor.
set -u
fail=0
for src in *.md appendices/*.md; do
  dir=$(dirname "$src")
  while IFS= read -r target; do
    [ -z "$target" ] && continue
    if [ ! -f "$dir/$target" ] && [ ! -f "$target" ]; then
      echo "BROKEN: $src -> $target"; fail=1
    fi
  done < <(grep -oE '\]\([^)#]+\.md' "$src" | sed 's/](\(.*\)/\1/')
done
exit $fail
```

```bash
chmod +x scripts/check_links.sh
printf '.DS_Store\nvenv/\nfebus_rulebook.pdf\n' > .gitignore
```

- [ ] **Krok 7: Verifikácia**

```bash
ls *.md                                   # očakávaný zoznam: 01-intro … 10-disciplinary, CLAUDE.md, README.md (+FEBUS_smernica*)
grep -rn "09-right-of-way.md\|04-longsword.md\|05-rapier.md\|08-sabre.md\|10-sword-and-buckler.md\|06-organisational.md\|07-disciplinary.md" *.md appendices/*.md
                                          # očakávané: žiadny výskyt (0 riadkov)
scripts/check_links.sh                    # očakávané: exit 0, žiadne BROKEN
grep -c "chapter_num - 9" generate_pdf.py # očakávané: 0
python3 -m venv venv 2>/dev/null; source venv/bin/activate; pip install -q -r requirements.txt; python generate_pdf.py
                                          # očakávané: "PDF vygenerované: febus_rulebook.pdf";
                                          # TOC má presne 10 kapitol (žiadna kapitola "Smernica…"),
                                          # prílohy A1/A2 v TOC AJ v tele dokumentu (nadpis "A1. Glossary")
```

- [ ] **Krok 8: Commit**

```bash
git add .gitignore *.md appendices scripts generate_pdf.py
git commit -m "refactor: rename chapters to canonical reading order, fix links and appendix numbering"
```

(Nepoužívaj `git add -A` — v pracovnom strome sú nesúvisiace súbory: .DS_Store, staré PDF, logá.)

---

### Úloha 2: Reorganizácia 03-general.md — podnadpisy, Forbidden actions, Dominance

**Files:**
- Modify: `03-general.md`, `07-sabre.md` (odkaz na dominance sekciu)

**Interfaces:**
- Consumes: kanonické názvy z Úlohy 1.
- Produces: štruktúru 03-general.md, na ktorú sa viaže číslovanie v Úlohe 8: H2 sekcie `The Process of the Bouts` (s H3 podsekciami), `The methods of scoring hits` (s H3 `Dominance`), `Forbidden actions (all weapons)`, `Close quarter combat`.

- [ ] **Krok 1: Vlož H3 podnadpisy do „The Process of the Bouts"** — číslovaný zoznam 1–29 rozdeľ takto (položky identifikuj podľa textu; číslovanie zoznamov v podsekciách nechaj priebežné 1–29, markdown to zvládne cez pokračovanie, alebo reštartuj v každej podsekcii — reštart je v poriadku, definitívne ID dostanú pravidlá až v Úlohe 8):
  - `### Starting the bout` — položky 1–7 (od „Each bout is performed" po „…with the word 'Fence!'.")
  - `### Stopping the exchange` — položky 8–12 (od „The exchange stops when the Referee commands" po „…annulment of other valid hits that happened afterwards.")
  - `### Arena boundaries` — položky 13–17 (od „When a competitor crosses one of the boundaries" po „…incurs no penalty.")
  - `### Restarting, video review and end of the bout` — položky 18–22 (od „After each valid hit" po „…before leaving the arena.")
  - `### Equipment failure and injury breaks` — položky 23–24
  - `### Forfeits and withdrawal` — položky 25–29

- [ ] **Krok 2: Vytiahni dominanciu do vlastnej H3 sekcie.** Z „The methods of scoring hits" odstráň pod-položku 4.5 („The referee may call an action as a valid hit, when a weapon action results in a passively constraining position…") a na koniec sekcie vlož:

```markdown
### Dominance

1. The Referee may award a hit when a weapon action results in a passively
   constraining position for the opponent, held for a considerable time during
   which the opponent is unable to break free. Dominance may be the result of
   grappling, locks involving the weapon, or opposing actions that restrain the
   opponent's weapon movement.

2. The Referee awards the hit by calling 'Halt!' once they find all criteria of
   dominance met. Hits received while the dominant position is upheld are not
   valid.

3. Dominance does not apply when the opponent can practically break free and
   initiate valid actions, even if the weapon contact is not completely broken.
   It is at the Referee's discretion to judge the validity of dominance actions.

4. Dominance achieved by grappling or close quarter combat applies only in the
   Longsword category.
```

(Znenie je rozklad pôvodného odseku bez zmeny významu; oprava `result of of grappling` je tu už zapracovaná.)

- [ ] **Krok 3: Povýš všeobecné zákazy.** Súčasná H3 `### Forbidden actions` (vnorená pod `## Close quarter combat`) sa rozdelí:

Pred `## Close quarter combat` vlož novú H2 sekciu:

```markdown
## Forbidden actions (all weapons)

1.  Punching, kicking, violent jostling, and throwing the weapon are strictly
    forbidden.

2.  Excessive force, brutality or unnecessary violence are forbidden.

3.  Hitting the back of the head, the spine, the groin, the back of the knee or
    the foot is forbidden and will be penalised (see penalty 1.5).

4.  It is forbidden to hit with the cross-guard, where applicable, or with the
    basket or bell guard (see penalty 1.5).

5.  Turning the head or covering a valid target with a non-valid one belongs to
    the first group of offences.

6.  Hitting the arena floor with any weapon due to bad measure in an action will
    be penalised according to the first group of offences (cases resulting from
    the opponent's interactions, accidental touches, and touching the floor
    after having hit the opponent, may be disregarded by the Referee).
```

a pôvodnú H3 `### Forbidden actions` pod Close quarter combat nahraď:

```markdown
### Forbidden actions in close quarter combat

1.  Neck-wrenching, lifting the opponent off the ground, full application of
    joint locks, small-joint manipulation, or other potentially dangerous
    wrestling techniques are strictly forbidden.
```

(Pôvodné položky 3 a 6 hovorili to isté dvakrát — zlúčené do bodov 3+4 novej sekcie. Punching/kicking/throwing the weapon platia univerzálne — presunuté z CQC bodu 1. Významovo sa nič nemení.)

- [ ] **Krok 4: Verifikácia**

```bash
grep -n "^## " 03-general.md
# očakávané poradie: The Process of the Bouts / The methods of scoring hits / Forbidden actions (all weapons) / Close quarter combat
grep -c "Hitting the back of the head" 03-general.md   # očakávané: 1 (duplicita zlúčená)
grep -n "result of of" 03-general.md                    # očakávané: 0 riadkov
scripts/check_links.sh
```

- [ ] **Krok 5: Commit** — `git commit -am "refactor(general): subsection headings, promote universal forbidden actions, extract dominance"`

---

### Úloha 3: Deduplikácia — jedno kanonické miesto pre každé pravidlo

**Files:**
- Modify: `03-general.md`, `09-organisational.md`, `02-equipment.md`

**Interfaces:**
- Produces: kanonické domovy — parametre bojov v `09-organisational.md`, kontrola výstroja v `02-equipment.md`, tri výzvy v `10-disciplinary.md`. Ostatné výskyty = jednovetné odkazy.

- [ ] **Krok 1: Parametre bojov → kanonicky v 09-organisational.** V `03-general.md` nahraď položku 6 („Pool bouts last 2 minutes… The Organising Team may announce different bout durations…") za:

```markdown
6.  Bout durations, hit limits and tie-break procedures are set out in the
    [Organisational Rules](09-organisational.md). Unless the Organising Team
    announces otherwise, the defaults are: pool bouts 2 minutes or 5 points;
    direct elimination bouts 2 × 2 minutes (with a one-minute rest) or 7
    points. The Timekeeper announces the end of time. Only the Referee may
    stop the bout.
```

Zároveň v `03-general.md` položke 20 (overtime — „In case the points of the fencers are equal…") nechaj plné znenie: je to jediné miesto s pravidlom o žrebovanej priorite; `09-organisational.md` body o deciding hit (pools bod 4, DE bod 7) doplň o odkaz `…as described in the [General Rules](03-general.md).` na konci vety „…if scores are still equal at the end of the extra minute."

- [ ] **Krok 2: Kontrola výstroja → kanonicky v 02-equipment.** V `03-general.md` nahraď položku 3 („An additional equipment check will be performed by the referee…") za:

```markdown
3.  Equipment checks before and during the competition, and the penalties for
    nonconforming equipment, are set out in the
    [Technical & Equipment Standards](02-equipment.md).
```

V `09-organisational.md` sekcii „Fencer readiness and presence" nahraď položku 4 („The Refereeing Team will check the readiness of fencers…") za:

```markdown
4.  The Refereeing Team checks the readiness of fencers (completeness of safety
    gear and weapons) before the indicated start of bouts, as set out in the
    [Technical & Equipment Standards](02-equipment.md). The Referee may repeat
    this check at any time.
```

- [ ] **Krok 3: Tri výzvy → kanonicky v 10-disciplinary.** V `09-organisational.md` položke 3 tej istej sekcie over, že text len odkazuje (už áno — „the procedure described in the disciplinary rules applies"), a oprav chybný názov cieľa: `see penalty 0.2 and the Fencing etiquette section` → `see penalty 0.2 and [Fencing etiquette and disciplinary rules](10-disciplinary.md), section 'The Fencers'`. (Dopredný odkaz: sekciu 'The Competitors' premenuje na 'The Fencers' Úloha 7, Krok 1 — odkaz na súbor je platný už teraz a `check_links.sh` kontroluje len existenciu súboru, nie sekcie.)

- [ ] **Krok 4: Postup merania flexibility → jeden článok.** V `02-equipment.md` je identický odsek o meraní flexibility 3× (longsword bod 6, rapier bod 4, sabre bod 5). Na začiatok sekcie `### Weapons` vlož všeobecný odsek:

```markdown
The flexibility of a blade is measured by applying pressure on the blade point
against scales, with one hand firmly placed on the pommel. The blade's
flexibility is the maximum value (in kg) displayed on the scales before the
blade reaches full bend.
```

a pri zbraniach ponechaj len limity: longsword bod 6 → `The acceptable flexibility range for longsword blades is 9–16 kg.`; rapier bod 4 → ponechaj prvé dve vety (`The maximum length of the blade including *ricasso* is 110cm. The blade must be flexible, especially from the middle of the rapier to the point in order not to pose a risk in thrust attacks.`) a zakonči `For rapier blades, the acceptable flexibility is 10 kg or less.`; sabre bod 5 → `For sabre blades, the acceptable flexibility is 10 kg or less.`

(Robí sa teraz — pred číslovaním v Úlohe 8 — aby sa počet článkov v 02-equipment.md už nemenil a pridelené E-čísla zostali stabilné.)

- [ ] **Krok 5: Verifikácia**

```bash
grep -c "2 minutes of effective fencing time" 03-general.md      # očakávané: 0 (parametre už len v 09)
grep -c "additional equipment check will be performed" 03-general.md  # očakávané: 0
grep -n "Fencing etiquette section" 09-organisational.md          # očakávané: 0 riadkov
grep -c "The flexibility of the blade is measured" 02-equipment.md    # očakávané: 0
grep -c "flexibility of a blade is measured" 02-equipment.md          # očakávané: 1
scripts/check_links.sh
```

- [ ] **Krok 6: Commit** — `git commit -am "refactor: single canonical home for bout parameters, equipment checks, three-call procedure and flexibility measurement"`

---

### Úloha 4: Kritické jazykové opravy — rozbité definície, gramatika, negácie

**Files:**
- Modify: `03-general.md`, `06-rapier.md`, `05-longsword.md`, `09-organisational.md`, `10-disciplinary.md`, `02-equipment.md`

Každý bod nižšie je nahradenie presného znenia (nájdi podľa BEFORE, nahraď AFTER). Význam sa nemení.

- [ ] **Krok 1: Definície double hitu**

`03-general.md` — BEFORE: `A double hit occurs when both fencers get hit within a period of fencing time, but are not simultaneous actions, are evaluated according to the rules or each specific weapon.`
AFTER: `A double hit occurs when both fencers are hit within one period of fencing time but the actions are not simultaneous. Double hits are evaluated according to the weapon-specific rules.`

`06-rapier.md` — BEFORE: `A double hit occurs when two valid hits that land within one period of fencing time.`
AFTER: `A double hit occurs when two valid hits land within one period of fencing time.`

`05-longsword.md` — BEFORE: `The double hit on the other hand, is the result of a clearly faulty action on the part of one of the fencers, according to the rules. Therefore, when there is not an interval of fencing time between the hits.`
AFTER: `A double hit, on the other hand, occurs when there is no interval of fencing time between the hits and it is the result of a clearly faulty action on the part of one of the fencers, as defined by these rules.`

- [ ] **Krok 2: Gramatické chyby**

| Súbor | BEFORE | AFTER |
|---|---|---|
| `09-organisational.md` | `Main referee must be able conduct and manage bouts in English.` | `The Referee must be able to conduct and manage bouts in English.` |
| `10-disciplinary.md` (2×: 3. aj 4. skupina) | `keeps the position in the ranking s obtained` | `keeps the position in the ranking obtained` |
| `10-disciplinary.md` | `exclusion from the competition, suspension from the remainder of the tournament. The fencer keeps` | `exclusion from the competition and suspension from the remainder of the tournament). The fencer keeps` (uzavri zátvorku otvorenú pred „exclusion") |
| `10-disciplinary.md` | `penalised by a BLACK CARD (exclusion from the competition.` | `penalised by a BLACK CARD (exclusion from the competition).` |
| `03-general.md` | `upon each subsequent cases within the bout, a hit will be scored against him (as if they had been hit).` | `on each subsequent occasion within the bout, a point is scored against the fencer (as if they had been hit).` |
| `03-general.md` | `Should a competitor cross the boundary of the arena completely — i.e. with both feet — without having scored any valid hits before crossing the limit of the arena (see penalty 0.3)` | `If a fencer crosses the boundary of the arena with both feet without having scored a valid hit before crossing (see penalty 0.3):` |
| `10-disciplinary.md` | `he can also propose to the the expulsion` | `they can also propose the expulsion` |

- [ ] **Krok 3: Zavádzajúce negácie („no … must")**

`02-equipment.md` — BEFORE: `If a contestant leans their head in any standard angle, no unprotected part or skin must be visible.`
AFTER: `The head protection must leave no skin or unprotected area visible when the fencer tilts their head at any normal angle.`

`02-equipment.md` — BEFORE: `Every part of the body must be covered. No open space must be left between the gloves and the jacket.`
AFTER: `Every part of the body must be covered. The gloves must overlap the jacket sleeves, leaving no gap.`

`07-sabre.md` — BEFORE: `Hits landed with blade contact (through a parry or over the cross/guard) are only valid if the strength of the hit is not meaningfully decreased.`
AFTER: `Hits landed with blade contact (through a parry or over the cross-guard) are valid only if the hit retains meaningful force.`

- [ ] **Krok 4: Najhoršie súvetia (FIE legalese) — rozklad bez zmeny významu**

`03-general.md` — BEFORE: `However, if when the Referee stops the exchange, a hit that the referee believed invalid and ignored before the conclusion of the last exchange proves to have been valid, the Referee shall, if possible, make a decision in relation to the actual first hit, even if this results in the annulment of other valid hits that happened afterwards.`
AFTER: `If a hit that the Referee ignored as invalid proves, when the exchange is stopped, to have been valid, the Referee must, if possible, re-judge the exchange from that actual first hit. Later hits are annulled, even if they were valid.`

`10-disciplinary.md` — BEFORE: `In his capacity as director of the bout and arbiter of hits, he can, in accordance with the rules, penalise the competitors, either by refusing to award a hit which they have in fact made on the opponent, or by awarding against them a hit which they have not in fact received, or by excluding them from the competition which he is refereeing, all, according to the circumstances, with or without prior warning. In these circumstances, and if he has judged on a matter of fact, his decisions are irrevocable`
AFTER: `As director of the bout and arbiter of hits, the Referee may, in accordance with the rules and — according to the circumstances — with or without prior warning: a) refuse to award a hit actually made; b) award a point against a fencer for a hit not actually received; c) exclude a fencer from the competition. When the Referee has judged on a matter of fact, the decision is irrevocable.`

`09-organisational.md` (protokol po výmene) — BEFORE: `After stopping an exchange, the Referee consults with the Assistant and proposes a result. If the fencers accept the decision (they say nothing), the fight continues with the proposed score. If they don’t agree with the Referee, but they agree with each other, the Referee may make a decision according to their wishes. If any of the fencers protests and the fencers disagree with each other, the Referee will decide whether to assign a point (being completely sure) or repeat the exchange.` (pozor: `don’t` s typografickým apostrofom)
AFTER:

```markdown
3.  After stopping an exchange, the Referee consults the Assistant and proposes
    a result. Then:
    a) if both fencers accept the decision (they say nothing), the bout
       continues with the proposed score;
    b) if the fencers disagree with the Referee but agree with each other, the
       Referee may decide according to their shared account;
    c) if a fencer protests and the fencers disagree with each other, the
       Referee either assigns the point (only when completely sure) or repeats
       the exchange.
```

- [ ] **Krok 5: Verifikácia**

```bash
grep -rn "get hit within a period\|two valid hits that land\|able conduct\|ranking s obtained\|of of \|subsequent cases\|no unprotected part or skin must\|No open space must" *.md
# očakávané: 0 riadkov
scripts/check_links.sh
```

- [ ] **Krok 6: Commit** — `git commit -am "fix(language): repair broken definitions, grammar errors and misleading negations"`

---

### Úloha 5: „Use of Language" + normatívne slovesá (shall/will → must/may)

**Files:**
- Modify: `01-intro.md` (nová sekcia), všetky kapitoly (sweep)

**Interfaces:**
- Produces: konvenciu, na ktorú sa odkazuje check skript (Úloha 7) a všetky ďalšie texty.

- [ ] **Krok 1: Pridaj do 01-intro.md na koniec novú sekciu**

```markdown
## Use of Language

1. This Rulebook uses the following verb conventions:
   - **must** / **must not** — a binding requirement or prohibition;
   - **may** — a permission;
   - **should** — a recommendation: not binding, but expected as good practice;
   - **can** — a statement of ability or possibility, not a norm.

2. Terms in *italics* are technical terms defined in the
   [Glossary](appendices/01-glossary.md).

3. Blocks introduced with **Note:** or **Example:** are informative only; they
   illustrate the rules but contain no requirements.
```

(4. bod o číslovaní článkov doplní Úloha 8, Krok 5.)

- [ ] **Krok 2: Sweep `shall`.** Nájdi všetky výskyty: `grep -rn "\bshall\b" *.md appendices/*.md`. Každý prepíš podľa významu: povinnosť → `must`, opis budúceho deja → prítomný čas. Známe výskyty a ich prepisy:

| Miesto | BEFORE → AFTER |
|---|---|
| `02-equipment.md` (sabre) | `The total weight of a sabre shall fall between the range of 650-800 grams, counting both blade and basket.` → `The sabre, including blade and basket, must weigh between 650 and 800 g.` |
| `02-equipment.md` (cloak) | `The Organizing Team shall announce in advance, whether they allow` → `The Organising Team must announce in advance whether they allow` |
| `03-general.md` | `The opponents shall salute to the referees and the opponent` → `The opponents must salute the Referees and the opponent` |
| `03-general.md` | `the fencers shall check and sign the result sheet` → `the fencers must check and sign the result sheet` |
| `03-general.md` | `their results shall be scratched, and their opponents shall be declared` → `their results are scratched, and their opponents are declared` |
| `03-general.md` | `the score shall be recorded as if` → `the score is recorded as if` |
| `03-general.md` (CQC — Ground action) | `the Referee shall call “Halt!”` (typografické úvodzovky) → `the Referee must call 'Halt!'` |
| `03-general.md` (CQC — pád/strata zbrane) | `the Referee shall call 'Halt!'` (rovné úvodzovky) → `the Referee must call 'Halt!'` |
| `09-organisational.md` | `A summary classification table shall then be made` → `A summary classification table is then made` |
| `09-organisational.md` | `a second index will be established` → ponechaj opisné, zmeň na prítomný čas: `a second index is established` |
| `01-intro.md` | `we shall regard each individual point as a separate "duel"` → `each individual point is regarded as a separate "duel"` |

- [ ] **Krok 3: Sweep `will` a `is going to` v normatívnych vetách.** `grep -rn "is going to\|will be penalised\|will be penalized\|will be judged\|will be scored\|will have\|will be defined\|will consist\|will decide\|will announce\|will be called\|will be made\|will call\|will be counted" *.md`. Pravidlo: ak veta ukladá povinnosť/normu → `must` alebo prítomný čas; ak opisuje procedúru → prítomný čas. Známe kľúčové prepisy:

| Miesto | BEFORE → AFTER |
|---|---|
| `02-equipment.md` | `The blade will have a safe tip, this being defined as rolled, thickened or spatulated. The tip will be further built up at the event with contrasting high-visibility tape.` → `The blade must have a safe tip: rolled, thickened or spatulated. The tip must be further built up at the event with contrasting high-visibility tape.` |
| `02-equipment.md` | `A sabre will be defined as` → `A sabre is a` |
| `02-equipment.md` | `no aluminium, plastic or wooden swords will be accepted` → `aluminium, plastic or wooden swords are not accepted` |
| `07-sabre.md` | `Repeated, deliberate strikes to an off-target will be judged as` → `Repeated, deliberate strikes to an off-target area are judged as` |
| `04-right-of-way.md` | `Priority will not be given for pure footwork` → `Priority is not given for pure footwork` |
| `09-organisational.md` | `Fencers will be called by the staff of the given fencing area` → `The staff of the given fencing area call the fencers` |
| `09-organisational.md` | `these pools will consist of 7 fencers` → `the pools consist of 7 fencers` |
| `09-organisational.md` | `Medical/paramedic staff will assess` → `Medical/paramedic staff assess` |
| `03-general.md` | `the referee will announce the winner` → `the Referee announces the winner` |

Ostatné výskyty rieš rovnakým pravidlom (rozhodovací postup je deterministický; ak veta vyjadruje podmienený následok v pravidle — „a point will be scored against" — použi prítomný čas „a point is scored against").

- [ ] **Krok 4: Verifikácia**

```bash
grep -rn "\bshall\b\|is going to" *.md appendices/*.md | grep -v "^docs/"   # očakávané: 0 riadkov
grep -c "## Use of Language" 01-intro.md                                     # očakávané: 1
```

- [ ] **Krok 5: Commit** — `git commit -am "style: normative verb convention (must/may/should) and Use of Language clause"`

---

### Úloha 6: Zámená a register — singular they, opakovanie roly, archaizmy

**Files:**
- Modify: `03-general.md`, `04-right-of-way.md`, `09-organisational.md`, `10-disciplinary.md`, `02-equipment.md`

- [ ] **Krok 1: Sweep rodových zámen.** `grep -rn "\bhe\b\|\bshe\b\|\bhis\b\|\bher\b\|\bhim\b\|he/she\|she/he\|his/her\|him/her\|him/them\|His/her" *.md`. Pravidlá prepisu: (a) tam, kde vystupuje jedna osoba → singular `they/their/them`; (b) tam, kde vystupujú dvaja aktéri (útočník/obranca, šermiar/rozhodca) → opakuj rolu (`the attacker`, `the defender`, `the fencer`, `the Referee`) namiesto zámena. Kľúčové miesta:
  - `10-disciplinary.md`: `they must remain still while the referee is making her decision; when she has given her decision` → `they must remain still while the Referee is making the decision; when the Referee has given the decision`
  - `10-disciplinary.md`: `must keep his mask on until the Referee calls ‘Halt!’. He may under no circumstances address the Referee until the Referee has made his decision.` (typografické úvodzovky okolo Halt!) → `must keep their mask on until the Referee calls 'Halt!'. They must not address the Referee until the Referee has announced the decision.`
  - `10-disciplinary.md`: `if the play becomes confused, dangerous or she/he is unable` → `if the play becomes confused or dangerous, or the Referee is unable`
  - `10-disciplinary.md`: `the Referee will penalise him/them as specified` → `the Referee penalises them as specified`
  - `04-right-of-way.md` (celé zoznamy „The fencer who is attacked/attacks is alone counted as hit"): `if he makes a counter-attack on his opponent's simple attack` → `if they make a counter-attack against the opponent's simple attack` — analogicky všetkých 11 položiek (`he` → `they`, `his opponent` → `the opponent`, `his point` → `their point`, `his final movement` → `the final movement of the attack`).
  - `09-organisational.md`: `His/her results are recorded` → `Their results are recorded`
  - `10-disciplinary.md`: `by his/her gestures, attitude or language` → `by their gestures, attitude or language`; `pledges his/her honour` → pozri Krok 2.
- Pozor na legitímne výskyty mimo pravidiel (napr. slovenské texty smernice `FEBUS_smernica*` — tie nechaj bez zmeny; sweep obmedz na kapitoly 01–10 a appendices).

- [ ] **Krok 2: Archaizmy a právnický register v 10-disciplinary.md**

| BEFORE | AFTER |
|---|---|
| `By the mere fact of entering a fencing competition, the fencers pledge their honour to observe the Rules, and the decisions and instructions of the officials, to be respectful towards the Referees (Referee and Assistant) and to scrupulously obey their orders and injunctions.` | `By entering a fencing competition, fencers agree to observe the Rules and the decisions and instructions of the officials, to be respectful towards the Referees (Referee and Assistant), and to follow their orders.` |
| `By accepting a position as referee or assistant, the person so designated pledges his/her honour to respect the rules` | `By accepting a position as Referee or Assistant, the person so designated agrees to respect the rules` |
| `All bouts must preserve the character of a courteous and frank encounter.` | `All bouts must remain courteous and fair.` |
| `In no circumstances can the imposition of this penalty give cause for redress to anyone.` | `The imposition of this penalty gives no one a right to compensation.` |

- [ ] **Krok 3: Pasíva zakrývajúce aktéra (02-equipment.md)** — BEFORE: `The mandatory equipment is controlled by the designated tournament staff before the competition and an additional check must be done by the referee of each fencing arena.` AFTER: `The designated tournament staff inspect the mandatory equipment before the competition; the referee of each fencing arena performs an additional check.` (Pozn.: `controlled` je kalk — správne `inspected`.)

- [ ] **Krok 4: Verifikácia**

```bash
grep -rn "he/she\|she/he\|his/her\|him/her\|him/them\|His/her" 0*.md 10-disciplinary.md   # očakávané: 0
grep -rnE '\b(he|she|his|her|him)\b' 0*.md 10-disciplinary.md   # posúď ručne — cieľ: žiadne rodové zámená v texte pravidiel
grep -n "injunctions\|frank encounter\|redress\|pledge" 10-disciplinary.md               # očakávané: 0
```

- [ ] **Krok 5: Commit** — `git commit -am "style: singular they, role nouns instead of pronouns, plain register in disciplinary chapter"`

---

### Úloha 7: Terminologická kanonizácia + glosár + check skript

**Files:**
- Modify: všetky kapitoly, `appendices/01-glossary.md`
- Create: `scripts/check_conventions.sh`

- [ ] **Krok 1: Hromadné náhrady kanonických termínov** (grep → cielené úpravy; `sed -i` len ak si istý kontextom):

| Kanonický termín | Nahrádza | Poznámky/výnimky |
|---|---|---|
| `fencer` | `competitor`, `contestant`, `athlete` | `participant` nechaj pre širší okruh osôb (diváci, tréneri); v 10-disciplinary premenuj sekciu `## The Competitors` → `## The Fencers`; „non-competitors" v texte o vylúčení → `non-fencers` alebo preformuluj `other persons present` |
| `bout` | `match`, `fight` (podstatné mená) | `the match can be stopped` → `the bout`; `a break in the fight` → `a break in the bout`; pozor: „matches" v `10-disciplinary.md` score-sheet vete → `bout` |
| `priority` | `right of way`, `right-of-way`, `Vor`, `right of initiative` v bežnom texte | Prvý výskyt v každej kapitole: `priority (right of way, historically *Vor*)`; nadpis v `05-longsword.md` `## Vor/Priority` → `## Priority`; názov kapitoly 04 a jej H1 nechaj `Right of Way and Priority Rules` (vžitý názov), ale v texte kapitoly používaj `priority` |
| `point` (bod v skóre) | `hit` tam, kde ide o skóre | `reaches 5 points` zostáva; `has scored 5 hits`/`7 hits` v 09-organisational → `5 points`/`7 points`; `penalty hit` v 10-disciplinary → `penalty point`; FYZICKÝ zásah zostáva `hit` (definície zásahov, valid hit…); indexy `HS – HR` nechaj, ale rozpíš `(points scored – points received)` |
| `arena` | `fencing area` | V 09-organisational a v tabuľke trestov; `fencing area staff` → `arena staff`; ak `fencing area` označuje širší priestor než arénu, ponechaj a over kontext |
| `on-guard line` | `start-line`, `starting line`, `on guard line` | `02-equipment.md` bod 4 a `03-general.md` |
| `Assistant Referee` | `Assistant (side Referee)`, `Side Referee` | Nadpis `### Side Referee (Assistant Referee)` → `### Assistant Referee`; prvá zmienka: `an Assistant Referee (observing from a different angle)` |
| `Organising Team` | `Organizing Team`, `organizer(s)`, `organisers` | Britský pravopis všade; `The organisers of a competition publish` → `The Organising Team publishes` |
| `Head of the Refereeing Team` | `Head of the Refereeing Committee`, `Refereeing committee` | `The Refereeing committee can be approached` → `The Head of the Refereeing Team can be approached` |
| `cross-guard` | `crossguard`, `cross/guard` | vrátane tabuľky trestov (1.5) |
| `stop-hit` | `stop hit` | glosár má kanonické heslo `*Stop-hit*`, ale v hesle *Counter-time* oprav `stop hit` → `stop-hit` (a `his opponent` → `the opponent`) |
| `Referee` (veľké R) | `referee` v texte pravidiel | Len tam, kde ide o rolu v tomto rulebooku; `referee` ako všeobecné slovo v úvode môže zostať malé — rozhodni jednotne: v kapitolách 02–10 vždy veľké `Referee`, `Timekeeper`, `Assistant Referee` |
| `off-target` / `forbidden target` | `non-scoring target`, `illegal target`, `non-valid target` | `07-sabre.md`: `legs being a non-scoring target` → `legs being off-target`; `strikes to an illegal target` → `strikes to a forbidden target`; `03-general.md` `covering a valid target with a non-valid one` → `covering a valid target with an off-target part` — POZOR: over význam každého výskytu (off-target = neskóruje; forbidden = trestá sa) |

- [ ] **Krok 2: Glosár — nové heslá a opravy.** V `appendices/01-glossary.md`:

(a) Oprav `Bout`: `the whole fight between two fencers` → `the whole contest between two fencers`.
(b) Otoč `Langort`: `*Langort* (point in line) – a specific position…` → `*Point in line* (*Langort*) – a specific position…`.
(c) Do sekcie **General terms** doplň:

```markdown
8. *Priority* (right of way; historically *Vor*) – the convention that
   determines which fencer's hit scores when both fencers are hit within one
   period of fencing time. Used in the Longsword and Sabre categories (see
   [Right of Way and Priority Rules](../04-right-of-way.md)).
9. *Simultaneous hit* – both fencers are hit as the result of a similar
   conception and execution of an action at the same time.
10. *Double hit* – both fencers are hit within one period of fencing time,
    without the actions being simultaneous.
11. *After-action* – a counter action (or the finishing move of a compound
    action) started at or after the moment of receiving a hit. After-actions
    never score and do not annul the hit received.
12. *Off-target* – a part of the body that does not score when hit and does not
    stop the exchange (e.g. the legs in the Sabre category).
13. *Forbidden target* – the back of the head, the spine, the groin, the feet
    and the back of the knees. Hitting a forbidden target is penalised (see
    penalty 1.5).
14. *Arena* (fencing arena) – the marked area in which bouts take place.
15. *On-guard line* – the marked line on which each fencer takes the on-guard
    position, at least 2 m from the centre of the arena.
```

(d) `03-general.md`: definíciu fencing time („Fencing time is the time required to perform one simple fencing action.") nahraď odkazom: `*Fencing time* (see [Glossary](appendices/01-glossary.md)) is counted as follows: in judging hits, referees count immediate actions that start up to the moment of the first hit as relevant actions.`

- [ ] **Krok 3: Vytvor scripts/check_conventions.sh**

```bash
#!/bin/bash
# Konvenčné kontroly rulebooku. Exit 0 = OK. Kontroluje kapitoly a appendices,
# nie docs/ ani slovenské súbory.
set -u
FILES="01-intro.md 02-equipment.md 03-general.md 04-right-of-way.md \
05-longsword.md 06-rapier.md 07-sabre.md 08-sword-and-buckler.md \
09-organisational.md 10-disciplinary.md README.md appendices/01-glossary.md"
fail=0
check_zero() {  # $1 = popis, $2 = pattern
  hits=$(grep -nE "$2" $FILES 2>/dev/null)
  if [ -n "$hits" ]; then echo "FAIL: $1"; echo "$hits"; fail=1; fi
}
check_zero "zakázané modálne tvary"        '\bshall\b|is going to'
check_zero "nekanonické osoby"              '\bcontestants?\b|\bcompetitors?\b|\bathletes?\b'
check_zero "nekanonický súboj"              '\bthe match\b|\bthe fight\b'
check_zero "rodové zámená"                  'he/she|she/he|his/her|him/her|him/them'
check_zero "nekanonická priorita"           'right of initiative'
check_zero "nekanonická čiara"              'start-line|\bstarting line\b'
check_zero "nekanonický asistent"           'Side Referee'
check_zero "americký pravopis organizácie"  'Organizing Team|organizer'
check_zero "nekanonický cross-guard"        '\bcrossguard\b|cross/guard'
check_zero "nekanonický stop hit"           '\bstop hit\b'
check_zero "rozbité FIE odkazy"             'Article [0-9]|in Article\.|Figure 2'
check_zero "staré HTML atribúty"            'bgcolor'
exit $fail
```

```bash
chmod +x scripts/check_conventions.sh
```

> **Poznámka:** `appendices/02-penalties.md` zámerne vo FILES nie je — starý HTML súbor obsahuje `he/she`, `competitor` aj `bgcolor`; do FILES ho vráti Úloha 9 po prepise. Kontrola `Article [0-9]` začne prechádzať až po Úlohe 8 — dovtedy je to jediné akceptované zlyhanie (všetko ostatné musí prejsť už teraz).

- [ ] **Krok 4: Verifikácia**

```bash
scripts/check_conventions.sh   # očakávané: FAIL len na "rozbité FIE odkazy" (opraví Úloha 8)
scripts/check_links.sh         # exit 0
```

- [ ] **Krok 5: Commit** — `git commit -am "style: canonical terminology, glossary entries for core scoring terms, convention check script"`

---

### Úloha 8: Globálne číslovanie článkov + krížové odkazy + FIE pozostatky

**Files:**
- Modify: `02-equipment.md`, `03-general.md`, `04-right-of-way.md`, `05-longsword.md`, `06-rapier.md`, `07-sabre.md`, `08-sword-and-buckler.md`, `09-organisational.md`, `10-disciplinary.md`, `01-intro.md` (bod 4 Use of Language)

**Interfaces:**
- Produces: stabilné ID článkov `<PREFIX>.<n>`, ktoré používa Úloha 9 (stĺpec ART.) a Úloha 11 (quick-reference). Po dokončení vygeneruj zoznam ID: `grep -hoE '\*\*[A-Za-z]+\.[0-9]+\*\*' *.md | sort -u > /tmp/article-ids.txt`.

- [ ] **Krok 1: Prefixy a postup číslovania.**

| Súbor | Prefix |
|---|---|
| `02-equipment.md` | `E` |
| `03-general.md` | `G` |
| `04-right-of-way.md` | `RoW` |
| `05-longsword.md` | `LS` |
| `06-rapier.md` | `R` |
| `07-sabre.md` | `S` |
| `08-sword-and-buckler.md` | `SB` |
| `09-organisational.md` | `O` |
| `10-disciplinary.md` | `D` |

`01-intro.md` a glosár sa nečíslujú (filozofia a definície sa citujú menom).

Postup pre každý súbor: prechádzaj zhora nadol; každú položku číslovaného zoznamu, ktorá je pravidlom, preveď na odsek začínajúci `**<PREFIX>.<n>**` s priebežným `n` cez celý súbor (žiadny reštart na sekciách). Vnorené pod-body preveď na `a)`, `b)`, `c)`… Úvodné nečíslované odseky sekcií (napr. úvod „Rapier and side weapons do not use priority…") nechaj bez ID — normu z nich presuň do prvého očíslovaného pravidla, ak ju obsahujú (v 06-rapier: veta `only the first valid hit scores` patrí do R.4, úvod nechaj informatívny).

Vzor (03-general, začiatok):

```markdown
## The Process of the Bouts

### Starting the bout

**G.1** Each bout is performed for a set amount of time or until a set amount
of points. This is achieved through a series of separate, independent
exchanges.

**G.2** The fencers present themselves in the arena when called by the Referee
before each pool or direct elimination bout, in appropriate gear conforming to
the rules, ready to fence.
```

- [ ] **Krok 2: Skontroluj markdown rendering.** Odseky `**G.1** …` nesmú byť súčasťou `1.` zoznamov (odstráň pôvodné čísla zoznamu). Pod-body píš **záväzne** ako markdown zoznam s pomlčkou: `- a) …`, `- b) …` — samostatný blok odsadený 4 medzerami by python-markdown vykreslil ako code block (sivý monospace rámik v PDF). Vygeneruj PDF po očíslovaní prvej kapitoly a over rendering skôr, než očísluješ zvyšok.

- [ ] **Krok 3: Preveď prozaické krížové odkazy na presné.** Zoznam konverzií (po pridelení čísel doplň skutočné `n`):

| Miesto | Teraz | Nahradiť |
|---|---|---|
| `03-general.md` + `09-organisational.md` | odkaz `[Technical & Equipment Standards](02-equipment.md)` vložený Úlohou 3 (pôvodné `(see the Equipment Standards)` už neexistuje) | doplň číslo článku o kontrole výstroja: `…are set out in the [Technical & Equipment Standards](02-equipment.md), E.<n>.` |
| `02-equipment.md` | `a break of up to 3 minutes may be allowed (see the General Rules).` | `…(see [G.<n>](03-general.md) — equipment failure breaks).` |
| `03-general.md` (dedup z Úlohy 3) | odkaz na Organisational Rules | doplň `, O.<n>–O.<n>` |
| `06-rapier.md` | `the regulations for these side weapons are set out elsewhere in this Rulebook.` | `the regulations for these side weapons are set out in the [Technical & Equipment Standards](02-equipment.md), E.<n>–E.<n> (dagger) and E.<n>–E.<n> (cloak).` |
| `09-organisational.md` | `(See Figure 2.)` | zmaž — žiadna Figure 2 neexistuje |
| `10-disciplinary.md` | `the same as those described in the Article 29. above` | `the same as those described in D.<n> (Exclusion) above` (odkaz na článok „Exclusion. A fencer who, while fencing…" — znenie po sweepe Úlohy 7) |
| `10-disciplinary.md` | `to be applied in the cases indicated in the table in Article.` | `to be applied in the cases indicated in the [Table of Offences and Penalties](appendices/02-penalties.md).` |
| `10-disciplinary.md` | `are summarised in the table that follows in Article 44.); they are divided` | `are summarised in the [Table of Offences and Penalties](appendices/02-penalties.md); they are divided` |
| `10-disciplinary.md` | `(see the table of offences, also attached to this summary)` | `(see the [Table of Offences and Penalties](appendices/02-penalties.md))` |
| `05-longsword.md` | `(see the General Rules, 'The methods of scoring hits')` | `(see [G.<n>](03-general.md) — pommel strike)` |
| `07-sabre.md` | `the general dominance rule (see [General Rules](03-general.md))` | `the general dominance rule (see [G.<n>–G.<n>](03-general.md))` |

Existujúce odkazy `(see penalty 0.3)`, `(see penalty 1.5)`, `(see penalty 1.6)` atď. nechaj — tabuľka trestov si drží vlastné číslovanie 0.1–4.5.

- [ ] **Krok 4: Doplň do 01-intro.md „Use of Language" bod 4**

```markdown
4. Rules are numbered with a chapter prefix: E = Equipment, G = General rules,
   RoW = Right of Way, LS = Longsword, R = Rapier, S = Sabre, SB = Sword &
   Buckler, O = Organisational, D = Disciplinary. Cite rules by these
   identifiers (e.g. "G.16", "RoW.12(a)"). Identifiers are stable: new rules
   receive new numbers and existing numbers are not reused.
```

- [ ] **Krok 5: Verifikácia**

```bash
grep -c '^\*\*E\.' 02-equipment.md      # > 60 (odhad ~80 článkov)
grep -c '^\*\*G\.' 03-general.md        # > 40
grep -rn "Article [0-9]\|in Article\.\|Figure 2" *.md    # 0 riadkov
scripts/check_links.sh && scripts/check_conventions.sh   # očakávané: exit 0 (02-penalties.md pribudne do kontrol až v Úlohe 9)
# každé ID unikátne:
grep -hoE '\*\*[A-Za-z]+\.[0-9]+\*\*' *.md | sort | uniq -d    # 0 riadkov
source venv/bin/activate && python generate_pdf.py             # PDF sa vygeneruje, skontroluj rendering G.1 odsekov
```

- [ ] **Krok 6: Commit** — `git commit -am "feat: global article numbering with chapter prefixes, precise cross-references, remove broken FIE references"`

---

### Úloha 9: Tabuľka trestov → čisté Markdown + ART. stĺpec + farby kariet v PDF

**Files:**
- Modify: `appendices/02-penalties.md` (kompletný prepis), `generate_pdf.py` (colorize + CSS)

**Interfaces:**
- Consumes: ID článkov z Úlohy 8 (`/tmp/article-ids.txt` alebo grep).
- Produces: markdown tabuľky; `colorize_cards()` v generate_pdf.py.

- [ ] **Krok 1: Prepíš appendices/02-penalties.md.** Nahraď **všetkých 7 HTML tabuliek** (Non-presentation, Boundary crossing, skupiny 1–4 a záverečná EXPLANATIONS, ktorú nahrádza sekcia „Cards and footnotes") markdown tabuľkami. Predloha (ART. hodnoty `<…>` doplň podľa pridelených ID; kde pravidlo v texte neexistuje, daj `—`):

```markdown
# Table of Offences and Penalties

This table is a summary; it is not a substitute for the full text of the
articles concerned (ART. column), which must be consulted in any case of doubt.

An asterisk (*) means: any hit scored by the fencer at fault is annulled.

## Non-presentation

| No. | Offence | Art. | Penalty |
|-----|---------|------|---------|
| 0.1 | Non-presentation when called by the staff of the arena ten minutes before the time indicated for the start of pool / direct elimination bouts | O.<n> | **BLACK** — elimination from the competition |
| 0.2 | Non-presentation on the arena ready to fence when ordered by the Referee (three calls, one-minute intervals) | D.<n> | 1st call **YELLOW** · 2nd call **RED** · 3rd call elimination |

## Boundary crossing

| No. | Offence | Art. | 1st occasion | Subsequent |
|-----|---------|------|--------------|------------|
| 0.3 | Leaving the arena with both feet without the opponent's interaction and without having scored a valid hit | G.<n> | Verbal warning | Point against |

## First group

Penalty ladder: 1st offence **YELLOW**, 2nd and subsequent offences **RED**.
A fencer already holding a RED card receives a further **RED** for a first
offence of this group.

| No. | Offence | Art. |
|-----|---------|------|
| 1.1 | Leaving the arena without permission | — |
| 1.2 | Turning the back on the opponent | G.<n> |
| 1.3 | Covering/substitution of valid target | G.<n> |
| 1.4 | Interruption of the bout without valid reason | G.<n> |
| 1.5 | Attacking forbidden targets (back of the head, spine, groin, foot, back of the knee). Hit with the cross-guard. Attack with the dagger in Rapier. Strike with the buckler. Wrestling or grappling in Rapier, Sword & Buckler, or Sabre. | G.<n>, R.<n>, SB.<n>, S.<n> |
| 1.6 | Clothing/equipment nonconforming; absence of regulation weapon | E.<n> |
| 1.7 | Hitting the arena floor with an uncontrolled action | G.<n> |
| 1.8 | Refusal to obey the Referee (including actions before 'Fence!' or after 'Halt!') | G.<n> |
| 1.9 | Disorderly fencing *; taking off the mask before the Referee calls 'Halt!'; dressing or undressing in the arena | D.<n> |
| 1.10 | Irregular movements in the arena *; throwing the opponent by lifting both of their feet off the ground * | D.<n>, G.<n> |
| 1.11 | Unjustified appeal | D.<n> |
| 1.12 | Hitting with the fists, kicking * | G.<n> |
| 1.13 | Removing the opponent's mask or any other protective equipment * | — |
| 1.14 | Losing or dropping the cloak during a Rapier bout | R.<n> |

## Second group

Penalty: **RED** for every offence, including the first.

| No. | Offence | Art. |
|-----|---------|------|
| 2.1 | Throwing the weapon * | G.<n> |
| 2.2 | Demanding a break for a claimed injury/cramp not confirmed by the medical staff | G.<n> |
| 2.3 | Absence of equipment control marks * | O.<n> |
| 2.4 | Dangerous, violent or vindictive action *; attack with the dagger in Rapier bouts *; strike with the buckler * | D.<n>, R.<n>, SB.<n> |

## Third group

| No. | Offence | Art. | 1st offence | 2nd offence |
|-----|---------|------|-------------|-------------|
| 3.1 | Fencer disturbing order when in the arena (in the most serious cases the Referee may award a black card immediately) | D.<n> | **RED**⁴ (even if already holding a RED from groups 1 or 2) | **BLACK**¹ |
| 3.2 | Dishonest fencing * | D.<n> | **RED** | **BLACK**¹ |
| 3.3 | Any person not in the arena disturbing order (in the most serious cases: immediate black card) | D.<n> | **YELLOW**⁴ (valid for the whole competition) | **BLACK**³ |
| 3.4 | Offence against sportsmanship * (in the most serious cases: immediate black card) | D.<n> | **YELLOW** | **BLACK**¹ or ² |

## Fourth group

Penalty: **BLACK** for the first offence.

| No. | Offence | Art. |
|-----|---------|------|
| 4.1 | Deliberate brutality; throwing the opponent onto their head *; neck-wrenching and small-joint manipulation *; failing to stop dangerous submission holds before full application (both fencers may be penalised, the victim as well if they did not submit) *; throwing the dagger at the opponent in Rapier bouts * | G.<n>, R.<n> |
| 4.2 | Causing injury or threat of injury with equipment non-conforming to the Rules, or with imitated/transferred weapon control marks | E.<n> |
| 4.3 | Offence against sportsmanship (e.g. refusal to salute or shake hands after the bout) | G.<n>, D.<n> |
| 4.4 | Refusal of a fencer to fence another fencer properly entered | D.<n> |
| 4.5 | Profiting from collusion, favouring an opponent | D.<n> |

## Cards and footnotes

| Card | Meaning |
|------|---------|
| **YELLOW** | Warning, valid for the bout. A fencer who commits a 1st-group offence after having been penalised with a RED card (for whatever reason) receives a further **RED**. |
| **RED** | Penalty point for the opponent. |
| **BLACK** | Exclusion from the competition and suspension from the remainder of the tournament; possible suspension from future events organised by the Federation or the Organiser. In the 3rd group, a BLACK card is awarded only after a previous offence in that group (demonstrated by a RED card). |

¹ exclusion from the competition · ² exclusion from the tournament ·
³ expulsion from the venue · ⁴ in serious cases the Referee may exclude/expel
immediately
```

Mapovanie ART. (pravidlá identifikuj podľa obsahu): 0.1 → O (tri výzvy 10 min pred štartom); 0.2 → D (tri výzvy rozhodcu, sekcia The Fencers); 0.3 → G (hranica bez zásahu); 1.2, 1.3 → G (Forbidden actions: turning/covering); 1.4 → G (prestávka len cez rozhodcu); 1.5 → G (forbidden targets + cross-guard) + R (útok dýkou) + SB (úder bucklerom) + S (zákaz grapplingu); 1.6 → E (kontrola výstroja); 1.7 → G (arena floor); 1.8 → G (akcie pred/po povele); 1.9 → D (Etiquette: disorderly; The Fencers: maska); 1.10 → D (Etiquette) + G (CQC forbidden); 1.11 → D (Referee: appeals); 1.12 → G (punching/kicking); 1.14 → R (cloak, bod 5); 2.1 → G (throwing weapon); 2.2 → G (injury break); 2.3 → O (Tournament Staff: stamps); 2.4 → D (Etiquette) + R + SB; 3.1 → D (Order 2); 3.2 → D (utmost ability); 3.3 → D (3rd group osoby mimo arény); 3.4 → D (Etiquette); 4.1 → G (CQC forbidden) + R (hod dýkou); 4.2 → E (zodpovednosť za výstroj); 4.3 → G (salute) + D (Etiquette 2); 4.4 → D (refusal to fence); 4.5 → D (collusion). Pre 1.1 a 1.13 v texte pravidiel niet kotvy → `—` (kandidáti na doplnenie textu pravidla, zaznamenaj do CHANGELOG poznámky v Úlohe 12).

- [ ] **Krok 2: Farby kariet v PDF.** Do `generate_pdf.py` pridaj metódu a volanie na konci `convert_markdown_to_html` (pred `return html_content`):

```python
    def colorize_cards(self, html: str) -> str:
        """Zafarbí YELLOW/RED/BLACK karty v tabuľkách trestov."""
        html = html.replace('<strong>YELLOW</strong>', '<strong class="card-yellow">YELLOW</strong>')
        html = html.replace('<strong>RED</strong>', '<strong class="card-red">RED</strong>')
        html = html.replace('<strong>BLACK</strong>', '<strong class="card-black">BLACK</strong>')
        return html
```

```python
        html_content = self.colorize_cards(html_content)
        return html_content
```

Do `css_styles` pridaj:

```css
            .card-yellow { background-color: #E3D059; padding: 0 4px; }
            .card-red    { background-color: #E36159; color: #fff; padding: 0 4px; }
            .card-black  { background-color: #787878; color: #fff; padding: 0 4px; }
```

- [ ] **Krok 3: Vráť tabuľku trestov do konvenčných kontrol.** V `scripts/check_conventions.sh` doplň `appendices/02-penalties.md` na koniec zoznamu FILES.

- [ ] **Krok 4: Verifikácia**

```bash
grep -c "<table>\|bgcolor\|<td" appendices/02-penalties.md    # očakávané: 0
scripts/check_conventions.sh                                   # očakávané: exit 0 (všetko prechádza, vrátane 02-penalties.md)
source venv/bin/activate && python generate_pdf.py             # over v PDF: farebné karty, tabuľky sa zmestia na stranu
```

- [ ] **Krok 5: Commit** — `git commit -am "refactor(penalties): pure markdown tables with filled ART. column and card colours in PDF"`

---

### Úloha 10: Súhrnné tabuľky — parametre bojov, parametre zbraní, checklist výstroja

**Files:**
- Modify: `09-organisational.md`, `02-equipment.md`

- [ ] **Krok 1: Tabuľka parametrov bojov.** Do `09-organisational.md`, na začiatok sekcie „Organisation of the competitions and classification" (hneď za úvodný odsek o defaultoch), vlož:

```markdown
| Phase | Fencing time | Point limit | Rest | If tied at end of time |
|-------|--------------|-------------|------|------------------------|
| Pool bout | 2 min | 5 | — | 1 min sudden death; lot decides if still tied |
| Direct elimination | 2 × 2 min | 7 | 1 min between periods | 1 min sudden death; lot decides if still tied |
| Medal bouts (gold, bronze) | per schedule | may be raised (e.g. 10 or 15) | per schedule | as direct elimination |

> **Note:** These are the default values; the Organising Team may announce
> different values before the start of the competition (see the articles
> below).
```

- [ ] **Krok 2: Tabuľka parametrov zbraní.** Do `02-equipment.md` na začiatok sekcie `### Weapons` vlož:

```markdown
| Parameter | Longsword | One-handed sword | Rapier | Dagger | Sabre |
|---|---|---|---|---|---|
| Overall length | 120–140 cm | 70–100 cm | ≤ 130 cm | ≤ 60 cm | ≤ 105 cm |
| Blade length | — | — | ≤ 110 cm (incl. *ricasso*) | ≤ 45 cm | ≤ 90 cm |
| Weight | 1400–1700 g (men), 1250–1600 g (women) | 900–1200 g | 900–1300 g | not specified | 650–800 g |
| Flexibility | 9–16 kg | not specified | ≤ 10 kg | not specified | ≤ 10 kg |
| Minimum point area | 70 mm² | 50 mm² | 50 mm² | blunt + rounded/secured | 50 mm² |
| Point of balance | ≤ 9 cm from cross-guard | ≤ 9 cm from cross-guard | — | — | — |

> **Note:** This table is a summary of the detailed requirements below, which
> prevail in case of doubt. Buckler: circular, diameter ≤ 40 cm, wooden or
> metallic, no studs or sharp edges.
```

(Postup merania flexibility bol zjednotený už v Úlohe 3, Krok 4 — tu len over, že hodnoty v tabuľke sedia s limitmi v texte. Nový článok sa v tejto úlohe do 02-equipment.md **nepridáva**, aby zostali E-čísla z Úlohy 8 stabilné; tabuľky sú informatívne a ID nemajú.)

- [ ] **Krok 3: Checklist výstroj × zbraň.** Na koniec `02-equipment.md` (za sekciu Weapons) pridaj:

```markdown
## Equipment checklist by weapon category

| Equipment | Longsword | Rapier | Sabre | Sword & Buckler |
|---|---|---|---|---|
| FIE mask (CE level 2, 1600 N), undamaged | required | required | required | required |
| Back-of-head + cervical spine protection | required | required | required | required |
| Throat/larynx protector | required | required | required | required |
| HEMA fencing gloves | required | not required with a sufficiently closed hilt (E.<n>) | not required with a sufficiently closed hilt (E.<n>) | required |
| Additional wrist/forearm protection | — | required when fencing without a massive glove | required when fencing without a massive glove | — |
| Rigid wrist guard | required | — | required | required |
| Fencing jacket/gambeson ≥ 350 N, covering armpits | required | required | required | required |
| Under-plastron 800 N (FIE) | — | required | — | — |
| Breast/chest protection (women) | required | required | required | required |
| Groin protector (men) | required | required | required | required |
| Knee + shin protection (front and sides) | required | required | required | required |
| Thigh protection ≥ 350 N (CE level 1) | required | required | required | required |
| Hip protection (jacket or padded trousers) | required | required | required | required |
| Side-weapon hand: glove with additional protection | — | required if a side weapon is used | — | — |

> **Note:** Summary only — the detailed articles above prevail. `required`
> means mandatory for entering the category.
```

(`E.<n>` doplň podľa ID pravidla o bell guard/basket z Úlohy 8.)

- [ ] **Krok 4: Verifikácia**

```bash
grep -c '^| Parameter' 02-equipment.md                               # očakávané: 1 (tabuľka parametrov zbraní)
grep -c '^## Equipment checklist by weapon category' 02-equipment.md # očakávané: 1
scripts/check_links.sh && scripts/check_conventions.sh
source venv/bin/activate && python generate_pdf.py                   # tabuľky sa zmestia na A4 (font 10pt, over vizuálne)
```

- [ ] **Krok 5: Commit** — `git commit -am "feat: summary tables for bout parameters, weapon parameters and equipment checklist"`

---

### Úloha 11: Príklady, Note konvencia, prehľad zbraní a quick-reference

**Files:**
- Modify: `03-general.md`, `04-right-of-way.md`, `05-longsword.md`, `appendices/01-glossary.md`, `README.md`
- Create: `appendices/03-weapon-overview.md`, `appendices/04-referee-quick-reference.md`

- [ ] **Krok 1: Note konvencia pre existujúce vysvetlivky.** Presuň do blockquote `> **Note:** …`:
  - `05-longsword.md`: `(The fault of the attacker consists of indecision, slowness of execution or the making of feints which are not sufficiently effective. The fault of the defender lies in delay or slowness in making the stop-hit.)` (znenie po sweepe Úlohy 7 — `stop-hit` už so spojovníkom) → `> **Note:** The fault of the attacker typically consists of indecision, slow execution, or insufficiently effective feints; the fault of the defender lies in a delayed or slow stop-hit.`
  - `03-general.md` (CQC, pád/strata zbrane): veta `…but in the spirit of sportsmanship, no intentional new attack should be initiated if the opponent has fallen or lost the weapon.` — ponechaj v pravidle (je normatívna, `should`), ale over, že po Úlohe 8 je to vlastný pod-bod, nie vsuvka.
  - `appendices/01-glossary.md`: úvodný bod 1 sekcie Fencing actions („This section of the rules defines basic fencing actions… It is stressed that this section in no way replaces a treatise on fencing…") preformátuj z položky zoznamu na `> **Note:** …` blok.

- [ ] **Krok 2: Príklady k trom taktickým situáciám (03-general.md).** Za definície simultaneous/double/after-action vlož:

```markdown
> **Example (simultaneous hit):** Both fencers decide to attack at the same
> moment and both cuts land together; neither action began meaningfully
> earlier. → Simultaneous hit, scored according to the weapon-specific rules
> (no score change in Longsword and Sabre; both fencers score in Rapier and
> Sword & Buckler).

> **Example (double hit):** Fencer A launches a correct attack. Fencer B,
> instead of parrying, counterattacks; both hits arrive within one period of
> fencing time. → Double hit, evaluated by the weapon-specific rules (in
> priority weapons the point goes to A).

> **Example (after-action):** Fencer A lands a clean valid hit. Only after
> being hit does Fencer B start a counter-cut, which also lands. → B's hit is
> an after-action: it does not score and does not annul A's point.
```

- [ ] **Krok 3: Príklady k priorite (04-right-of-way.md).** Za zoznam „The fencer who is attacked is alone counted as hit" vlož:

```markdown
> **Example:** A attacks with a straight thrust, the arm extending before the
> lunge. B counterattacks to the arm without parrying; both hits land within
> one fencing time. → A alone scores: a counterattack into a simple attack
> loses.

> **Example:** A makes a compound attack (feint, then disengage). B stop-hits,
> but the stop-hit lands only as A starts the final movement. → The stop-hit
> is not in time; A alone scores.
```

Za zoznam „The fencer who attacks is alone counted as hit" vlož:

```markdown
> **Example:** B stands with the point in line before A starts attacking. A
> attacks without deflecting B's blade and both fencers are hit. → B alone
> scores: A had to take the blade first.

> **Example:** A attacks; B parries and ripostes immediately with a simple
> direct riposte. A renews the attack (remise) and both hits land. → B alone
> scores: a remise against an immediate simple riposte loses.
```

Za sekciu „Parry and Riposte" vlož:

```markdown
> **Example:** A attacks; B parries successfully but pauses before riposting.
> A immediately renews the attack and hits while B's delayed riposte also
> lands. → A scores: the delayed riposte lost priority.
```

- [ ] **Krok 4: Vytvor appendices/03-weapon-overview.md**

```markdown
# Weapon Overview

Summary of the key differences between weapon categories. The weapon-specific
chapters prevail in case of doubt.

| | Longsword | Rapier & side weapons | Sabre | Sword & Buckler |
|---|---|---|---|---|
| Valid target | whole body incl. weapon handle, except forbidden targets | whole body except forbidden targets and the cloak | hips up (incl. arms and head); legs are off-target | whole body except forbidden targets; hits on the buckler are not valid |
| Priority (right of way) | yes ([RoW](../04-right-of-way.md)) | no — combat rules | yes ([RoW](../04-right-of-way.md)) | no — combat rules (as Rapier) |
| Simultaneous hits | no points | both score a point | no score change | both score a point |
| Double hits | priority rules decide | both score; a thrust beats a cut or slice | priority rules decide | as Rapier |
| After-actions | never score | never score | never score | never score |
| Grappling / close quarter combat | allowed | forbidden | forbidden | forbidden |
| Special rules | pommel strike to the mask scores; dominance incl. grappling | dagger and cloak defensive only; parrying with the unarmed hand allowed | hits through blade contact must retain force; point-in-line exception; dominance without grappling | buckler defensive only; striking with the buckler forbidden |

Forbidden targets in all categories: back of the head, spine, groin, feet,
back of the knees (see [Forbidden actions](../03-general.md)).
```

- [ ] **Krok 5: Vytvor appendices/04-referee-quick-reference.md**

```markdown
# Referee Quick Reference

> **Note:** Informative summary for referees. The full rules prevail.

## Commands

'On guard!' → 'Are you ready?' → 'Fence!' → … → 'Halt!'

## Stop the exchange ('Halt!') when

a valid hit lands · an invalid hit complicates further evaluation · a fencer
leaves the arena with both feet · end of time · dangerous or confused fencing ·
equipment failure · injury · a fencer requests a break (raised arm)

## Arena boundaries

- Both feet out → stop immediately; annul everything after the crossing.
- One foot out → a hit still scores if the action started before 'Halt!'.
- Both feet out without a prior valid hit (penalty 0.3): first time a verbal
  warning, then a point against.
- Pushed out accidentally by the opponent → no penalty.

## Bout parameters (defaults)

Pools: 2 min or 5 points. Direct elimination: 2 × 2 min (1 min rest) or 7
points. Tie → 1 min sudden death; before it starts, the Referee draws lots for
priority in case nobody scores.

## Breaks

Equipment failure: up to 3 min. Injury/cramp: up to 10 min (confirmed by
medical staff; once per injury per bout).

## Cards

Group 1: **YELLOW** → **RED** → **RED** · Group 2: **RED** every time ·
Group 3: **RED** → **BLACK** (3.1, 3.2) / **YELLOW** → **BLACK** (3.3, 3.4) ·
Group 4: **BLACK** immediately.
Full table: [Table of Offences and Penalties](02-penalties.md).

## Verdicts per weapon

See [Weapon Overview](03-weapon-overview.md).
```

(Do ART. odkazov quick-reference doplň konkrétne `G.<n>`/`O.<n>` ID podľa Úlohy 8, ak chceš — minimálne pri boundaries a breaks.)

- [ ] **Krok 6: Zaregistruj nové prílohy do README.md** — do sekcie Appendix doplň:

```markdown
- [Weapon Overview](appendices/03-weapon-overview.md)
- [Referee Quick Reference](appendices/04-referee-quick-reference.md)
```

- [ ] **Krok 7: Naplň sľub „examples" v 05-longsword.md** — veta `See [Right of Way and Priority Rules](04-right-of-way.md) for detailed priority conventions and examples.` teraz zodpovedá realite (04 obsahuje príklady) — nechaj; over.

- [ ] **Krok 8: Verifikácia**

```bash
grep -c "> \*\*Example" 04-right-of-way.md    # očakávané: 5
grep -c "> \*\*Example" 03-general.md         # očakávané: 3
ls appendices/                                 # 01-glossary, 02-penalties, 03-weapon-overview, 04-referee-quick-reference
scripts/check_links.sh                        # pozor na relatívne cesty ../ z appendices — musí prejsť
source venv/bin/activate && python generate_pdf.py   # nové prílohy = A3, A4 v TOC
```

- [ ] **Krok 9: Commit** — `git commit -am "feat: worked examples, Note convention, weapon overview and referee quick reference appendices"`

---

### Úloha 12: Verzia, changelog, titulná strana + finálna QA

**Files:**
- Create: `VERSION`, `CHANGELOG.md`
- Modify: `README.md`, `generate_pdf.py`

- [ ] **Krok 1: Vytvor VERSION** — obsah: `2.0.0-draft`

- [ ] **Krok 2: Vytvor CHANGELOG.md**

```markdown
# Changelog

## 2.0.0-draft (2026)

Readability refactor — no intended changes to the meaning of the rules:

- Chapters renamed to the canonical reading order; README, PDF and file
  numbering unified.
- Global article numbering with chapter prefixes (E, G, RoW, LS, R, S, SB, O,
  D); ART. column of the penalty table filled in; broken references inherited
  from the FIE rules removed.
- Normative verb convention (must/may/should) and a "Use of Language" clause.
- Terminology unified (fencer, bout, priority, point vs hit, arena, on-guard
  line, Assistant Referee, off-target vs forbidden target); new glossary
  entries.
- General rules reorganised: subsection headings, universal forbidden actions
  promoted out of the longsword-only close-quarter section, dominance rules
  restructured.
- Summary tables (bout parameters, weapon parameters, equipment checklist),
  worked examples for tactical situations and priority, weapon overview and
  referee quick-reference appendices.
- Known gaps flagged for the federation: no rule text exists for offences 1.1
  (leaving the arena without permission) and 1.13 (removing the opponent's
  mask); video-review procedure is unspecified; the sabre hip boundary and the
  rapier hilt-as-target question are open.

## 1.x

Original rulebook (see git history).
```

- [ ] **Krok 3: Verzia v README.md** — pod H1 pridaj:

```markdown
**Version 2.0.0-draft** — under review, not yet in force. See the
[Changelog](CHANGELOG.md).
```

- [ ] **Krok 4: generate_pdf.py — verzia na titulnej strane, CHANGELOG.md namiesto git logu, vylúčenie nových root súborov**

(a) V `collect_markdown_files` doplň do výnimiek `CHANGELOG.md` (filter na `FEBUS_smernica*` je tam už z Úlohy 1, Krok 5):

```python
            if file.name not in ['README.md', 'CLAUDE.md', 'CHANGELOG.md'] \
                    and not file.name.startswith('FEBUS_smernica'):
```

(b) Pridaj metódu:

```python
    def get_version(self) -> str:
        p = Path('VERSION')
        return p.read_text(encoding='utf-8').strip() if p.exists() else ''
```

(c) V `generate_pdf` v bloku titulnej strany nahraď `<div class="edition">Official Edition</div>` za:

```python
        version = self.get_version()
        edition = f'Official Edition — Version {version}' if version else 'Official Edition'
```

a v f-stringu `<div class="edition">{edition}</div>`.

(d) V `generate_changelog` uprednostni kurátorovaný changelog:

```python
    def generate_changelog(self) -> str:
        """Vygeneruje changelog: preferuje CHANGELOG.md, fallback git história."""
        changelog_md = Path('CHANGELOG.md')
        if changelog_md.exists():
            md = markdown.Markdown(extensions=['extra', 'sane_lists'])
            body = md.convert(changelog_md.read_text(encoding='utf-8'))
            return f'<div class="changelog">{body}</div>'
        # …pôvodné telo s git log ako fallback…
```

- [ ] **Krok 5: OBSAHOVÁ ZMENA — otvorené otázky pre federáciu.** Nezapracúvaj do pravidiel; vytvor `docs/open-questions.md` so zoznamom návrhov na rozhodnutie federácie (každý s navrhovaným znením):

```markdown
# Otvorené obsahové otázky (vyžadujú rozhodnutie federácie)

1. **Video review** — G-pravidlo dnes dáva právo na jeden appeal, ale chýba
   procedúra. Návrh: nový článok v Organisational Rules — o review rozhoduje
   Referee po vzhliadnutí záznamu s Assistantom; review môže zmeniť len
   posúdenie faktov poslednej výmeny; ak záznam nie je presvedčivý, pôvodný
   verdikt platí a fencer stráca ďalší appeal.
2. **Sabre — hranica bedra**: "from the hips up" nedefinuje, či zásah presne na
   bedrový kĺb platí. Návrh: "hits on the hip line count as valid".
3. **Rapier — rukoväť/koš ako cieľ**: longsword rukoväť explicitne zahŕňa,
   rapier mlčí. Návrh: doplniť do R článku o cieli "including the hilt of the
   weapon" alebo explicitne vylúčiť.
4. **Priestupky 1.1 a 1.13** nemajú kotvu v texte pravidiel — doplniť články
   (opustenie arény bez povolenia; strhnutie masky súpera) do G/D.
5. **One-handed sword** nemá v equipment kapitole limit flexibility — doplniť?
```

- [ ] **Krok 6: Finálna QA**

```bash
scripts/check_conventions.sh          # exit 0
scripts/check_links.sh                # exit 0
grep -hoE '\*\*[A-Za-z]+\.[0-9]+\*\*' *.md | sort | uniq -d   # 0 duplicitných ID
source venv/bin/activate && python generate_pdf.py
# Manuálna kontrola PDF (otvor febus_rulebook.pdf):
#  - titulná strana: "Official Edition — Version 2.0.0-draft"
#  - TOC: kapitoly 1–10 v kanonickom poradí, prílohy A1–A4
#  - tabuľka trestov: farebné karty, vyplnený stĺpec Art.
#  - kapitola General rules: G.1 … články, H3 podsekcie
#  - Change Log strana: obsah CHANGELOG.md, nie git log
```

- [ ] **Krok 7: Commit + záverečné porovnanie**

```bash
git add -A
git commit -m "feat: version, curated changelog, title page version and open content questions"
git diff master --stat    # rekapitulácia rozsahu pre PR/review
```

---

## Self-Review (vykonané pri písaní plánu)

1. **Pokrytie auditu:** všetkých 6 optík auditu má zodpovedajúce úlohy — jazyk (4, 5, 6), štruktúra/navigácia (1, 2, 3, 8), terminológia (7), formát/vizuál (9, 10, 11 + farby kariet), publiká (10, 11), best practices (5 — ISO konvencia, 8 — FIE číslovanie, 12 — verzia/changelog, 11 — Longpoint examples/quick-ref). Bug generate_pdf.py príloh — Úloha 1, Krok 5.
2. **Bez placeholderov:** všetky nové texty (Use of Language, dominancia, Forbidden actions, glosárové heslá, príklady, tabuľky, quick-reference, CHANGELOG) sú v pláne v plnom znení. Jediné odložené hodnoty sú `<n>` v ID článkov — tie vzniknú deterministicky až v Úlohe 8 a plán definuje presný postup ich pridelenia aj dosadenia.
3. **Konzistencia názvov:** názvy súborov po premenovaní (Úloha 1) sa používajú vo všetkých nasledujúcich úlohách; `scripts/check_links.sh` a `scripts/check_conventions.sh` sa vytvárajú skôr, než ich verifikácie vyžadujú; sekcia `The Fencers` (premenovaná v Úlohe 7) je zohľadnená v Úlohe 3, Krok 3.
4. **Adverzariálna verifikácia (2026-08-08):** plán prešiel kontrolou troch nezávislých recenzentov (fakty vs. repo, sémantika pravidiel, konzistencia poradia úloh). Zapracovaných 29 nálezov, o. i.: netrackovaný `10-sword-and-buckler.md` pri `git mv`; 7 (nie 6) výskytov `chapter_num - 9` v generate_pdf.py vrátane vetvy `is_first_header`; smernica zbieraná do PDF ako 11. kapitola; presun zjednotenia flexibility pred číslovanie článkov; nesplniteľné brány check_conventions (02-penalties.md vo FILES pred prepisom, `starting line` v novom glosárovom hesle); typografické úvodzovky v BEFORE citátoch; zlý kartový rebríček 3. skupiny v quick-reference; pod-body cez 4-medzerové odsadenie by renderovali ako code block.
