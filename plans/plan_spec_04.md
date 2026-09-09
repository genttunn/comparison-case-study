# Plan: Spec-04 Third-Party Dependency Compromise

## Context
Static analysis page on Issue 3 tab of both apps. No live exploit. Shows the package inventory for each architecture layer (client-side and server-side), annotates what each layer exposes if compromised, and presents a side-by-side narrative. The key finding: client-side attack surface is asymmetric (SPA has a full npm graph in the browser; HDA has one vendored file); server-side attack surface is identical (both run Flask+pip with equal blast radius). No verdict — evidence only.

---

## Approach: hardcoded tables (FR7 loosened)

The SPA frontend cannot read `package.json` at runtime in the Vite dev build without a dedicated backend endpoint. HDA could read `requirements.txt` at request time, but the asymmetry creates inconsistency. Since FR7 was explicitly loosened to allow hardcoded tables, both apps will use hardcoded HTML/template rows that accurately reflect the actual `package.json` and `requirements.txt` contents. This is simpler and consistent across both apps.

---

## Page layout (both apps, same structure)

1. **Page title + subtitle**
2. **Client-side package table** — columns: Package, Source, If compromised, reaches...
   - SPA: vue, vue-router, @vitejs/plugin-vue (build-time), vite (build-time)
   - HDA: htmx.min.js (vendored)
   - Blast radius row below table (highlighted)
   - Note about CDN scripts in production
3. **Server-side package table** — columns: Package, Source, If compromised, reaches...
   - SPA server: apiflask, PyJWT, werkzeug, flask-cors, python-dotenv
   - HDA server: flask, flask-session, werkzeug, python-dotenv
   - Blast radius row below table (same text for both: full DB, all sessions, SECRET_KEY)
4. **Narrative comparison block** — side-by-side bullet lists, no verdict
   - Left: SPA attack surface summary
   - Right: HDA attack surface summary
   - Real-world incidents: event-stream (2018), ua-parser-js (2021), Polyfill.io (2024)
5. **Repro block** — "Notes" — explains the asymmetry in plain language

---

## Files to modify

### `spa/frontend/src/views/Issue3ThirdPartyView.vue`
Full replacement of placeholder. Pure `<template>` — no `<script setup>` needed (no data fetching, no interactivity). Static HTML tables and narrative text. Follow the card/repro-block CSS pattern from Issue1XssView.vue.

### `hda/backend/templates/issue_3_third_party.html`
Full replacement of placeholder. Extends `base.html`, `{% set active = "issue-3" %}`. Same layout as Vue component but Jinja2 template. Pass `username=session.get("username")` from route (already done in existing stub route).

### `hda/backend/app.py`
No changes needed — `issue_3_third_party()` route already exists and passes `username`. Confirmed at line 196–197.

### `spa/backend/app.py`
No changes needed — no new routes or data required.

---

## Narrative content (both pages carry the same text)

**SPA client surface:**
- 4 npm packages run in (or inject into) the browser
- vue, vue-router: full DOM access, component state, all reactive data
- vite, @vitejs/plugin-vue: build-time — malicious code injected here lands silently in the browser bundle
- A compromised package can read `localStorage` (JWT), intercept fetch calls, exfiltrate credentials
- JWT is portable: stolen token works from any machine until expiry

**HDA client surface:**
- 1 vendored file (htmx.min.js), no transitive dependencies, no npm graph
- A compromise reaches: DOM content, credentialed fetch calls (session riding)
- No credential in storage — nothing portable to exfiltrate
- Attack window closes when tab closes

**Both server surfaces (equal):**
- Full database (users, tasks, comments, password hashes, secret_notes)
- All active sessions
- SECRET_KEY / JWT signing key
- Filesystem

**Real-world incidents:** event-stream (2018) — malicious code in transitive npm dep; ua-parser-js (2021) — hijacked npm package with crypto miner; Polyfill.io (2024) — CDN domain sold, served malicious JS to 100k+ sites.

---

## Verification (AC mapping)
- AC1: SPA Issue 3 page shows client package table with blast radius
- AC2: HDA Issue 3 page shows client package table with blast radius
- AC3: Both pages show server package table
- AC4: Both pages include side-by-side narrative bullets (no verdict)
- AC5: No payload on either page
- AC6: Real-world incidents cited
