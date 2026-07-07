from functools import wraps

from flask import session, redirect, url_for

from supabase_client import get_client


def signup(email, password):
    client = get_client()
    return client.auth.sign_up({"email": email, "password": password})


def login(email, password):
    client = get_client()
    return client.auth.sign_in_with_password({"email": email, "password": password})


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login_page"))
        return view(*args, **kwargs)
    return wrapped_view
