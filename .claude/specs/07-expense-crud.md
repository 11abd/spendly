# Spec: Expense CRUD

## Overview
This feature implements the full expense lifecycle — add, edit, and delete — replacing the three placeholder routes (`/expenses/add`, `/expenses/<id>/edit`, `/expenses/<id>/delete`) with real, session-scoped functionality. It also wires the profile page's expense table and stats to live data from the `expenses` table, removing the hardcoded `demo_expenses` block that has stood in for real data since Step 4. This is the core purpose of Spendly — until this step, the app can authenticate users but cannot actually track a single expense. It covers Steps 7, 8, and 9 of the roadmap together since all three CRUD operations share the same data-access patterns, ownership guard, and templates.

## Depends on
- Step 1 (database-setup) — requires `expenses` table (`id`, `user_id`, `amount`, `category`, `date`, `description`, `created_at`), `get_db()`, `init_db()`. Complete.
- Step 3 (login-logout) — requires `session["user_id"]` to identify the acting user. Complete.
- Step 4 (profile) — requires `profile()` route and `profile.html` to exist as the page these routes redirect back to. Complete.

## Routes
- `GET /expenses/add` — renders a blank add-expense form — logged-in (redirect to `/login` if no session)
- `POST /expenses/add` — validates and inserts a new expense owned by the current user, redirects to `/profile` — logged-in
- `GET /expenses/<int:id>/edit` — renders the edit form pre-filled with the expense's current values — logged-in; 404 if the expense doesn't exist or isn't owned by the current user
- `POST /expenses/<int:id>/edit` — validates and updates the expense, redirects to `/profile` — logged-in; 404 if the expense doesn't exist or isn't owned by the current user
- `GET /expenses/<int:id>/delete` — deletes the expense and redirects to `/profile` — logged-in; 404 if the expense doesn't exist or isn't owned by the current user

## Database changes
No schema changes — the `expenses` table already has every column needed. New functions needed in `database/db.py` (no expense CRUD helpers exist yet):
- `get_expenses_by_user(user_id)` — `SELECT * FROM expenses WHERE user_id = ? ORDER BY date DESC`
- `get_expense_by_id(expense_id)` — `SELECT * FROM expenses WHERE id = ?` (route layer checks `user_id` ownership before use)
- `create_expense(user_id, amount, category, date, description)` — parameterized `INSERT`, returns `lastrowid`
- `update_expense(expense_id, amount, category, date, description)` — parameterized `UPDATE ... WHERE id = ?`
- `delete_expense(expense_id)` — parameterized `DELETE FROM expenses WHERE id = ?`

## Templates
- **Create:** `templates/expense_form.html` — extends `base.html`; single form reused for both add and edit (title and submit label vary via a passed-in variable, e.g. `mode="add"` vs `mode="edit"`); fields: amount, category (select, matching existing badge categories: Food, Transport, Bills, Health, Entertainment, Shopping, Other), date, description (optional)
- **Modify:** `templates/profile.html` — remove the hardcoded `demo_expenses`/`demo_total` Jinja block and the "Preview data"/"demo data" badges; render the expense table and stats from a real `expenses` list passed in from the route; add an "Add expense" link/button pointing to `url_for('add_expense')`; add per-row edit/delete links pointing to `url_for('edit_expense', id=expense.id)` / `url_for('delete_expense', id=expense.id)`

## Files to change
- `app.py` — replace all three placeholder routes with full implementations; update `profile()` to fetch the user's real expenses via `get_expenses_by_user()` and compute the stats (total, transaction count, top category) in the route instead of in the template
- `database/db.py` — add the five new functions listed above
- `templates/profile.html` — wire to real data as described above

## Files to create
- `templates/expense_form.html`

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug (not touched in this step)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- All expense DB access (`get_expenses_by_user`, `get_expense_by_id`, `create_expense`, `update_expense`, `delete_expense`) must live in `database/db.py`, never as inline queries in `app.py`
- Every expense route must guard on `session.get("user_id")` first and redirect with `redirect(url_for("login"))` if missing — mirrors the existing guard in `profile()`
- Every edit/delete route must verify the expense's `user_id` matches `session["user_id"]` before acting, and call `abort(404)` on mismatch or missing row — never leak another user's expense via ID guessing
- Validate `amount` is a positive number and `category`/`date` are non-empty on both add and edit; on validation failure, re-render the form with an `error` message and the submitted values (mirrors the `register()`/`login()` error-handling pattern)
- Reuse one template (`expense_form.html`) for both add and edit rather than duplicating markup
- Stat calculations (total spent, transaction count, top category) belong in the route function, not the template

## Definition of done
- [ ] Visiting any `/expenses/*` route while logged out redirects to `/login`
- [ ] `GET /expenses/add` renders a real form (not a placeholder string)
- [ ] Submitting valid data to `POST /expenses/add` creates a row in `expenses` owned by the current user and redirects to `/profile`
- [ ] Submitting invalid data (negative/zero amount, empty category or date) re-renders the form with an error and no row is created
- [ ] `GET /expenses/<id>/edit` for an expense owned by the current user renders the form pre-filled with its current values
- [ ] `GET /expenses/<id>/edit` for an expense owned by a different user (or a non-existent id) returns 404
- [ ] Submitting valid data to `POST /expenses/<id>/edit` updates the row and redirects to `/profile`, and the change is visible on the profile page
- [ ] `GET /expenses/<id>/delete` for an expense owned by the current user removes it and redirects to `/profile`
- [ ] `GET /expenses/<id>/delete` for an expense owned by a different user (or a non-existent id) returns 404 and does not delete anything
- [ ] `/profile` renders the logged-in user's real expenses from the database — no `demo_expenses`/"Preview data" content remains
- [ ] Profile stats (total, transaction count, top category) are computed from real data and update correctly after add/edit/delete
- [ ] App starts without errors and existing routes (`/`, `/register`, `/login`, `/logout`, `/terms`, `/privacy`, `/profile`) are unaffected
