# /inventory-audit — Inventory Logic Auditor

Audits inventory logic **in a project's own repository** against this context: the concept nodes
in `docs/25-concepts/05-inventory-management/` and `06-warehouse-management/`, and the INV/WMS
rule families in `docs/40-contexts/`.

There is no inventory implementation in *this* repository and there will not be (ADR-0037): the
context states what is fixed outside it and names the decisions a project must make. This command
carries that distinction — it checks a project's code, and it never supplies a value the project
is supposed to choose.

## Usage
`/inventory-audit [file, feature, or repository path]`

---

Audit the inventory logic in: $ARGUMENTS

Check for:
1. **Non-negative stock** — is the physical truth guarded (you cannot ship what you do not have),
   and is the project's chosen policy for the exception — backorder, allocate, refuse — applied
   consistently? The policy is theirs; the guard's presence is not optional.
2. **Concurrent update safety** — optimistic locking or row-level locks on stock movements. Two
   concurrent picks against the same stock is the defect that hides until production load.
3. **Transaction atomicity** — multi-step movements (pick + ship) in one transaction, so a partial
   failure cannot leave stock in neither place.
4. **Lot and serial traceability** — where the goods are regulated, the *obligation* is external
   (food: EU 178/2002; SVHC: REACH, CMP-R3; pharma: GDP/GMP). Check the obligation is met and that
   the picking discipline matches it — FEFO where shelf life governs (CPT-0036), FIFO otherwise.
5. **Count tolerance defined before accuracy is reported** — "correct" is not self-evident, and an
   accuracy figure without its tolerance is not a measurement.
6. **Location validation** — bin and location codes checked against the master, not accepted raw.
7. **UOM conversion** — conversions from the factor table, never hardcoded, and the codes are the
   **UN/ECE Rec 20** spellings: `KGM`, `LTR`, `MTR`. `KG`/`L`/`M` is invented shorthand that fails
   conformance silently (SCM-R10) — this repository shipped that bug.
8. **Money as minor units, quantized only at boundaries**, ties to even (SCM-R14, ENG-R4/R5).

Output a checklist with PASS / FAIL / NEEDS REVIEW per item and line references. For anything that
turns on a threshold, a tolerance or a service level, report it as **a project decision to confirm**
rather than as a failure — and say which standard constrains the answer.
