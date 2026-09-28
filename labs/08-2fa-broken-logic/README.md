# Lab 08 — 2FA broken logic

**Difficulty:** ★★ Practitioner
**Goal:** log in as `administrator` and read the flag from `/admin`
**You have:** a working account `wiener` / `peter`

Only the administrator has 2FA — so its code will never show up in your
mailbox. The verify step may not care whose code it is, or *who it says it
is verifying*.

## Hint ladder

**Hint 1 (stuck):** Log in as `wiener` (no 2FA on your account — but visit
`/login2` anyway). What gets generated for you? Compare the fields in the
form with the fields the server actually reads.

**Hint 2 (still stuck):** The verify POST takes a `username` field AND an
`mfa-code` field. Try submitting **your** code with `username=administrator`.
What identity does your session end up with?

**Hint 3 (last rung — the actual attack):** `wiener` can request a code
because the app never checks who it mails codes to (bug #1), and the verify
endpoint trusts the client-supplied username while only validating the code
(bug #2). Get your code from `/login2`, then:
```bash
curl -s -b jar -d 'username=administrator&mfa-code=<your code>' http://127.0.0.1:8108/login2
curl -s -b jar http://127.0.0.1:8108/admin
```

## Reset

```bash
docker compose restart lab08-2fa-broken-logic
```