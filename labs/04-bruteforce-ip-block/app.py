#!/usr/bin/env python3
"""
Lab 04 — Broken brute-force protection, IP block

Five failed logins from one IP block that IP entirely. Two flaws make the
protection breakable:
  1. the failure counter resets on ANY successful login (interleave
     legitimate logins to keep the counter low), and
  2. the client IP is taken from the X-Forwarded-For header, so the block
     is trivially rotated away.
"""
import sqlite3
from collections import defaultdict

from flask import Flask, redirect, render_template, request, session

app = Flask(__name__)
app.secret_key = "lab04-not-the-vulnerability"

USERS = [
    ("wiener", "peter"),
    ("carlos", "montoya"),
    ("administrator", "sunshine"),
]

FLAG = "FLAG{04-header-trust-and-reset-logic-break-ip-blocks}"

DESC = "Reminder: five wrong logins get an IP blocked — but the block has two cracks. Find them, brute administrator's password from the downloadable list, and grab the flag. wiener / peter is your demo account."

WL_USER = "wordlists/usernames-04.txt"
WL_PASS = "wordlists/passwords-04.txt"


def _wl_count(name):
    try:
        with open(f"/app/static/{name}", "rb") as f:
            return sum(1 for _ in f)
    except OSError:
        return 0


ACCENT = "#fb7185"
HERO = "Secure sign-in for employees and administrators."
FOOTNOTE = "Protected by the SecureBank authentication gateway."

MAX_FAILURES = 5
failures = defaultdict(int)  # ip -> count


def page(user=None, error=None, flag=None):
    return render_template(
        "base.html",
        title="Lab 4 · Broken brute-force protection, IP block",
        accent=ACCENT,
        hero=HERO,
        footnote=FOOTNOTE,
        lab="Lab 4 — Broken brute-force protection, IP block",
        desc=DESC,
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


def client_ip():
    # VULN: trusts a client-controllable header instead of the connection
    return request.headers.get("X-Forwarded-For", request.remote_addr).split(",")[0].strip()


@app.get("/")
def index():
    return page(user=session.get("user"), flag=FLAG if session.get("user") == "administrator" else None)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return page()

    username = request.form.get("username", "")
    password = request.form.get("password", "")
    ip = client_ip()

    if failures[ip] >= MAX_FAILURES:
        return page(
            error="You have made too many incorrect login attempts. "
            "Please try again in 1 minute(s)."
        ), 401

    conn = db()
    row = conn.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()

    if row is not None and row[1] == password:
        failures[ip] = 0  # VULN: a successful login resets the counter
        session["user"] = username
        return redirect("/")

    failures[ip] += 1
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