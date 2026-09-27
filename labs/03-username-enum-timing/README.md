# Lab 03 — Username enumeration via response timing

**Difficulty:** ★★ Practitioner
**Goal:** log in as `administrator` and read the flag from `/admin`
**You have:** a working account `wiener` / `peter`
**Wordlists:** `../wordlists/usernames.txt`, `../wordlists/passwords.txt`

The error message gives nothing away — the *clock* does.

## Hint ladder

**Hint 1 (stuck):** Time the login requests. Send a wrong password for a
fake username, then for `administrator`, and compare response times with
`curl -w '%{time_total}'` or Burp's response-time column.

**Hint 2 (still stuck):** When the account exists, the server does the
expensive credential verification work (a password hash comparison — here
simulated with a delay). When the account does not exist, it short-circuits
and answers immediately. Which way round do you think it goes?

**Hint 3 (last rung — the actual attack):** Confirmed users take ~0.6 s
longer. Enumerate usernames on timing, then brute-force the password on the
confirm-valid `administrator` account. There is no lockout here — time each
candidate or fire them in one loop and watch for the redirect on success.

## Reset

```bash
docker compose restart lab03-username-enum-timing
```