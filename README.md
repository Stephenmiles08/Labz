# Authentication Lab Suite — Password-Based Login

A self-contained set of deliberately vulnerable web applications for learning
how password-based login mechanisms break. Every lab runs locally in Docker —
no internet, no hosted platform, no account needed. The Docker build itself
is fully offline too: all Python dependencies are vendored as wheels.

Derived from the PortSwigger Web Security Academy "Authentication" topic
(username enumeration & brute-force families) and the PentesterLab
`authe-*` exercise series.

## Quick start

```bash
docker network create --driver bridge --subnet 10.10.0.0/24 --gateway 10.10.0.1 lab_net   # once per host
docker compose up -d --build     # build + start all six labs
docker compose ps                # check they are up
```

Labs join the external `lab_net` bridge with fixed addresses
**10.10.0.50 – 10.10.0.55** (lab01 → lab06). The network must exist before
`compose up` (that one create command above — re-run it on a fresh host).

Each lab is a small Flask app. There is **no database to manage** — state
lives in memory and is re-seeded whenever the container starts, so:

```bash
docker compose restart lab04-bruteforce-ip-block   # reset one lab
docker compose down && docker compose up -d        # reset everything
```

## The labs

| # | Service | Port | Lab | Difficulty |
|---|---------|------|-----|------------|
| 01 | `lab01-username-enum-different` | 8101 | Username enumeration via different responses | ★ |
| 02 | `lab02-username-enum-subtle` | 8102 | Username enumeration via subtly different responses | ★★ |
| 03 | `lab03-username-enum-timing` | 8103 | Username enumeration via response timing | ★★ |
| 04 | `lab04-bruteforce-ip-block` | 8104 | Broken brute-force protection, IP block | ★★ |
| 05 | `lab05-username-enum-account-lock` | 8105 | Username enumeration via account lock | ★★ |
| 06 | `lab06-bruteforce-multi-credential` | 8106 | Broken brute-force protection, multiple credentials per request | ★★★ |
| 07 | `lab07-2fa-simple-bypass` | 8107 | 2FA simple bypass | ★ |
| 08 | `lab08-2fa-broken-logic` | 8108 | 2FA broken logic | ★★ |
| 09 | `lab09-2fa-brute-force` | 8109 | 2FA bypass using a brute-force attack | ★★★ |
| 10 | `lab10-password-reset-broken-logic` | 8110 | Password reset broken logic | ★ |
| 11 | `lab11-password-reset-poisoning` | 8111 | Password reset poisoning via middleware | ★★ |

## Playing

- Every lab has the same setup: you also hold a normal account
  `wiener` / `peter`, and the goal is to **log in as `administrator`** and
  read the flag from `/admin`. Each lab has its own flag.
- The labs bind to **loopback only** (`127.0.0.1:8101–8111`) plus the
  Tailscale node address (`100.99.154.48:8101–8111`) when the host is on a
  tailnet — nothing listens on the LAN or docker bridges.
- `wordlists/` in this repo contains **starter hints** (a short candidate list)
  — plus, **every lab page offers its own downloadable full wordlists**
  (`usernames.txt` / `passwords.txt`, 1,000–5,000 lines each, with the real
  entries randomly placed). Click the pill links under the login card.
- Each lab directory has its own `README.md` with a **three-rung hint
  ladder**: read rung 1 only if you are stuck, rung 2 if you are still
  stuck, and rung 3 only after a real attempt.
- Suggested tooling: curl, Burp Suite Community Edition, or Postman. For the
  timing lab you will want `time` / timing stats rather than eyeballing it.

## Rules of the exercise

1. The flag is the deliverable — show the flag string to your instructor
   (or submit it wherever your course says).
2. These apps are intended to be broken — on purpose. Do not run this stack
   on a machine you care about; it binds to `localhost` ports 8101–8111.
3. Restart any lab (`docker compose restart <service>`) to get a clean state
   — e.g. after you lock an account, trip the IP block, or burn a reset
   token.

## How each lab maps to the real world

The mechanics mirror the real PortSwigger Academy labs. After solving a lab,
re-read `labs/0X-*/app.py` (the `# VULN` comments name the flaw and the fix)
and then try the same technique against the corresponding real Academy lab —
the skill transfers directly.