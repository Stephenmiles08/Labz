#!/usr/bin/env python3
"""
Lab 09 — 2FA bypass using a brute-force attack

The verification code is a random 4-digit number. The endpoint never
locks, never throttles, and never expires the code — the entire 0000-9999
space is testable in one long loop. No list needed; the math is the
wordlist.
"""
import secrets
import sqlite3

from flask import Flask, redirect, render_template, request, session

app = Flask(__name__)
app.secret_key = "lab09-not-the-vulnerability"

USERS = [
    ("wiener", "peter"),
    ("carlos", "montoya"),
    ("administrator", "123456"),
]
TWOFA_USERS = {"administrator"}

FLAG = "FLAG{09-2fa-code-space-is-bruteforceable}"

ACCENT = "#f472b6"
HERO = "Secure sign-in for employees and administrators."
FOOTNOTE = "Protected by the SecureBank authentication gateway."
DESC = ("Reminder: administrator has 2FA enabled and its code never appears "
        "on screen. Four digits is a small number — maybe the whole space "
        "can be tried. wiener / peter is your demo account.")

WL_USER = "wordlists/usernames-09.txt"
WL_PASS = "wordlists/passwords-09.txt"


def _wl_count(name):
    try:
        with open(f"/app/static/{name}", "rb") as f:
            return sum(1 for _ in f)
    except OSError:
        return 0


def page(user=None, error=None, flag=None, content_html=None):
    return render_template(
        "base.html",
        title="Lab 9 · 2FA bypass using a brute-force attack",
        accent=ACCENT,
        hero=HERO,
        footnote=FOOTNOTE,
        lab="Lab 9 — 2FA bypass using a brute-force attack",
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
    session["user"] = username
    if username in TWOFA_USERS:
        session["code"] = f"{secrets.randbelow(10000):04d}"  # 0000-9999
        return redirect("/login2")
    return redirect("/")


@app.route("/login2", methods=["GET", "POST"])
def login2():
    u = session.get("user")
    if u is None:
        return redirect("/login")
    if request.method == "GET":
        html = """
        <h1>Two-factor authentication</h1>
        <p class="muted">A verification code was sent to your registered device.</p>
        <form method="POST" action="/login2">
          <label>Verification code
          <input type="text" name="code" placeholder="0000" autofocus></label>
          <button type="submit">Verify →</button>
        </form>"""
        return page(content_html=html)
    # VULN: no lockout, no throttle, no expiry — try again forever
    if request.form.get("code", "") == session.get("code"):
        return redirect("/")
    return page(error="Incorrect code"), 401


@app.get("/admin")
def admin():
    u = session.get("user")
    if u == "administrator":
        return page(user=u, flag=FLAG)
    return page(error="Admins only"), 403


@app.get("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)