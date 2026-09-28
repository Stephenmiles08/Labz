# Lab 16 — LDAP filter injection

**Difficulty:** ★★★ Expert
**Goal:** read the flag from `/admin`
**You have:** a working account `wiener` / `peter`

The login builds a directory filter from your username:
`(&(uid=<username>)(userPassword=<password>))`. The value you supply is
treated as data… until it contains filter syntax of its own. In LDAP, `*`
is a wildcard — widen the filter and the password clause stops mattering.

## Hint ladder

**Hint 1 (stuck):** Where does your username end up in the login logic?
What is the filter built from it? What does a `*` mean inside an LDAP
filter value?

**Hint 2 (still stuck):** Submitting `*` as the username makes the `uid`
clause match the whole directory. The evaluator resolves the match set and
returns its most privileged entry. You don't need a password at all.

**Hint 3 (last rung — the actual attack):**
```bash
curl -s -c jar -d 'username=*&password=anything' http://127.0.0.1:8116/login
curl -s -b jar http://127.0.0.1:8116/admin
```
In a real LDAP setup the classic payload is `*)(cn=*))%00` — closes the
filter, ANDs an always-true clause, and null-terminates the rest (the
password check). This lab's evaluator accepts the wildcard form of the
same idea.

## Reset

```bash
docker compose restart lab16-ldap-filter-injection
```