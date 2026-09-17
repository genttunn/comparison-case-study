-- Shared seed for both spa/backend/app.db and hda/backend/app.db
-- Run this file to recreate the database from scratch on app start.
-- Passwords (plaintext for reference): alice=alice123, bob=bob123, levi=levi123

PRAGMA journal_mode=WAL;

-- ── Tables ────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS users (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    username       TEXT NOT NULL UNIQUE,
    password_hash  TEXT NOT NULL,
    role           TEXT NOT NULL CHECK(role IN ('admin', 'user')),
    email          TEXT NOT NULL,
    personal_token TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tasks (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_id     INTEGER NOT NULL REFERENCES users(id),
    title        TEXT NOT NULL,
    description  TEXT,
    status       TEXT NOT NULL DEFAULT 'open' CHECK(status IN ('open', 'in_progress', 'done')),
    priority     TEXT NOT NULL DEFAULT 'medium' CHECK(priority IN ('low', 'medium', 'high')),
    is_private   INTEGER NOT NULL DEFAULT 0 CHECK(is_private IN (0, 1)),
    secret_notes TEXT,
    created_at   TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS comments (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id    INTEGER NOT NULL REFERENCES tasks(id),
    user_id    INTEGER NOT NULL REFERENCES users(id),
    body       TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ── Users ─────────────────────────────────────────────────────────────────────

INSERT INTO users (id, username, password_hash, role, email, personal_token) VALUES
(1, 'alice', 'scrypt:32768:8:1$wBDZSeM8qcAvQ2nT$93032ce89ad2763d590e92e8d696b84ae71f2e14e08f90cf49c4dd575f377a8190cfe4e50a275edc5840e45bfcb9714cdacc0b69fee5da90317c91219566d7b8', 'admin', 'alice@example.com', 'tok_alice_8f3kQpZ2'),
(2, 'bob',   'scrypt:32768:8:1$vLHoQgXeEsCwkd8r$188def54c016aa5b12879c87e172222fa5589f96377e99bd8c15ba392209f90f15c5203b8963757ca0d8c1c5aabf740e75d9644149cf7267853af39ca89254ba', 'user',  'bob@example.com',   'tok_bob_7tRmNx91'),
(3, 'levi',  'scrypt:32768:8:1$mw4riIyVQoISvoU6$da2a3244868cfe8b4879fc9b352f620178f237c5653f17f2e506c1e65fc56a6f32ef98024810d840d761e7f282beec208a8bf3c6b8cdc4087230b66ad8107bd0', 'user',  'levi@example.com',  'tok_levi_2sKvYe44');

-- ── Tasks ─────────────────────────────────────────────────────────────────────

INSERT INTO tasks (id, owner_id, title, description, status, priority, is_private, secret_notes, created_at) VALUES
(1, 1, 'Set up CI pipeline',        'Configure GitHub Actions for lint and test.', 'done',        'high',   0, 'Uses org-level secret DEPLOY_KEY.',                    '2026-07-10 09:00:00'),
(2, 1, 'Security audit Q3',         'Review auth flows and input handling.',        'in_progress', 'high',   1, 'Potential IDOR on /tasks endpoint — do not disclose.', '2026-07-15 10:00:00'),
(3, 2, 'Write onboarding docs',     'Cover local setup and env vars.',              'open',        'medium', 0, NULL,                                                    '2026-07-20 14:00:00'),
(4, 2, 'Refactor task list view',   'Extract TaskCard into its own component.',     'open',        'low',    0, NULL,                                                    '2026-07-25 11:00:00'),
(5, 1, 'Rotate API tokens',         'Expire all personal_tokens older than 90d.',   'open',        'high',   1, 'Current prod token: tok_alice_8f3kQpZ2',               '2026-08-01 08:00:00'),
(6, 3, 'Research htmx pagination',  'Evaluate hx-boost vs manual hx-get paging.',  'open',        'medium', 0, NULL,                                                    '2026-08-05 16:00:00'),
(7, 1, 'User access review',        'Audit active sessions and token usage.',        'open',        'high',   0, 'Found 3 stale tokens not rotated since Q1.',            '2026-08-08 09:30:00'),
(8, 1, 'Rotate API keys',           'Quarterly key rotation for all external services.', 'done',        'high',   0, NULL,                                                    '2026-09-01 08:00:00');

-- ── Comments ──────────────────────────────────────────────────────────────────

INSERT INTO comments (id, task_id, user_id, body, created_at) VALUES
(1, 1, 2, 'Looks good, merged.',                          '2026-08-01 09:00:00'),
(2, 1, 1, 'Closing this one out.',                        '2026-08-01 10:30:00'),
(3, 3, 1, 'Start with the README, then env var section.', '2026-08-05 14:00:00'),
(4, 4, 3, 'I can help review the Vue component split.',   '2026-08-10 11:15:00'),
(5, 6, 2, 'hx-boost breaks on the task detail modal.',   '2026-08-12 16:45:00');
