#!/usr/bin/env python3
"""
Lab 02 — Username enumeration via subtly different responses

The error message is IDENTICAL for both failure cases — except that for an
existing username the message carries one extra trailing space. Compare
response lengths byte-for-byte (Content-Length) to spot the difference.
"""
import sqlite3

from flask import Flask, redirect, render_template, request, session

app = Flask(__name__)
app.secret_key = "lab02-not-the-vulnerability"

USERS = [
    ("wiener", "peter"),
    ("carlos", "montoya"),
    ("administrator", "football"),
]

FLAG = "FLAG{02-byte-level-differences-leak-usernames}"

WL_USER = "wordlists/usernames-02.txt"
WL_PASS = "wordlists/passwords-02.txt"


def _wl_count(name):
    try:
        with open(f"/app/static/{name}", "rb") as f:
            return sum(1 for _ in f)
    except OSError:
        return 0


ACCENT = "#a78bfa"
HERO = "Secure sign-in for employees and administrators."
FOOTNOTE = "Protected by the SecureBank authentication gateway."


def page(user=None, error=None, flag=None):
    return render_template(
        "base.html",
        title="Lab 2 · Username enumeration via subtly different responses",
        accent=ACCENT,
        hero=HERO,
        footnote=FOOTNOTE,
        lab="Lab 2 — Username enumeration via subtly different responses",
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

    if row is None:
        # VULN: unknown usernames get a ONE-CHARACTER SHORTER response than
        # existing ones (existing users' message carries a trailing space).
        return page(error="Invalid username or password"), 401

    if row[1] != password:
        # VULN: note the trailing space — the only byte that differs
        return page(error="Invalid username or password "), 401

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