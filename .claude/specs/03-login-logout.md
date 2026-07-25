# Spec: Login and Logout

## Overview
This feature implements session-based authentication for Spendly: a working `POST /login` handler that verifies email/password against the `users` table and starts a session, plus a `GET /logout` handler that clears the session and returns the user to the landing page. This is the third step of the roadmap, following database setup and registration, and is a prerequisite for profile and every other user-scoped feature that comes after it.

## Depends on
- Step 1 (database-setup) — requires `users` table, `get_db()`, `init_db()`. Complete.
- Step 2 (registration) — requires `create_user()`, `get_user_by_email()`, and the session-based login pattern (`session["user_id"]`, `session["name"]`) established during registration. Complete.

## Routes
- `GET /login` — renders the login form; redirects to `/profile` if already logged in — public
- `POST /login` — validates credentials, starts a session, redirects to `/profile` — public (new)
- `GET /logout` — clears the session, redirects to `/` — logged-in (replaces placeholder)
- `GET /register` — redirects to `/profile` if already logged in (unchanged otherwise) — public

## Database changes
No database changes. `get_user_by_email(email)` (added in Step 2) already returns the row needed to verify a password hash. No new columns or constraints needed.

## Templates
- **Create:** none
- **Modify:** `templates/login.html` — repopulate the `email` field value on redisplay after a validation error (`value="{{ email or '' }}"` on the email input), matching the pattern used in `register.html`
- **Modify:** `templates/base.html` — nav currently always shows "Sign in" / "Get started" regardless of session state; add a logged-in branch showing a "Log out" link (pointing to `/logout`) when `session.user_id` is set, keeping the existing public links otherwise

## Files to change
- `app.py` — replace the placeholder `login()` view with a function handling both GET and POST (validation, credential check, session start, redirect); replace the placeholder `logout()` view with a function that clears the session and redirects to `/`
- `database/db.py` — no changes expected; reuse existing `get_user_by_email`
- `templates/login.html` — repopulate `email` field value on validation failure
- `templates/base.html` — add logged-in/logged-out nav branching

## Files to create
None.

## New dependencies
No new dependencies. Uses `werkzeug.security.check_password_hash` (pair to the existing `generate_password_hash`) and Flask's built-in `session`.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug — verify with `check_password_hash`, never compare plaintext
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Validate on the server: email non-empty, password non-empty
- Look up the user with `get_user_by_email(email)`; if no user is found, or `check_password_hash(user["password_hash"], password)` fails, show a single generic error ("Invalid email or password") via the existing `{{ error }}` block — do not reveal whether the email exists, to avoid user enumeration
- On success, store `user_id` and `name` in `session` (same keys used by registration) and redirect with `redirect(url_for("profile"))`
- `logout()` must clear the session (`session.clear()`) rather than deleting keys individually, then redirect with `redirect(url_for("landing"))`
- Do not log or expose password values in error messages or logs
- Both `login()` and `register()` must check `session.get("user_id")` first and redirect to `/profile` if already logged in, before handling GET or POST — a logged-in user should never see the login/register forms

## Definition of done
- [x] Visiting `/login` shows the form with no errors
- [x] Submitting the seeded demo user's credentials (`demo@spendly.com` / `demo123`) redirects to `/profile` and sets a session cookie
- [x] Submitting a correct email with the wrong password shows "Invalid email or password" on the same form, with the email field still filled in, and no session is created
- [x] Submitting an email that doesn't exist shows the same "Invalid email or password" message (not a different one) and no session is created
- [x] Submitting an empty email or empty password shows a validation error and no session is created
- [x] Visiting `/logout` while logged in clears the session and redirects to `/`
- [x] After `/logout`, the nav bar shows "Sign in" / "Get started" again instead of "Log out"
- [x] While logged in, the nav bar shows a "Log out" link instead of "Sign in" / "Get started"
- [x] App starts without errors and existing routes (`/`, `/register`, `/terms`, `/privacy`) are unaffected
- [x] While logged in, visiting `/login` redirects to `/profile` instead of showing the login form
- [x] While logged in, visiting `/register` redirects to `/profile` instead of showing the registration form
- [x] While logged out, `/login` and `/register` still render normally (200, not redirected)
