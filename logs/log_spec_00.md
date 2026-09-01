User:
Read `spec_00_shared_data_model.md` for what to do, use `background.md` as context, and implement the spec. Before implementation, if there are any points unclear or require decision, pause and ask.

Claude:
One decision point before I proceed:

Password hashes — the spec says passwords are Werkzeug-hashed, but seed.sql is plain SQL with no Python runtime. I need to embed the hashes as string literals. I'll pre-generate Werkzeug-compatible pbkdf2:sha256 hashes for simple passwords (e.g. alice123, bob123, levi123) and hardcode them directly in the INSERT. These are the same hashes Werkzeug's check_password_hash will verify at runtime.

User:
What are the different approaches?

Claude:
Two approaches for getting Werkzeug hashes into a static SQL file:

1. Hardcode pre-generated hash strings — run Werkzeug once externally, copy the output hash strings into the SQL file as literals. Simple, no moving parts, but the hashes are opaque in the file and you need to know what plaintext they correspond to.
2. Plain-text passwords in SQL, hash on first app start — store passwords as plaintext in seed.sql, then have the app's DB init code hash them when it seeds. Keeps passwords readable in the file, but requires app-side seeding logic (violates the "SQL only" spirit of the spec slightly).
3. Known static Werkzeug hashes — use the well-known default hash format with a fixed salt, so the hash is deterministic and reproducible. Same as option 1 but you can re-derive the hash from the password anytime.

Recommendation: option 1. The spec says "passwords hashed (Werkzeug)" and shared/seed.sql is supposed to be the single source of truth runnable directly. I generate the hashes once now, embed them, and add a comment in the SQL noting the plaintext. Clean, self-contained, no app logic dependency.

User:
Go with option 1.

Claude:
I'll generate the Werkzeug hashes first, then write the SQL file.

  Ran 4 shell commands

Got the hashes. Now I'll check if the shared/ directory exists and create the SQL file.

  Listed 1 directory

● Write(shared\seed.sql)
Wrote 61 lines to shared\seed.sql
-- Shared seed for both spa/backend/app.db and hda/backend/app.db
-- Run this file to recreate the database from scratch on app start.
-- Passwords (plaintext for reference): alice=alice123, bob=bob123, levi=levi123

shared/seed.sql is created. A few notes on the seeding choices:

- Tasks 2 and 5 are is_private=1 and owned by alice — these will be the ones other users shouldn't see, useful for the business logic / data exposure cases later.
- secret_notes on private tasks contain plausible sensitive content (a prod token, an undisclosed vulnerability note) to make the exposure demos meaningful.
- personal_token values are realistic-looking but fake.
- levi (the attacker) owns one innocuous task and has one comment, giving him a foothold in the app without admin access.