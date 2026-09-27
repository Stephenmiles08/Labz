#!/usr/bin/env python3
"""
Lab 01 — Username enumeration via different responses

The login handler answers differently depending on whether the username
exists ("Invalid username" vs "Incorrect password").
"""
import sqlite3

from flask import Flask, redirect, render_template, request, session

app = Flask(__name__)
app.secret_key = "lab01-not-the-vulnerability"

# (username, password) — the administrator password is in the shared wordlist
USERS = [
    ("wiener", "peter"),
    ("carlos", "montoya"),
    ("administrator", "dragon"),
]

FLAG = "FLAG{01-different-responses-reveal-valid-usernames}"

DESC = "Reminder: this lab is about the login form answering differently for real vs fake usernames — use that to find administrator, then brute its password from the downloadable list. Your demo account wiener / peter is there so you can see what a real login looks like first."

WL_USER = "wordlists/usernames-01.txt"
WL_PASS = "wordlists/passwords-01.txt"


def _wl_count(name):
    try:
        with open(f"/app/static/{name}", "rb") as f:
            return sum(1 for _ in f)
    except OSError:
        return 0


ACCENT = "#22d3ee"
HERO = "Secure sign-in for employees and administrators."
FOOTNOTE = "Protected by the SecureBank authentication gateway."


def page(user=None, error=None, flag=None):
    return render_template(
        "base.html",
        title="Lab 1 · Username enumeration via different responses",
        accent=ACCENT,
        hero=HERO,
        footnote=FOOTNOTE,
        lab="Lab 1 — Username enumeration via different responses",
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

    # VULN: the error message discloses username validity
    if row is None:
        return page(error="Invalid username"), 401
    if row[1] != password:
        return page(error="Incorrect password"), 401

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