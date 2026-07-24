# Spec: Registration

## Overview
This feature implements user registration for Spendly: a working `POST /register` handler that validates input, creates a new user with a hashed password, starts a session, and redirects into the app. This is the second step of the roadmap, following the database foundation, and is a prerequisite for login, logout, and every user-scoped feature (profile, expenses) that comes after it.

## Depends on
- Step 1 (database-setup) — requires `users` table, `get_db()`, `init_db()` to exist and work. Complete.

## Routes
- `GET /register` — renders the registration form — public (already exists, unchanged)
- `POST /register` — validates form input, creates the user, starts a session, redirects to `/profile` — public (new)

## Database changes
No database changes. The `users` table (id, name, email, password_hash, created_at) already supports registration. No new columns or constraints needed.

## Templates
- **Create:** none
- **Modify:** `templates/register.html` — no structural changes needed; it already posts to `/register` and renders `{{ error }}`. Values should be re-populated on validation failure (`value="{{ name or '' }}"` / `value="{{ email or '' }}"` on the inputs) so users don't retype everything.

## Files to change
- `app.py` — replace the placeholder `register()` view with a function handling both GET and POST, including validation, user creation, session start, and redirect
- `database/db.py` — add a `create_user(name, email, password)` function and a `get_user_by_email(email)` function
- `templates/register.html` — repopulate `name`/`email` field values on redisplay after a validation error

## Files to create
None.

## New dependencies
No new dependencies. Uses `werkzeug.security.generate_password_hash` (already imported in `database/db.py`) and Flask's built-in `session`.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug (`generate_password_hash`, never store plaintext)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- `app.secret_key` must be set for `session` to work (add via `app.config["SECRET_KEY"]`, e.g. from `os.urandom` or a fixed dev value — flag to the user that production needs a real secret)
- Validate on the server even though HTML5 `required`/`type=email` exist client-side: name non-empty, email non-empty and contains "@", password minimum 8 characters
- Enforce unique email at the application level by checking `get_user_by_email` before insert, and handle the `sqlite3.IntegrityError` from the UNIQUE constraint as a fallback — show a friendly "Email already registered" error via the existing `{{ error }}` block rather than a stack trace
- On success, store `user_id` (and optionally `name`) in `session`, then redirect (`redirect(url_for("profile"))`)
- Do not log or expose password values in error messages

## Definition of done
- [ ] Visiting `/register` shows the form with no errors
- [ ] Submitting valid name/email/password creates a row in `users` with a hashed (not plaintext) password
- [ ] After successful registration, the browser is redirected to `/profile` and a session cookie is set
- [ ] Submitting an email that already exists shows "Email already registered" on the same form, with name/email fields still filled in, and no duplicate row is created
- [ ] Submitting a password under 8 characters shows a validation error and creates no row
- [ ] Submitting an empty name or an email without "@" shows a validation error and creates no row
- [ ] App starts without errors and existing routes (`/`, `/login`, `/terms`, `/privacy`) are unaffected
