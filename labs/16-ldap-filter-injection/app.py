#!/usr/bin/env python3
"""
Lab 16 — LDAP filter injection (PentesterLab ldap-02)

The login builds a directory filter with the username embedded, and the
naive evaluator treats `*` inside the value as a wildcard. Injecting a
wildcard/OR clause makes the filter match the whole directory — and the
password clause effectively collapses. The first directory entry wins —
the administrator.
"""
from flask import Flask, redirect, render_template, request, session

app = Flask(__name__)
app.secret_key = "lab16-not-the-vulnerability"

USERS = [
    ("wiener", "peter"),
    ("carlos", "montoya"),
    ("administrator", "sunshine"),
]

FLAG = "FLAG{16-ldap-filter-injection-auth-bypass}"

ACCENT = "#14b8a6"
HERO = "Secure sign-in for employees and administrators."
FOOTNOTE = "Directory service: SecureBank-AD"
DESC = ("Reminder: the login value is dropped inside a directory filter "
        "(&(uid=VALUE)(userPassword=...)). Filter values are data — until "
        "the value supplies filter syntax of its own. What does '*') do to "
        "a filter? wiener / peter is your demo account.")

WL_USER = "wordlists/usernames-16.txt"
WL_PASS = "wordlists/passwords-16.txt"


def _wl_count(name):
    try:
        with open(f"/app/static/{name}", "rb") as f:
            return sum(1 for _ in f)
    except OSError:
        return 0


def page(user=None, error=None, flag=None, content_html=None):
    return render_template(
        "base.html",
        title="Lab 16 · LDAP filter injection",
        accent=ACCENT,
        hero=HERO,
        footnote=FOOTNOTE,
        lab="Lab 16 — LDAP filter injection",
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


def directory_lookup(username, password):
    """Offline analog of building and running:
       (&(uid=<username>)(userPassword=<password>))
    """
    # VULN: the username is inserted into filter syntax. A '*' in the value
    # makes the uid clause match EVERY entry; with the clause widened, the
    # password clause is moot — the evaluator returns the administrator.
    if "*" in username or "cn=*" in username:
        return "administrator"  # directory-wide match -> admin entry
    for u, p in USERS:
        if u == username and p == password:
            return u
    return None


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
    who = directory_lookup(username, password)
    if who is None:
        return page(error="Invalid username or password"), 401
    session["user"] = who
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