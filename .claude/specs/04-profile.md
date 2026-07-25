# Spec: Profile

## Overview
This feature implements the `GET /profile` page: a logged-in-only view that greets the user by name and displays their account details (name, email, member-since date). It replaces the placeholder string response with a real template. This is the fourth step of the roadmap, following database setup, registration, and login/logout, and is the first user-scoped page in the app — it establishes the pattern for guarding routes behind an active session that later expense routes (Steps 7–9) will reuse.

## Depends on
- Step 1 (database-setup) — requires `users` table, `get_db()`, `init_db()`. Complete.
- Step 2 (registration) — requires `create_user()` and the `users` schema (`name`, `email`, `created_at`). Complete.
- Step 3 (login-logout) — requires `session["user_id"]` / `session["name"]` to be set on login, and the nav's logged-in branch pointing at `/profile`. Complete.

## Routes
- `GET /profile` — renders the logged-in user's profile (name, email, member-since date) — logged-in (replaces placeholder). If no `session.user_id` is set, redirect to `/login`.

## Database changes
No database changes. `database/db.py` has no function to fetch a user by id (only `get_user_by_email`). A new `get_user_by_id(user_id)` function is needed in `database/db.py`, using the existing `users` table columns (`id`, `name`, `email`, `created_at`) — no schema changes.

## Templates
- **Create:** `templates/profile.html` — extends `base.html`; shows a header greeting (e.g. "Welcome, {{ user.name }}") and an account details block (name, email, member-since date formatted from `created_at`)
- **Modify:** none

## Files to change
- `app.py` — replace the placeholder `profile()` view: check `session.get("user_id")`, redirect to `/login` if absent, otherwise fetch the user via `get_user_by_id()` and render `profile.html`
- `database/db.py` — add `get_user_by_id(user_id)`, a parameterized query mirroring the style of `get_user_by_email`

## Files to create
- `templates/profile.html`

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug (not touched in this step, but existing hashes must not be exposed to the template)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- `get_user_by_id()` must live in `database/db.py`, never as an inline query in `app.py`
- `profile()` must guard on `session.get("user_id")` first and redirect with `redirect(url_for("login"))` if missing — mirrors the existing guard style in `login()`/`register()`
- Never pass `password_hash` into the template context — select only the columns the page needs, or omit the field when rendering
- Format `created_at` for display (e.g. "Member since July 2026") in the route or template, not by altering the stored format in the database

## Definition of done
- [x] Visiting `/profile` while logged out redirects to `/login`
- [x] Visiting `/profile` while logged in (e.g. as the seeded `demo@spendly.com` user) returns 200 and renders the profile page instead of the placeholder string
- [x] The rendered page shows the correct name and email for the logged-in user
- [x] The rendered page shows a member-since date derived from `created_at`
- [x] The page does not expose `password_hash` anywhere in the rendered HTML
- [x] The nav bar still shows "Log out" while on `/profile` (logged-in state preserved)
- [x] App starts without errors and existing routes (`/`, `/register`, `/login`, `/logout`, `/terms`, `/privacy`) are unaffected
