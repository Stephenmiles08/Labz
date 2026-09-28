#!/usr/bin/env python3
"""
Lab 13 — Predictable session token (PentesterLab authe-02)

The auth cookie is not a username — it is md5(username). Deterministic,
dictionary-guessable, and forgeable for any known username, including
`administrator`. One md5sum away from the flag.
"""
import hashlib
import sqlite3

from flask import Flask, make_response, redirect, render_template, request, session

app = Flask(__name__)
app.secret_key = "lab13-not-the-vulnerability"

USERS = [
    ("wiener", "peter"),
    ("carlos", "montoya"),
    ("administrator", "letmein"),
]

FLAG = "FLAG{13-session-token-is-predictable-md5}"

ACCENT = "#f59e0b"
HERO = "Secure sign-in for employees and administrators."
FOOTNOTE = "Protected by the SecureBank authentication gateway."
DESC = ("Reminder: your identity token is derived from the username alone "
        "— a fixed, public value. If you can guess the derivation, you can "
        "spend someone else's identity. wiener / peter is your demo "
        "account.")

WL_USER = "wordlists/usernames-13.txt"
WL_PASS = "wordlists/passwords-13.txt"


def _wl_count(name):
    try:
        with open(f"/app/static/{name}", "rb") as f:
            return sum(1 for _ in f)
    except OSError:
        return 0


def page(user=None, error=None, flag=None, content_html=None):
    return render_template(
        "base.html",
        title="Lab 13 · Predictable session token",
        accent=ACCENT,
        hero=HERO,
        footnote=FOOTNOTE,
        lab="Lab 13 — Predictable session token",
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


def token_for(username):
    # VULN: deterministic function of a public value
    return hashlib.md5(username.encode()).hexdigest()


def identity():
    tok = request.cookies.get("auth")
    if not tok:
        return None
    for u, _p in USERS:
        if token_for(u) == tok:
            return u
    return None


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
    resp.set_cookie("auth", token_for(username))
    return resp


@app.get("/admin")
def admin():
    if identity() == "administrator":
        return page(user="administrator", flag=FLAG)
    return page(error="Admins only — token not recognized"), 403


@app.get("/logout")
def logout():
    resp = make_response(redirect("/"))
    resp.delete_cookie("auth")
    return resp


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)