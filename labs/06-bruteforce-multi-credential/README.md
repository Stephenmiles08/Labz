# Lab 06 — Broken brute-force protection, multiple credentials per request

**Difficulty:** ★★★ Expert
**Goal:** log in as `administrator` and read the flag from `/admin`
**You have:** a working account `wiener` / `peter`
**Wordlists:** `../wordlists/usernames.txt`, `../wordlists/passwords.txt`

The login endpoint looks like a normal web form… but it also speaks JSON.
What if "one attempt" could be *many attempts*?

## Hint ladder

**Hint 1 (stuck):** Talk to the endpoint the way an API client would —
`Content-Type: application/json` with `{"username": "...", "password":
"..."}`. What does it answer for a wrong password? What *types* does it
accept for the password field?

**Hint 2 (still stuck):** The form page mentions JSON explicitly. Send the
password as a **list**: `{"username":"administrator",
"password":["123456","password","qwerty"]}`. Watch what happens when one of
those entries is right.

**Hint 3 (last rung — the actual attack):** Send the entire password
wordlist as the JSON array in a single request. If any entry matches, the
server logs you in — and no rate limiter, lockout, or IP block ever fires,
because from the server's perspective there was never more than one
"attempt". Grab the session cookie from the response and take it to `/admin`.

## Reset

```bash
docker compose restart lab06-bruteforce-multi-credential
```