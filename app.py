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


@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    user_id = session["user_id"]
    if request.method == "POST":
        action = request.form.get("action")
        name = request.form.get("name", "").strip()
        if name and action == "add":
            inventory_service.add_item(user_id, name)
        elif name and action == "remove":
            inventory_service.remove_item(user_id, name)
        return redirect(url_for("dashboard"))

    inventory_items = sorted(inventory_service.list_items(user_id))
    statuses = cocktail_service.cocktail_statuses(set(inventory_items))
    return render_template("dashboard.html", inventory_items=inventory_items, statuses=statuses)


@app.route("/cocktail/<name>")
@login_required
def cocktail_detail(name):
    cocktail = cocktail_service.show_cocktail(name)
    return render_template("cocktail_detail.html", cocktail=cocktail, name=name)


if __name__ == "__main__":
    app.run(debug=True)
