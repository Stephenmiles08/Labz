# Lab 12 — Auth cookie trust

**Difficulty:** ★ Beginner
**Goal:** read the flag from `/admin`
**You have:** a working account `wiener` / `peter`

This app has no server-side sessions. Your identity is a cookie called
`auth`, and the server reads it back and believes it.

## Hint ladder

**Hint 1 (stuck):** Log in as `wiener` and inspect the cookies the browser
received (DevTools → Application → Cookies). What does the `auth` cookie
contain? Now change its value to `administrator` and reload `/admin`.

**Hint 2 (still stuck):** The cookie contains only the username — no
signature, no expiry, no session id. The server never checks who issued it;
it takes the value at face value.

**Hint 3 (last rung — the actual attack):**
```bash
curl -s -H 'Cookie: auth=administrator' http://127.0.0.1:8112/admin
```
That is the whole exploit. No login required.

## Reset

```bash
docker compose restart lab12-auth-cookie-trust
```