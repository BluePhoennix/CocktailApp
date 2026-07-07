import os

from dotenv import load_dotenv

load_dotenv()

from flask import Flask, render_template, request, redirect, url_for, session, flash

from auth import signup, login, login_required
import cocktail_service
import inventory_service

app = Flask(__name__)
app.secret_key = os.environ["FLASK_SECRET_KEY"]


@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login_page"))


@app.route("/signup", methods=["GET", "POST"])
def signup_page():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        try:
            signup(email, password)
            flash("Account created. Check your email to confirm, then log in.")
            return redirect(url_for("login_page"))
        except Exception as e:
            flash(str(e))
    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        try:
            result = login(email, password)
            session["user_id"] = result.user.id
            session["email"] = result.user.email
            return redirect(url_for("dashboard"))
        except Exception as e:
            flash("Login failed: " + str(e))
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", email=session.get("email"))


@app.route("/inventory", methods=["GET", "POST"])
@login_required
def inventory_page():
    user_id = session["user_id"]
    if request.method == "POST":
        action = request.form.get("action")
        name = request.form.get("name", "").strip()
        if name and action == "add":
            inventory_service.add_item(user_id, name)
        elif name and action == "remove":
            inventory_service.remove_item(user_id, name)
        return redirect(url_for("inventory_page"))
    items = sorted(inventory_service.list_items(user_id))
    return render_template("inventory.html", items=items)


@app.route("/search")
@login_required
def search_page():
    query = request.args.get("q", "")
    results = cocktail_service.search(query) if query else []
    return render_template("search.html", query=query, results=results)


@app.route("/cocktail/<name>")
@login_required
def cocktail_detail(name):
    cocktail = cocktail_service.show_cocktail(name)
    return render_template("cocktail_detail.html", cocktail=cocktail, name=name)


@app.route("/cocktails")
@login_required
def cocktails_page():
    inventory_names = inventory_service.list_items(session["user_id"])
    statuses = cocktail_service.cocktail_statuses(inventory_names)
    return render_template("cocktails.html", statuses=statuses)


if __name__ == "__main__":
    app.run(debug=True)
