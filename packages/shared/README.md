# @scm/shared

**Standards reference data only.** ISO 4217 currencies and minor units, ISO 3166-1 countries,
UN/ECE Rec 20 units of measure, Incoterms® 2020 with the four sea-only rules, and GS1 key
validation (the mod-10 check digit).

It holds **no money type** — exact monetary arithmetic is `crates/scm-money` (ENG-R4/R10,
SCM-R14) — and no status vocabulary, threshold or other policy value (ADR-0037). Imports
nothing (ENG-R1).

The unit codes are the standard's spelling, not the intuitive abbreviation: `KGM`, `LTR`, `MTR`.
`KG`/`L`/`M` were an invented shorthand that silently failed conformance.
