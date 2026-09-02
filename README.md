# SPA vs HDA: A Client-Side Security Case Study

A prototype comparing two web application architectures — **Single Page Application (SPA)** and **Hypermedia-Driven Application (HDA)** — from a client-side security perspective.

The prototype demonstrates five common client-side security issues side-by-side, showing how each architecture behaves when facing the same exploit. The focus is architectural differences, not production hardening.

## Security issues covered

| # | Issue |
|---|-------|
| 1 | XSS — injected attacker script executing in victim's browser |
| 2 | Sensitive data exposure via client-side storage |
| 3 | Third-party script and dependency compromise |
| 4 | Monitoring and detection of client-side changes |
| 5 | Business logic and proprietary information exposure |

## Architecture

**SPA** — Vue 3 + Vite frontend, Flask + APIFlask backend (JSON API only, port 5001). Client holds state and routing; JWT stored in localStorage.

**HDA** — Flask + Jinja2 backend (HTML responses only, port 5002). Server drives all navigation via htmx attributes. No hand-written application JavaScript.

Both apps share a single CSS file and are seeded from the same SQL file on every start.

## File structure

```
/
├── shared/
│   ├── seed.sql          # Single source of truth for DB schema and seed data
│   └── styles.css        # Shared stylesheet (linked by both apps)
│
├── spa/
│   ├── backend/          # Flask + APIFlask, port 5001
│   │   ├── app.py
│   │   └── requirements.txt
│   └── frontend/         # Vue 3 + Vite
│       ├── src/
│       │   ├── App.vue
│       │   ├── main.js
│       │   ├── router/
│       │   └── views/
│       └── package.json
│
├── hda/
│   ├── backend/          # Flask + Jinja2, port 5002
│   │   ├── app.py
│   │   ├── requirements.txt
│   │   └── templates/
│   └── frontend/
│       └── static/
│           └── htmx.min.js
│
├── specs/                # Spec files (one per implementation step)
└── logs/                 # Prompt logs per spec
```

## Running the apps

Both apps wipe and reseed their database from `shared/seed.sql` on every start.

### SPA

```bash
# Terminal 1 — backend
cd spa/backend
pip install -r requirements.txt
python app.py
# Runs on http://localhost:5001

# Terminal 2 — frontend
cd spa/frontend
npm install
npm run dev
# Runs on http://localhost:5173
```

### HDA

```bash
cd hda/backend
pip install -r requirements.txt
python app.py
# Runs on http://localhost:5002
```

### Demo credentials

| Username | Password | Role     |
|----------|----------|----------|
| alice    | alice123 | admin    |
| bob      | bob123   | user     |
| levi     | levi123  | attacker |
