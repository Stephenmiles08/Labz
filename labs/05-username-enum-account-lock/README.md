# Lab 05 — Username enumeration via account lock

**Difficulty:** ★★ Practitioner
**Goal:** log in as `administrator` and read the flag from `/admin`
**You have:** a working account `wiener` / `peter`
**Wordlists:** `../wordlists/usernames.txt`, `../wordlists/passwords.txt`

An automated lockout system kicks in after three failed attempts. Can you
make the protective mechanism work *for* you?

## Hint ladder

**Hint 1 (stuck):** Send three wrong passwords for a fake username, then
three wrong passwords for `administrator`. Compare the third responses.

**Hint 2 (still stuck):** The lock only fires for accounts that exist — so
the lockout *message* is the username oracle. And once you have found the
real username, try the password wordlist anyway: does the lock actually
stop the *correct* password from being accepted?

**Hint 3 (last rung — the actual attack):** Enumerate with the "Account
locked" message, then brute force `administrator` past the lockout — a
correct password still logs you in while the account is locked (the app
checks the password first and only reports the lock for *failed* attempts).
Bonus: you now know exactly why "lock after N tries" must lock *after*
verification, not before it.

## Reset

```bash
docker compose restart lab05-username-enum-account-lock
```