#!/usr/bin/env python3
"""
Lab 15 — Null bind (PentesterLab ldap-01)

The login is wired to a directory service the way LDAP often is: the
credential filters are built from the submitted form fields. When the
form fields are absent entirely, the request performs an ANONYMOUS BIND —
and this directory grants the anonymous bind full default privileges
(namely, the administrator).
"""
from flask import Flask, redirect, render_template, request, session

app = Flask(__name__)
app.secret_key = "lab15-not-the-vulnerability"

USERS = [
    ("wiener", "peter"),
    ("carlos", "montoya"),
    ("administrator", "monkey"),
]

FLAG = "FLAG{15-anonymous-bind-accepted}"

ACCENT = "#e879f9"
HERO = "Secure sign-in for employees and administrators."
FOOTNOTE = "Directory service: SecureBank-AD"
DESC = ("Reminder: LDAP binds authenticate even when no credentials are "
        "presented — if the handler composes a filter from form fields and "
        "those fields never arrive, the request binds with NO identity. "
        "Send a credential POST with no credentials at all. wiener / peter "
        "is your demo account.")

WL_USER = "wordlists/usernames-15.txt"
WL_PASS = "wordlists/passwords-15.txt"


def _wl_count(name):
    try:
        with open(f"/app/static/{name}", "rb") as f:
            return sum(1 for _ in f)
    except OSError:
        return 0


def page(user=None, error=None, flag=None, content_html=None):
    return render_template(
        "base.html",
        title="Lab 15 · Null bind",
        accent=ACCENT,
        hero=HERO,
        footnote=FOOTNOTE,
        lab="Lab 15 — Null bind",
        desc=DESC,
        user=user,
        error=error,
        admin_flag=flag,
        content_html=content_html,
        wl_user=WL_USER,
        wl_pass=WL_PASS,
        wl_user_lines=_wl_count(WL_USER),
        wl_pass_lines=_wl_count(WL_PASS),
    )


def db():
    import sqlite3
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users (username TEXT PRIMARY KEY, password TEXT)")
    for u, p in USERS:
        conn.execute("INSERT INTO users VALUES (?, ?)", (u, p))
    conn.commit()
    return conn


@app.get("/")
def index():
    u = session.get("user")
    if u is None:
        return page()
    return page(user=u, flag=FLAG if u == "administrator" else None)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return page()
    # VULN: request.form.get returns None when the field is ABSENT, and the
    # handler treats 'no username' as "null bind" — authenticated with the
    # directory's default identity instead of failing closed.
    username = request.form.get("username")
    password = request.form.get("password")
    if username is None and password is None:
        session["user"] = "administrator"  # anonymous bind => default admin
        return redirect("/")
    if username is None or password is None:
        return page(error="Invalid username or password"), 401
    conn = db()
    row = conn.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()
    if row is None or row[1] != password:
        return page(error="Invalid username or password"), 401
    session["user"] = username
    return redirect("/")


@app.get("/admin")
def admin():
    if session.get("user") == "administrator":
        return page(user="administrator", flag=FLAG)
    return page(error="Admins only"), 403


@app.get("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)