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
- PDF generator: title page now shows the rulebook version; the Change Log
  page renders this file instead of the raw git log; table-of-contents page
  numbers are now resolved from the PDF's own internal anchors (named
  destinations) rather than by matching heading text, which fixes wrong page
  numbers for headings whose title text repeats across chapters (e.g.
  "Judging of hits" in longsword, rapier and sword & buckler, or "Arena
  boundaries" in both the main body and appendix A4). Also fixed a related
  anchor bug: heading IDs used in cross-chapter links were derived from
  already smart-quoted HTML, so a heading containing an apostrophe or
  quotation mark (e.g. "Stop the exchange ('Halt!') when") produced a
  different ID than the one used to link to it, leaving that entry's page
  number blank and its link dead.
- Known gaps flagged for the federation: no rule text exists for offences 1.1
  (leaving the arena without permission) and 1.13 (removing the opponent's
  mask); offence 1.2 is only partially anchored (G.42 covers turning the head
  or covering a target, not turning the back on the opponent); offence 1.9 is
  only partially anchored (D.11/D.13 cover keeping the mask on and general
  irregular conduct, not dressing or undressing in the arena); offence 4.2 is
  only partially anchored (E.5 covers general equipment responsibility, not
  imitated or transferred weapon control marks specifically); video-review
  procedure is unspecified; the sabre hip boundary and the rapier
  hilt-as-target question are open. See `docs/open-questions.md` for the
  full list with proposed wording.

## 1.x

Original rulebook (see git history).
