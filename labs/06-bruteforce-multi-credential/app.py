#!/usr/bin/env python3
"""
Lab 06 — Broken brute-force protection, multiple credentials per request

The login endpoint accepts JSON and will test a LIST of passwords in a
single request, authenticating if ANY of them matches. The whole wordlist
fits in one request, so no rate limit, lockout, or IP block ever engages.
"""
import sqlite3

from flask import Flask, jsonify, redirect, render_template, request, session

app = Flask(__name__)
app.secret_key = "lab06-not-the-vulnerability"

USERS = [
    ("wiener", "peter"),
    ("carlos", "montoya"),
    ("administrator", "gandalf"),
]

FLAG = "FLAG{06-one-request-can-test-the-whole-wordlist}"

WL_USER = "wordlists/usernames-06.txt"
WL_PASS = "wordlists/passwords-06.txt"


def _wl_count(name):
    try:
        with open(f"/app/static/{name}", "rb") as f:
            return sum(1 for _ in f)
    except OSError:
        return 0


ACCENT = "#34d399"
HERO = "Secure sign-in for employees and administrators."
FOOTNOTE = "API clients may POST JSON to /login instead of using this form."


def page(user=None, error=None, flag=None):
    return render_template(
        "base.html",
        title="Lab 6 · Broken brute-force protection, multiple credentials per request",
        accent=ACCENT,
        hero=HERO,
        footnote=FOOTNOTE,
        lab="Lab 6 — Broken brute-force protection, multiple credentials per request",
        wl_user=WL_USER,
        wl_pass=WL_PASS,
        wl_user_lines=_wl_count(WL_USER),
        wl_pass_lines=_wl_count(WL_PASS),
        user=user,
        error=error,
        admin_flag=flag,
    )


def db():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users (username TEXT PRIMARY KEY, password TEXT)")
    for u, p in USERS:
        conn.execute("INSERT INTO users VALUES (?, ?)", (u, p))
    conn.commit()
    return conn


@app.get("/")
def index():
    return page(user=session.get("user"), flag=FLAG if session.get("user") == "administrator" else None)


def parse_credentials():
    """Accept classic form posts OR a JSON API body."""
    if request.is_json:
        data = request.get_json(silent=True) or {}
        return data.get("username", ""), data.get("password")
    return request.form.get("username", ""), request.form.get("password", "")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return page()

    username, password = parse_credentials()

    # VULN: a list of passwords is accepted and every entry is tested.
    # A rate limiter cannot help when the whole attack is one request.
    if isinstance(password, list):
        candidates = [str(p) for p in password]
    else:
        candidates = [str(password or "")]

    conn = db()
    row = conn.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()

    if row is not None and any(c == row[1] for c in candidates):
        session["user"] = username
        if request.is_json:
            return jsonify({"ok": True, "user": username})
        return redirect("/")

    if request.is_json:
        return jsonify({"ok": False}), 401
    return page(error="Invalid username or password"), 401


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