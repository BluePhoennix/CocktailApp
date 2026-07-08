import os

from dotenv import load_dotenv

load_dotenv()

from flask import Flask, render_template, request, redirect, url_for, session, flash

from auth import signup, login, login_required
import cocktail_service
import inventory_service
import profile_service

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
            result = signup(email, password)
            profile_service.create_profile(result.user.id)
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

    share_code = profile_service.get_share_code(user_id)
    if share_code is None:
        share_code = profile_service.create_profile(user_id)
    share_url = url_for("view_page", share_code=share_code, _external=True)

    return render_template(
        "dashboard.html", inventory_items=inventory_items, statuses=statuses, share_url=share_url
    )


@app.route("/cocktails/new", methods=["GET", "POST"])
@login_required
def add_cocktail_page():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        instructions = request.form.get("instructions", "").strip()
        ingredient_names = request.form.getlist("ingredient_name")
        ingredient_amounts = request.form.getlist("ingredient_amount")
        ingredients = [
            {"name": ing_name.strip(), "amount": ing_amount.strip()}
            for ing_name, ing_amount in zip(ingredient_names, ingredient_amounts)
            if ing_name.strip() and ing_amount.strip()
        ]

        if not name or not instructions or not ingredients:
            flash("A cocktail needs a name, at least one ingredient with an amount, and instructions.")
            return render_template("add_cocktail.html")

        try:
            cocktail_service.create_cocktail(name, instructions, ingredients)
            flash(f"{name} added to the recipe book.")
            return redirect(url_for("dashboard"))
        except Exception as e:
            flash(str(e))
            return render_template("add_cocktail.html")

    return render_template("add_cocktail.html")


@app.route("/view/<share_code>")
def view_page(share_code):
    owner_id = profile_service.get_user_id_by_share_code(share_code)
    if owner_id is None:
        return render_template("view.html", found=False, makeable=[])

    inventory_names = inventory_service.list_items(owner_id)
    statuses = cocktail_service.cocktail_statuses(inventory_names)
    makeable = [s for s in statuses if s["state"] == "can_make"]
    return render_template("view.html", found=True, makeable=makeable)


if __name__ == "__main__":
    app.run(debug=True)
