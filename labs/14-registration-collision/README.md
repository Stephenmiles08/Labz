# Lab 14 — Case-insensitive login collision

**Difficulty:** ★★ Practitioner
**Goal:** read the flag from `/admin` from the `administrator` identity
**You have:** a working account `wiener` / `peter`, and a registration page

Two parts of the system disagree on what counts as the same name. The
registration check is case-sensitive; the login lookup is not. That
disagreement is an account-collision bug.

## Hint ladder

**Hint 1 (stuck):** Register a new account called `ADMINISTRATOR` (all
caps) with any password — does registration accept it? Now log in with
`ADMINISTRATOR` and *your* password. Look at who you're logged in as.

**Hint 2 (still stuck):** The login resolves names case-insensitively, so
`ADMINISTRATOR` and `administrator` are the SAME identity set. Your
registration added a credential to a set that contains the real
administrator — and the login hands out the admin role for that set.

**Hint 3 (last rung — the actual attack):**
```bash
curl -s -c jar -d 'username=ADMINISTRATOR&password=mine!' http://127.0.0.1:8114/register
curl -s -b jar -d 'username=ADMINISTRATOR&password=mine!' http://127.0.0.1:8114/login
curl -s -b jar http://127.0.0.1:8114/admin
```
(Any case variant works — `aDmInIsTrAtOr` included.)

## Reset

```bash
docker compose restart lab14-registration-collision
```