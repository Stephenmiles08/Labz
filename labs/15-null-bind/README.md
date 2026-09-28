# Lab 15 — Null bind

**Difficulty:** ★★ Practitioner
**Goal:** read the flag from `/admin`
**You have:** a working account `wiener` / `peter`

The login talks to a directory service (LDAP-style). LDAP has a quirk:
a bind request with NO credentials is an *anonymous* bind — and this
application's handler grants the anonymous bind the directory's default
privileges.

## Hint ladder

**Hint 1 (stuck):** The login form submits `username` and `password`
fields. What happens if the request carries **neither** field? Send a POST
to `/login` with an empty body (no `-d` data at all).

**Hint 2 (still stuck):** The handler distinguishes "fields present but
wrong" from "fields absent". Absent → it performs a bind with no
identity — and this directory maps that to the administrator. Failing
closed is not what happened here.

**Hint 3 (last rung — the actual attack):**
```bash
curl -s -c jar -X POST http://127.0.0.1:8115/login
curl -s -b jar http://127.0.0.1:8115/admin
```

## Reset

```bash
docker compose restart lab15-null-bind
```