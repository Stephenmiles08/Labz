#!/usr/bin/env python3
"""
Lab 11 — Password reset poisoning via middleware

The password-reset email's link is built from a hostname the CLIENT can
control (X-Forwarded-Host, as if from a misconfigured proxy). Point it at a
host you control and the reset token rides the poisoned link off the
premises. The app's simulated "victim click" logs the token to your
webhook inbox — exactly what your real webhook would have received.

Offline stand-in: GET /webhook IS your attacker server.
"""
import secrets
import time

from flask import Flask, redirect, render_template, request, session

app = Flask(__name__)
app.secret_key = "lab11-not-the-vulnerability"

USERS = [
    ("wiener", "peter"),
    ("carlos", "montoya"),
    ("administrator", "sunshine"),
]
# process-level user store — password resets MUST persist across requests
users = dict(USERS)

tokens = {}            # token -> recipient
mailbox = {}           # username -> mail list
webhook = []           # the attacker's "server" log: poisoned-click receipts

FLAG = "FLAG{11-reset-link-built-from-untrusted-host}"

ACCENT = "#c084fc"
HERO = "Secure sign-in for employees and administrators."
FOOTNOTE = "Protected by the SecureBank authentication gateway."
DESC = ("Reminder: the reset email's link should always point back to the "
        "site — but the hostname in it may be taken from a header any "
        "client can set. Point it at your own host and watch the token "
        "arrive. wiener / peter is your demo account.")

WL_USER = "wordlists/usernames-11.txt"
WL_PASS = "wordlists/passwords-11.txt"


def _wl_count(name):
    try:
        with open(f"/app/static/{name}", "rb") as f:
            return sum(1 for _ in f)
    except OSError:
        return 0


def page(user=None, error=None, flag=None, content_html=None):
    return render_template(
        "base.html",
        title="Lab 11 · Password reset poisoning via middleware",
        accent=ACCENT,
        hero=HERO,
        footnote=FOOTNOTE,
        lab="Lab 11 — Password reset poisoning via middleware",
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
        if tok:
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

    tok = request.form.get("token")
    if tok:
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

    # VULN: the link host comes from the request, not from an allowed list
    # of origins. A misconfigured proxy passes X-Forwarded-Host through.
    xfh = request.headers.get("X-Forwarded-Host")
    host = xfh or request.headers.get("Host", "securebank.local")
    link = f"http://{host}/forgot-password?token={tok}"

    poisoned = xfh is not None
    mailbox.setdefault(who, []).append({
        "from": "SecureBank Security <no-reply@securebank.local>",
        "subject": "Password reset request",
        "body": f"Click here to reset your password:\n{link}",
    })
    if poisoned:
        # stand-in for the real victim browser: the poisoned click reports
        # to the attacker's host — here, your /webhook inbox
        webhook.append({
            "time": time.strftime("%H:%M:%S"),
            "target": host,
            "recipient": who,
            "token": tok,
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
        f'<pre class="mail-body">{m["body"]}</pre></div>'
        for m in mailbox.get(u, [])
    ) or '<p class="muted">No mail yet.</p>'
    return page(content_html=f"<h1>Your mailbox</h1>{items}")


@app.get("/webhook")
def webhook_view():
    # your attacker server: every poisoned reset link reports here
    rows = "".join(
        f'<tr><td>{w["time"]}</td><td><code>{w["target"]}</code></td>'
        f'<td>{w["recipient"]}</td><td><code class="code">{w["token"]}</code></td></tr>'
        for w in webhook
    ) or '<tr><td colspan="4" class="muted">No hits yet. Poison a reset link.</td></tr>'
    html = f"""
    <h1>Webhook inbox <span class="chip">attacker server</span></h1>
    <p class="muted">Anything that clicked a poisoned reset link reports here (offline stand-in).</p>
    <table class="wtable"><thead><tr><th>time</th><th>target host</th><th>recipient</th><th>token</th></tr></thead>
    <tbody>{rows}</tbody></table>"""
    return page(content_html=html)


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