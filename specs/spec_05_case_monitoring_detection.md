# SPEC-<NN>: <Component Name>

## 0. Metadata
- ID: SPEC-<NN>
- Depends on: SPEC-<NN>, SPEC-<NN>
- Date written:
- Model used for generation: claude-sonnet-4-6 - medium effort (<date>)

## 1. Objective
One paragraph: what this component is for and which research question / comparison axis it serves (e.g., "demonstrates how XSS surfaces differently under SPA vs HDA client-trust models").

## 2. Functional requirements
Numbered, checkable requirements. E.g.:
- FR1: Endpoint `/comments` accepts POST with `body` field.
- FR2: HDA variant returns an HTML fragment; SPA variant returns JSON.

## 4. Explicit prohibitions
What the LLM must NOT do. E.g.:
- Do not sanitize input server-side (vulnerability must be reproducible for the demo).
- Do not add any npm package beyond Vue 3 + Vite defaults.
- Do not use fetch/axios interceptors not specified here.

## 5. Interface contract
Routes, request/response shape, DB tables touched. Reference `shared/seed.sql` where relevant.

## 6. Security issue under test
The specific vulnerability class (from your 5), what "vulnerable" and "mitigated" looks like, and what the demo needs to visibly show (e.g., attacker payload → observable effect).

## 7. Acceptance Criteria
Concrete, checkable, written before prompting:
- AC1: Given payload X in comment body, script executes in victim browser (SPA) produces architectural client-side exploit.
- AC2: Same payload against HDA variant, document expected/observed outcome.

## 8. Prompt used
Verbatim prompt(s) sent to the model (this section filled after — or copy the spec itself as the prompt, noting so).

## 9. Deviations / Corrections
What you changed after generation, and why. This is your key evidence of human oversight.
