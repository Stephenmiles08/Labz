#!/usr/bin/env python3
"""
Lab 14 — Case-insensitive login collision (PentesterLab authe-03/04)

Registration validates usernames with case-sensitive equality, but login
looks accounts up case-insensitively (as MySQL VARCHAR does with its
default collation, and as this app's directory lookup does). Register a
case-variant of the administrator's name and the login returns the REAL
administrator row.
"""
from flask import Flask, redirect, render_template, request, session

app = Flask(__name__)
app.secret_key = "lab14-not-the-vulnerability"

USERS = [
    ("wiener", "peter"),
    ("carlos", "montoya"),
    ("administrator", "freedom"),
]

FLAG = "FLAG{14-case-insensitive-login-collision}"

ACCENT = "#84cc16"
HERO = "Secure sign-in for employees and administrators."
FOOTNOTE = "Protected by the SecureBank authentication gateway."
DESC = ("Reminder: two checks in one system can disagree on what counts as "
        "the same name. Registration sees 'ADMINISTRATOR' as brand new; "
        "the login lookup sees it as the existing administrator. Find the "
        "name that is both — and claim the flag.")

WL_USER = "wordlists/usernames-14.txt"
WL_PASS = "wordlists/passwords-14.txt"


def _wl_count(name):
    try:
        with open(f"/app/static/{name}", "rb") as f:
            return sum(1 for _ in f)
    except OSError:
        return 0


def page(user=None, error=None, flag=None, content_html=None):
    return render_template(
        "base.html",
        title="Lab 14 · Case-insensitive login collision",
        accent=ACCENT,
        hero=HERO,
        footnote=FOOTNOTE,
        lab="Lab 14 — Case-insensitive login collision",
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


# process-level store: registration MUST persist across requests
users = dict(USERS)  # insertion order = seed first, registrations after


def ci_lookup(name):
    """VULN: case-insensitive match. Returns EVERY stored row whose name
    compares equal ignoring case — so a registered 'ADMINISTRATOR' and the
    seeded 'administrator' are the SAME identity here."""
    return [stored for stored in users if stored.lower() == name.lower()]


@app.get("/")
def index():
    u = session.get("user")
    if u is None:
        return page()
    return page(user=u, flag=FLAG if u == "administrator" else None)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        html = """
        <h1>Create an account</h1>
        <form method="POST" action="/register">
          <label>Username <input type="text" name="username" autofocus></label>
          <label>Password <input type="password" name="password"></label>
          <button type="submit">Register →</button>
        </form>"""
        return page(content_html=html)
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    if not username or not password:
        return page(error="Username and password required"), 401
    # VULN: only EXACT-case duplicates are rejected — a case-variant of an
    # existing name registers as "brand new" but is the same identity to
    # the ci login lookup (MySQL VARCHAR default collation behaves the same)
    if username in users:
        return page(error=f"Username '{username}' is taken"), 401
    users[username] = password
    return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return page()
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    # VULN: the identity is resolved case-insensitively, so a registered
    # case-variant ends up in the SAME identity set as the real account —
    # a credential registered for 'ADMINISTRATOR' validates the
    # administrator identity.
    matches = ci_lookup(username)
    if not matches:
        return page(error="Invalid username or password"), 401
    if not any(users[m] == password for m in matches):
        return page(error="Invalid username or password"), 401
    if "administrator" in matches:
        session["user"] = "administrator"  # collided identity -> admin role
    else:
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