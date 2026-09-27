#!/usr/bin/env python3
"""
Lab 03 — Username enumeration via response timing

A fast path is taken when the username does not exist, while an existing
username forces the handler through an expensive password verification
(simulated with time.sleep). The response-time differential is the oracle.
"""
import sqlite3
import time

from flask import Flask, redirect, render_template, request, session

app = Flask(__name__)
app.secret_key = "lab03-not-the-vulnerability"

USERS = [
    ("wiener", "peter"),
    ("carlos", "montoya"),
    ("administrator", "monkey"),
]

FLAG = "FLAG{03-timing-is-an-enumeration-oracle}"

WL_USER = "wordlists/usernames-03.txt"
WL_PASS = "wordlists/passwords-03.txt"


def _wl_count(name):
    try:
        with open(f"/app/static/{name}", "rb") as f:
            return sum(1 for _ in f)
    except OSError:
        return 0


ACCENT = "#fbbf24"
HERO = "Secure sign-in for employees and administrators."
FOOTNOTE = "Protected by the SecureBank authentication gateway."


def page(user=None, error=None, flag=None):
    return render_template(
        "base.html",
        title="Lab 3 · Username enumeration via response timing",
        accent=ACCENT,
        hero=HERO,
        footnote=FOOTNOTE,
        lab="Lab 3 — Username enumeration via response timing",
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

    # VULN: the password check runs only for existing usernames, so valid
    # usernames take measurably longer (simulated bcrypt compare).
    if row is None:
        return page(error="Invalid username or password"), 401

    time.sleep(0.6)  # stand-in for an expensive credential verification

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