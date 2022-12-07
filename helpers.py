from flask import redirect, render_template, session
from functools import wraps


def error(message, code=400):
    return render_template("error.html", top=code, bottom=message)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("is_staff") is not True:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function
