#!/usr/bin/env python3
"""
Lab 07 — 2FA simple bypass

Two-factor authentication is required… but only enforced on the 2FA page
itself. After a successful credential login the session knows who you are,
and every other route trusts that without checking whether 2FA was
completed. Log in as administrator and navigate straight past /login2.
"""
import secrets
import sqlite3

from flask import Flask, redirect, render_template, request, session

app = Flask(__name__)
app.secret_key = "lab07-not-the-vulnerability"

USERS = [
    ("wiener", "peter"),
    ("carlos", "montoya"),
    ("administrator", "freedom"),
]
TWOFA_USERS = {"carlos", "administrator"}  # 2FA enforced on these accounts

FLAG = "FLAG{07-2fa-is-enforced-on-one-page-only}"

ACCENT = "#2dd4bf"
HERO = "Secure sign-in for employees and administrators."
FOOTNOTE = "Protected by the SecureBank authentication gateway."
DESC = ("Reminder: administrator has two-factor authentication enabled — you "
        "still need its password, but the 2FA step might be the only door "
        "worth worrying about. wiener / peter is your demo account.")

WL_USER = "wordlists/usernames-07.txt"
WL_PASS = "wordlists/passwords-07.txt"


def _wl_count(name):
    try:
        with open(f"/app/static/{name}", "rb") as f:
            return sum(1 for _ in f)
    except OSError:
        return 0


def page(user=None, error=None, flag=None, content_html=None):
    return render_template(
        "base.html",
        title="Lab 7 · 2FA simple bypass",
        accent=ACCENT,
        hero=HERO,
        footnote=FOOTNOTE,
        lab="Lab 7 — 2FA simple bypass",
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


def current_user():
    u = session.get("user")
    return u


@app.get("/")
def index():
    u = current_user()
    if u is None:
        return page()
    # FLAW: no 2FA check here — only "is someone logged in"
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
    session["2fa_ok"] = False
    if username in TWOFA_USERS:
        # VULN: nothing here stops the client from never visiting /login2
        return redirect("/login2")
    return redirect("/")


@app.route("/login2", methods=["GET", "POST"])
def login2():
    u = session.get("user")
    if u is None:
        return redirect("/login")
    if request.method == "GET":
        code = f"{secrets.randbelow(1000000):06d}"
        session["code"] = code
        html = f"""
        <h1>Two-factor authentication</h1>
        <p class="muted">A verification code was sent to your registered device.</p>
        <div class="mailbox">
          <div class="mail-item"><span class="k">SecureBank Security</span>
          <span>Your 2FA code is <code class="code">{code}</code></span></div>
        </div>
        <form method="POST" action="/login2">
          <label>Verification code
          <input type="text" name="code" placeholder="000000" autofocus></label>
          <button type="submit">Verify →</button>
        </form>"""
        return page(content_html=html)
    if request.form.get("code", "") == session.get("code"):
        session["2fa_ok"] = True
        return redirect("/")
    return page(error="Incorrect code"), 401


@app.get("/admin")
def admin():
    u = current_user()
    # FLAW: trusts the session identity without requiring 2fa_ok
    if u == "administrator":
        return page(user=u, flag=FLAG)
    return page(error="Admins only"), 403


@app.get("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)