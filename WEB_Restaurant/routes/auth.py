from flask import render_template, request, redirect, url_for, flash, session
from models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from settings import Session
from flask import Blueprint
import re

bp = Blueprint('auth', __name__)


def is_valid_password(password):
    """ Перевіряє, чи відповідає пароль вимогам """
    if len(password) < 8:
        return False, "password_too_short"
    if not re.search(r"\d", password):
        return False, "password_no_digit"
    if not re.search(r"[A-ZА-ЯЄІЇҐ]", password):
        return False, "password_no_uppercase"
    if not re.search(r"[a-zа-яєіїґ]", password):
        return False, "password_no_lowercase"
    return True, ""


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        current_lang = session.get('language', 'uk')
        from app import t
        flash("already_logged_in", "info")
        return redirect(url_for("index"))

    current_lang = session.get('language', 'uk')
    from app import t

    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        is_valid, error_message = is_valid_password(password)

        if not is_valid:
            flash(error_message, "error")
            return render_template("auth/register.html",
                                   t=lambda key: t(key, current_lang),
                                   lang=current_lang)

        hashed_password = generate_password_hash(password)
        user = User(username=username, email=email, hash_password=hashed_password)

        with Session() as session_db:
            existing_user = session_db.query(User).filter((User.username == username) | (User.email == email)).first()
            if existing_user:
                if existing_user.username == username:
                    flash("username_exists", "error")
                else:
                    flash("email_exists", "error")
                return render_template("auth/register.html",
                                       t=lambda key: t(key, current_lang),
                                       lang=current_lang)

            session_db.add(user)
            session_db.commit()
            flash("registration_success", "success")
            return redirect(url_for("auth.login"))

    return render_template("auth/register.html",
                           t=lambda key: t(key, current_lang),
                           lang=current_lang)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        current_lang = session.get('language', 'uk')
        from app import t
        flash("already_logged_in", "info")
        return redirect(url_for("index"))

    current_lang = session.get('language', 'uk')
    from app import t

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.get_by_username(username=username)

        if user and check_password_hash(user.hash_password, password):
            login_user(user)
            flash("login_success", "success")
            return redirect(url_for("index"))

        flash("invalid_credentials", "error")

    return render_template("auth/login.html",
                           t=lambda key: t(key, current_lang),
                           lang=current_lang)


@bp.route("/logout")
@login_required
def logout():
    current_lang = session.get('language', 'uk')
    from app import t

    logout_user()
    flash("logout_success", "success")
    return redirect(url_for("index"))