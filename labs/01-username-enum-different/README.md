# Lab 01 — Username enumeration via different responses

**Difficulty:** ★ Apprentice
**Goal:** log in as `administrator` and read the flag from `/admin`
**You have:** a working account `wiener` / `peter`
**Wordlists:** `../wordlists/usernames.txt`, `../wordlists/passwords.txt`

The login page rejects *something* differently depending on what you get
wrong — and that something is an oracle.

## Hint ladder

**Hint 1 (stuck):** Send a login with a clearly fake username, then resend
the exact same request with `administrator`. Compare the two responses —
status code *and* body text.

**Hint 2 (still stuck):** The server tells you whether the *username* is the
problem or the *password* is the problem. That means valid usernames can be
collected one request at a time. Run each candidate username through the
login form without a password.

**Hint 3 (last rung — the actual attack):** Once `administrator` is
confirmed as valid, loop the password wordlist against `administrator` until
the error message changes to a redirect / login success. There is no
lockout and no IP block on this lab — brute force freely.

## Reset

```bash
docker compose restart lab01-username-enum-different
```