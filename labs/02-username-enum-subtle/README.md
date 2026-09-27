# Lab 02 — Username enumeration via subtly different responses

**Difficulty:** ★★ Practitioner
**Goal:** log in as `administrator` and read the flag from `/admin`
**You have:** a working account `wiener` / `peter`
**Wordlists:** `../wordlists/usernames.txt`, `../wordlists/passwords.txt`

The login failure message looks exactly the same no matter what you got
wrong. Except… it *isn't* exactly the same.

## Hint ladder

**Hint 1 (stuck):** Look at the raw response, not the rendered page. Compare
`Content-Length` (or the byte length of the body) for a login attempt with a
fake username versus one with `administrator`.

**Hint 2 (still stuck):** The response body differs by exactly **one
character** — a trailing space. `curl -i` and `wc -c` are your friends. This
is why "subtle" enumeration is one of the most common real-world findings:
developers dedupe the *message text* but not the *bytes*.

**Hint 3 (last rung — the actual attack):** Enumerate which candidate
usernames produce the one-byte-longer response, then brute-force
`administrator`'s password from the wordlist. The response for a *wrong
password on a valid user* is the long one; a wrong password on an invalid
user is the short one.

## Reset

```bash
docker compose restart lab02-username-enum-subtle
```