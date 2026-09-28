# Lab 07 — 2FA simple bypass

**Difficulty:** ★ Apprentice
**Goal:** log in as `administrator` and read the flag from `/admin`
**You have:** a working account `wiener` / `peter`
**You can find:** the administrator's password in the downloadable list

The administrator's account is protected by two-factor authentication. On
one page. Maybe.

## Hint ladder

**Hint 1 (stuck):** Log in as `administrator` (password from the wordlist).
The app bounces you to `/login2` for a code. Now — what happens if you send
requests to *other* pages while that code is still pending? Try `/admin`
directly. No redirect, no code entry.

**Hint 2 (still stuck):** The 2FA check exists, but it was only attached to
the 2FA page itself. The session cookie already says who you are — every
other route trusts it without asking whether the code was ever entered.

**Hint 3 (last rung — the actual attack):**
```bash
curl -s -c jar -d 'username=administrator&password=<from wordlist>' http://127.0.0.1:8107/login
curl -s -b jar http://127.0.0.1:8107/admin     # never visit /login2
```
The moment your credentials are accepted, the flag is one GET away.

## Reset

```bash
docker compose restart lab07-2fa-simple-bypass
```