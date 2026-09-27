# Lab 04 — Broken brute-force protection, IP block

**Difficulty:** ★★ Practitioner
**Goal:** log in as `administrator` and read the flag from `/admin`
**You have:** a working account `wiener` / `peter`
**Wordlists:** `../wordlists/usernames.txt`, `../wordlists/passwords.txt`

The server locks out your IP after five failed logins. Or does it?

## Hint ladder

**Hint 1 (stuck):** Fire five wrong passwords and watch the sixth request —
even with the *correct* password you get "too many incorrect login
attempts". The block is real per IP. Now think about what a legit login
does to the counter — try one correct `wiener`/`peter` login in the middle
of your brute-force run.

**Hint 2 (still stuck):** Two independent flaws stack here. (a) How does
the app decide who the client is? Look at every header you are allowed to
send. (b) What resets the counter besides time?

**Hint 3 (last rung — the actual attack):** (a) Set a rotating
`X-Forwarded-For: <random-ip>` on every request — the app takes the client
IP from that header, so each rotation is a "new" IP with a fresh counter.
(b) Or: alternate two failed guesses with one correct `wiener`/`peter`
login — the counter resets on success, so it never reaches five. Both
paths get you to a full password brute-force on `administrator`.

## Reset

```bash
docker compose restart lab04-bruteforce-ip-block
```