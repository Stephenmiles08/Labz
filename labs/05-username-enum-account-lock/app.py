#!/usr/bin/env python3
"""
Lab 05 — Username enumeration via account lock

Three failed logins lock an EXISTING account, and the error message for a
locked account is distinct ("Account locked"). Two lessons:
  1. the lock message is a username-enumeration oracle, and
  2. the lock never actually stops testing — a CORRECT password still
     logs in while locked, so brute-forcing continues past the lockout.
"""
import sqlite3
from collections import defaultdict

from flask import Flask, redirect, render_template, request, session

app = Flask(__name__)
app.secret_key = "lab05-not-the-vulnerability"

USERS = [
    ("wiener", "peter"),
    ("carlos", "montoya"),
    ("administrator", "iloveyou"),
]

FLAG = "FLAG{05-lockout-messages-are-an-enumeration-oracle}"

DESC = "Reminder: lockout protects accounts… but its own message tells you who it's protecting. Use the lock message to find administrator, then keep testing — the correct password still works. wiener / peter is your demo account."

WL_USER = "wordlists/usernames-05.txt"
WL_PASS = "wordlists/passwords-05.txt"


def _wl_count(name):
    try:
        with open(f"/app/static/{name}", "rb") as f:
            return sum(1 for _ in f)
    except OSError:
        return 0


ACCENT = "#fb923c"
HERO = "Secure sign-in for employees and administrators."
FOOTNOTE = "Protected by the SecureBank authentication gateway."

LOCK_AFTER = 3
# Per-username failed-attempt counter. LIVES WITH THE PROCESS (module-level),
# so lockout state persists across requests — as a real app's would.
attempts = defaultdict(int)


def page(user=None, error=None, flag=None):
    return render_template(
        "base.html",
        title="Lab 5 · Username enumeration via account lock",
        accent=ACCENT,
        hero=HERO,
        footnote=FOOTNOTE,
        lab="Lab 5 — Username enumeration via account lock",
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


@app.get("/")
def index():
    return page(user=session.get("user"), flag=FLAG if session.get("user") == "administrator" else None)


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

    # VULN: unknowns get the generic message; locked EXISTING accounts get
    # a distinct one — the lock message is the username oracle.
    if row is None:
        return page(error="Invalid username or password"), 401

    if row[1] == password:
        # VULN: the lock never blocks a correct password — testing can
        # continue past lockout.
        session["user"] = username
        return redirect("/")

    attempts[username] += 1

    if attempts[username] >= LOCK_AFTER:
        # VULN: the lock message is distinct from the generic error,
        # turning the lockout mechanism into a username oracle.
        return page(error="Account locked: too many incorrect password attempts"), 401

    return page(error="Incorrect password"), 401


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