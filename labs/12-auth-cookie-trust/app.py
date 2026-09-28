#!/usr/bin/env python3
"""
Lab 12 — Auth cookie trust (PentesterLab authe-01)

The application's entire identity model is a cookie called `auth` whose
value is the username, sent in cleartext to the browser. The server reads
it back and trusts it wholesale: no signing, no server-side session.
Anyone can mint an administrator.
"""
import sqlite3

from flask import Flask, make_response, redirect, render_template, request, session

app = Flask(__name__)
app.secret_key = "lab12-not-the-vulnerability"

USERS = [
    ("wiener", "peter"),
    ("carlos", "montoya"),
    ("administrator", "freedom"),
]

FLAG = "FLAG{12-auth-cookie-trusts-client-value}"

ACCENT = "#38bdf8"
HERO = "Secure sign-in for employees and administrators."
FOOTNOTE = "Protected by the SecureBank authentication gateway."
DESC = ("Reminder: this app does not use server-side sessions — it keeps "
        "your identity in a cookie the browser can read and write. The "
        "question is what the server does with that cookie. The "
        "administrator's password is in the downloadable list if you ever "
        "want the 'normal' login.")

WL_USER = "wordlists/usernames-12.txt"
WL_PASS = "wordlists/passwords-12.txt"


def _wl_count(name):
    try:
        with open(f"/app/static/{name}", "rb") as f:
            return sum(1 for _ in f)
    except OSError:
        return 0


def page(user=None, error=None, flag=None, content_html=None):
    return render_template(
        "base.html",
        title="Lab 12 · Auth cookie trust",
        accent=ACCENT,
        hero=HERO,
        footnote=FOOTNOTE,
        lab="Lab 12 — Auth cookie trust",
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
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users (username TEXT PRIMARY KEY, password TEXT)")
    for u, p in USERS:
        conn.execute("INSERT INTO users VALUES (?, ?)", (u, p))
    conn.commit()
    return conn


def identity():
    # VULN: the whole authentication state is this one client-supplied cookie
    return request.cookies.get("auth")


@app.get("/")
def index():
    u = identity()
    if u is None:
        return page()
    return page(user=u, flag=FLAG if u == "administrator" else None)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return page()
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    conn = db()
    row = conn.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()
    if row is None:
        return page(error="Invalid username"), 401
    if row[1] != password:
        return page(error="Incorrect password"), 401
    resp = make_response(redirect("/"))
    # VULN: identity is handed to the client as a mutable cookie
    resp.set_cookie("auth", username)
    return resp


@app.get("/admin")
def admin():
    if identity() == "administrator":
        return page(user="administrator", flag=FLAG)
    return page(error="Admins only — who are you?"), 403


@app.get("/logout")
def logout():
    resp = make_response(redirect("/"))
    resp.delete_cookie("auth")
    return resp


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)