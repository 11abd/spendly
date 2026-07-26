import sqlite3
from datetime import datetime

from flask import Flask, abort, redirect, render_template, request, session, url_for

from werkzeug.security import check_password_hash

from database.db import (
    create_expense,
    create_user,
    delete_expense as delete_expense_row,
    get_expense_by_id,
    get_expenses_by_user,
    get_user_by_email,
    get_user_by_id,
    init_db,
    seed_db,
    update_expense,
)

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret-change-in-production"  # TODO: load from env var in production

with app.app_context():
    init_db()
    seed_db()


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("profile"))

    if request.method == "GET":
        return render_template("register.html")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    if not name:
        return render_template("register.html", error="Name is required.", name=name, email=email)

    if not email or "@" not in email:
        return render_template("register.html", error="Enter a valid email address.", name=name, email=email)

    if len(password) < 8:
        return render_template("register.html", error="Password must be at least 8 characters.", name=name, email=email)

    if get_user_by_email(email):
        return render_template("register.html", error="Email already registered.", name=name, email=email)

    try:
        user_id = create_user(name, email, password)
    except sqlite3.IntegrityError:
        return render_template("register.html", error="Email already registered.", name=name, email=email)

    session["user_id"] = user_id
    session["name"] = name
    return redirect(url_for("profile"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("profile"))

    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    if not email or not password:
        return render_template("login.html", error="Enter your email and password.", email=email)

    user = get_user_by_email(email)
    if not user or not check_password_hash(user["password_hash"], password):
        return render_template("login.html", error="Invalid email or password.", email=email)

    session["user_id"] = user["id"]
    session["name"] = user["name"]
    return redirect(url_for("profile"))


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/profile")
def profile():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    user = get_user_by_id(session["user_id"])
    if not user:
        abort(404)

    member_since = datetime.strptime(
        user["created_at"], "%Y-%m-%d %H:%M:%S"
    ).strftime("Member since %B %Y")

    expenses = get_expenses_by_user(session["user_id"])
    total_spent = sum(expense["amount"] for expense in expenses)

    top_category = None
    top_category_total = 0
    if expenses:
        category_totals = {}
        for expense in expenses:
            category_totals[expense["category"]] = (
                category_totals.get(expense["category"], 0) + expense["amount"]
            )
        top_category, top_category_total = max(category_totals.items(), key=lambda item: item[1])

    return render_template(
        "profile.html",
        user=user,
        member_since=member_since,
        expenses=expenses,
        total_spent=total_spent,
        top_category=top_category,
        top_category_total=top_category_total,
    )


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/expenses/add", methods=["GET", "POST"])
def add_expense():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    if request.method == "GET":
        return render_template("expense_form.html", mode="add")

    amount = request.form.get("amount", "").strip()
    category = request.form.get("category", "").strip()
    date = request.form.get("date", "").strip()
    description = request.form.get("description", "").strip()

    try:
        amount_value = float(amount)
        if amount_value <= 0:
            raise ValueError
    except ValueError:
        return render_template(
            "expense_form.html",
            mode="add",
            error="Enter a valid amount greater than zero.",
            amount=amount,
            category=category,
            date=date,
            description=description,
        )

    if not category:
        return render_template(
            "expense_form.html",
            mode="add",
            error="Please select a category.",
            amount=amount,
            category=category,
            date=date,
            description=description,
        )

    if not date:
        return render_template(
            "expense_form.html",
            mode="add",
            error="Please select a date.",
            amount=amount,
            category=category,
            date=date,
            description=description,
        )

    create_expense(session["user_id"], amount_value, category, date, description or None)
    return redirect(url_for("profile"))


@app.route("/expenses/<int:id>/edit", methods=["GET", "POST"])
def edit_expense(id):
    if not session.get("user_id"):
        return redirect(url_for("login"))

    expense = get_expense_by_id(id)
    if not expense or expense["user_id"] != session["user_id"]:
        abort(404)

    if request.method == "GET":
        return render_template("expense_form.html", mode="edit", expense=expense)

    amount = request.form.get("amount", "").strip()
    category = request.form.get("category", "").strip()
    date = request.form.get("date", "").strip()
    description = request.form.get("description", "").strip()

    try:
        amount_value = float(amount)
        if amount_value <= 0:
            raise ValueError
    except ValueError:
        return render_template(
            "expense_form.html",
            mode="edit",
            expense=expense,
            error="Enter a valid amount greater than zero.",
            amount=amount,
            category=category,
            date=date,
            description=description,
        )

    if not category:
        return render_template(
            "expense_form.html",
            mode="edit",
            expense=expense,
            error="Please select a category.",
            amount=amount,
            category=category,
            date=date,
            description=description,
        )

    if not date:
        return render_template(
            "expense_form.html",
            mode="edit",
            expense=expense,
            error="Please select a date.",
            amount=amount,
            category=category,
            date=date,
            description=description,
        )

    update_expense(id, amount_value, category, date, description or None)
    return redirect(url_for("profile"))


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    if not session.get("user_id"):
        return redirect(url_for("login"))

    expense = get_expense_by_id(id)
    if not expense or expense["user_id"] != session["user_id"]:
        abort(404)

    delete_expense_row(id)
    return redirect(url_for("profile"))


if __name__ == "__main__":
    app.run(debug=True, port=5001)
