#!/usr/bin/env python3
"""
Lab 08 — 2FA broken logic

The 2FA *verify* step trusts the username the client supplies in the POST.
The code is checked (against any code issued to the current session), but
the identity the session is upgraded to comes from the request — not from
the code, not from the session. Get a code for your own account and verify
with username=administrator.
"""
import secrets
import sqlite3

from flask import Flask, redirect, render_template, request, session

app = Flask(__name__)
app.secret_key = "lab08-not-the-vulnerability"

USERS = [
    ("wiener", "peter"),
    ("carlos", "montoya"),
    ("administrator", "letmein"),
]
TWOFA_USERS = {"administrator"}  # only admin has 2FA attached
# every code this app has ever issued — VULN: codes are not bound to a user
# (and not invalidated after use)
issued_codes = set()

FLAG = "FLAG{08-2fa-verify-trusts-client-username}"

ACCENT = "#818cf8"
HERO = "Secure sign-in for employees and administrators."
FOOTNOTE = "Protected by the SecureBank authentication gateway."
DESC = ("Reminder: administrator has 2FA enabled — so you will never see its "
        "code. But the verify step may trust what the request says about who "
        "is being verified. wiener / peter is your demo account.")

WL_USER = "wordlists/usernames-08.txt"
WL_PASS = "wordlists/passwords-08.txt"


def _wl_count(name):
    try:
        with open(f"/app/static/{name}", "rb") as f:
            return sum(1 for _ in f)
    except OSError:
        return 0


def page(user=None, error=None, flag=None, content_html=None):
    return render_template(
        "base.html",
        title="Lab 8 · 2FA broken logic",
        accent=ACCENT,
        hero=HERO,
        footnote=FOOTNOTE,
        lab="Lab 8 — 2FA broken logic",
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
        return redirect("/login2")
    return redirect("/")


@app.route("/login2", methods=["GET", "POST"])
def login2():
    u = session.get("user")
    if u is None:
        return redirect("/login")
    if request.method == "GET":
        # VULN: a code is issued to ANY logged-in session, 2FA-enabled or not
        code = f"{secrets.randbelow(1000000):06d}"
        issued_codes.add(code)
        html = f"""
        <h1>Two-factor authentication</h1>
        <p class="muted">A verification code was sent to your registered device.</p>
        <div class="mailbox">
          <div class="mail-item"><span class="k">SecureBank Security</span>
          <span>Your 2FA code is <code class="code">{code}</code></span></div>
        </div>
        <form method="POST" action="/login2">
          <label>Username to verify
          <input type="text" name="username" value="{u}"></label>
          <label>Verification code
          <input type="text" name="mfa-code" placeholder="000000"></label>
          <button type="submit">Verify →</button>
        </form>"""
        return page(content_html=html)
    # VULN: the code is validated, but the *identity* that gets the session
    # is whatever username the client sends. Nothing ties the two together.
    who = request.form.get("username", "")
    code_given = request.form.get("mfa-code", "")
    if not who or code_given not in issued_codes:
        return page(error="Incorrect verification code"), 401
    session["user"] = who
    return redirect("/")


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