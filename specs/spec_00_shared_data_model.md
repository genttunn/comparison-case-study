# SPEC-<NN>: <Component Name>

## 0. Metadata
- ID: SPEC-00
- Depends on:
- Date written: 01.09.2026
- Model used for generation: claude-sonnet-4-6 - medium effort (01.09.2026)

## 1. Objective
This spec file is for setting up the data definition for the prototype.

## 2. Functional requirements
- The seed is written in `shared/seed.sql`
- There are 3 tables created with some data seeded as follows:
  - Table `users(id, username, password_hash, role, email, personal_token` :
    - Preseeded rows are: `alice`=admin, `bob`=user, `levi`=user(attacker). Passwords hashed (Werkzeug).
  - Table `tasks(id, owner_id, title, description, status, priority, is_private, secret_notes)`:
    - Preseed several task rows; a couple `is_private=1` owned by others.
  - Table `comments(id, task_id, user_id, body, created_at)`: `body` stores raw content.

## 4. Explicit prohibitions
Do not touch any other file.

## 5. Interface contract
N/A

## 6. Security issue under test
N/A

## 7. Acceptance Criteria
- 3 tables created
- Data seeded
- `shared/seed.sql` is created.

## 8. Prompt used
Read `spec_00_shared_data_model.md` for what to do, use `background.md` as context, and implement the spec. Before implementation, if there are any points unclear or require decision, pause and ask.

## 9. Deviations / Corrections
No deviation.
