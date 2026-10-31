# TechGap Handoff (as of 2026-10-24)

Entry point for any AI provider or new session. It points to the existing documents and does not repeat them. It is planning and implementation context only; it does not establish that analytics are implemented or validated.

## Reading order

Read the current contracts first, then orientation and history.

1. `docs/plan/PLANNED_DATA_FLOW.md` — current downstream contract: four tracks, evidence rules, meaning of results.
2. `docs/plan/JOBSTREET_COLLECTION.md` — collection scope, count definitions, source preservation, spending controls.
3. `PLAN.md` — latest actor evidence reconciliation handoff and route decision.
4. `docs/plan/JOB_NORMALIZATION_HANDOFF_2026-10-24.md` — first offline processing milestone; normalizing saved jobs.
5. `docs/plan/PREMODEL_DATA_PREPARATION_PLAN_2026-10-24.md` — preparing saved jobs and syllabus records for model training.
6. `docs/plan/JOBSTREET_REMAINING_COLLECTION_HANDOFF_2026-10-24.md` — completed bounded Game Development search; remaining collection decisions.
7. `docs/plan/README.md` (precedence guidance) and `docs/plan/DATA_FLOW_CHANGES.md` (change history).

Supplementary only: `JOBSTREET_BRAINSTORM_HANDOFF.md` and the browser-automation / actor research notes.

Some older documents conflict with the revised contract. Follow the precedence guidance in `docs/plan/README.md`.

## Standing rules (user decisions)

**How to work**
- Do not assume unless stated. Separate verified facts, explicit decisions, proposals, and unresolved assumptions.
- When asked to assess, stay read-only and show a proposal before modifying, deleting, copying, merging, or superseding anything.
- Make targeted corrections only; do not reformat or touch unrelated code.
- For consequential policy decisions, ask one question at a time with a concrete example and explicit options, then wait.
- The user owns product intent and major architecture. AI drafts, organizes, and finds gaps; nothing is decided until the user approves.
- Prefer the smallest working solution; avoid over-engineering.
- Do not claim implementation, accuracy, coverage, or acceptance from plans, formulas, or scores without evidence. Report implementation, commit, and live collection as separate phases.
- Prefer current source evidence over old plans, labels, or prototypes.

**Data and collection**
- Preserve every raw observation. Keep legacy artifacts as history. Do not filter raw imports through legacy admission. Do not touch raw JobStreet data unless separately authorized.
- Paid collection: start each query once, serially; reconcile before the next; stop if a check or cap fails. No optional searches or paid retries without new authorization. Earlier permission, tokens, allowances, or ceilings do not authorize a new scope.
- Never expose `APIFY_API_TOKEN` in logs, URLs, config, manifests, or chat. Do not rotate accounts to bypass pricing, limits, or terms.

**Tracks and classification**
- Four authoritative tracks: BSCS Intelligent Systems, BSCS Game Development, BSIT Network Technology, BSIT Web Development. ESCO is vocabulary and supporting evidence only, never a track label.
- Use broad title-based role grouping; do not require exact ESCO selection or pool unrelated roles. Link tracks by duties and requirements, not an extra semantic classifier.
- Reach automatic terminal decisions; no required manual labels, review queues, or CSV review. Keep unresolved or conflicting evidence instead of silently excluding it.
- Rejecting a suitable entry/junior posting costs more than accepting a borderline one; use assumed entry-level status only as a labelled last resort.
- Faculty/professor, department chair, associate dean, and dean form one Faculty/Academic Administrator group.

**Scope**
- General Education is excluded. Curriculum simulation is removed scope unless affected requirements are reconciled.
- Keep frontend, backend, API, deployment, and authentication planning separate from collection, extraction, models, and outputs.
- Requirements stay non-technical and qualitative unless a source or explicit decision gives detail. Do not invent numeric quality targets.
- Syllabus extraction: no week-by-week table; flag ambiguous PDF boundaries instead of guessing.
