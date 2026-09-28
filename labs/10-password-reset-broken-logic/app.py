#!/usr/bin/env python3
"""
Lab 10 — Password reset broken logic

A reset token is issued and emailed… but when the token is redeemed, the
username whose password changes comes from the REQUEST, not from the token.
Properly, the token carries the account identity. Here it carries nothing
except validity. Request a reset for yourself, then redeem your token
against administrator's username.
"""
import secrets
import sqlite3

from flask import Flask, redirect, render_template, request, session

app = Flask(__name__)
app.secret_key = "lab10-not-the-vulnerability"

USERS = [
    ("wiener", "peter"),
    ("carlos", "montoya"),
    ("administrator", "freedom"),
]
# process-level user store — password resets MUST persist across requests
users = dict(USERS)

tokens = {}        # token -> recipient (mail is delivered to the recipient)
mailbox = {}       # username -> list of mail dicts

FLAG = "FLAG{10-reset-token-not-bound-to-user}"

ACCENT = "#fb923c"
HERO = "Secure sign-in for employees and administrators."
FOOTNOTE = "Protected by the SecureBank authentication gateway."
DESC = ("Reminder: when a reset token is used, which account's password "
        "changes is decided in the request — the token may only prove you "
        "have some mailbox, not WHICH one. wiener / peter is your demo "
        "account, and you can read your own mail.")

WL_USER = "wordlists/usernames-10.txt"
WL_PASS = "wordlists/passwords-10.txt"


def _wl_count(name):
    try:
        with open(f"/app/static/{name}", "rb") as f:
            return sum(1 for _ in f)
    except OSError:
        return 0


def page(user=None, error=None, flag=None, content_html=None):
    return render_template(
        "base.html",
        title="Lab 10 · Password reset broken logic",
        accent=ACCENT,
        hero=HERO,
        footnote=FOOTNOTE,
        lab="Lab 10 — Password reset broken logic",
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
    if username not in users:
        return page(error="Invalid username"), 401
    if users[username] != password:
        return page(error="Incorrect password"), 401
    session["user"] = username
    return redirect("/")


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "GET":
        tok = request.args.get("token")
        if tok:  # arrive here from the email link
            if tok not in tokens:
                return page(error="Invalid or expired reset token"), 401
            html = f"""
            <h1>Reset your password</h1>
            <p class="muted">Account: <b>{tokens[tok]}</b></p>
            <form method="POST" action="/forgot-password">
              <input type="hidden" name="token" value="{tok}">
              <label>Username <input type="text" name="username" value="{tokens[tok]}"></label>
              <label>New password <input type="password" name="new-password"></label>
              <button type="submit">Reset password →</button>
            </form>"""
            return page(content_html=html)
        html = """
        <h1>Forgot your password?</h1>
        <p class="muted">Enter your username and we'll email you a reset link.</p>
        <form method="POST" action="/forgot-password">
          <label>Username <input type="text" name="username" autofocus></label>
          <button type="submit">Send reset link →</button>
        </form>"""
        return page(content_html=html)

    # POST: either "request reset" or "redeem reset"
    tok = request.form.get("token")
    if tok:
        # VULN: the username in the POST is trusted; the token only has to
        # be a VALID token — it is never matched to this username.
        who = request.form.get("username", "")
        new_pw = request.form.get("new-password", "")
        if tok not in tokens:
            return page(error="Invalid or expired reset token"), 401
        users[who] = new_pw  # VULN: username comes from the client
        del tokens[tok]
        return page(content_html="<h1>Password updated</h1><p class='muted'>Sign in with your new password.</p>")

    who = request.form.get("username", "")
    if who not in users:
        return page(error="Unknown username"), 401
    tok = secrets.token_urlsafe(16)
    tokens[tok] = who
    mailbox.setdefault(who, []).append({
        "from": "SecureBank Security <no-reply@securebank.local>",
        "subject": "Password reset request",
        "body": f"Click here to reset your password:\n/forgot-password?token={tok}",
    })
    return page(content_html="<h1>Reset link sent</h1><p class='muted'>Check your mailbox.</p>")


@app.get("/mail")
def mail():
    u = session.get("user")
    if u is None:
        return redirect("/login")
    items = "".join(
        f'<div class="mail-item"><span class="k">{m["from"]}</span>'
        f'<span class="subj">{m["subject"]}</span>'
        f'<pre class="mail-body">{m["body"]}<br>'
        f'<a href="{m["body"].splitlines()[1]}">Open link</a></pre></div>'
        for m in mailbox.get(u, [])
    ) or '<p class="muted">No mail yet.</p>'
    return page(content_html=f"<h1>Your mailbox</h1>{items}")


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