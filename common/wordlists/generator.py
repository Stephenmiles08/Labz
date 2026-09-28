#!/usr/bin/env python3
"""
Student-lab wordlist generator (build-time).

For each lab, creates two downloadable wordlists in the image:
  /app/static/wordlists/usernames-NN.txt   (candidate usernames)
  /app/static/wordlists/passwords-NN.txt   (candidate passwords)

Rules:
  - line counts land in the 1,000-5,000 range (per-lab sizes below)
  - the lab's REAL entries (valid usernames; the administrator's password
    plus the two demo accounts' passwords) are injected at RANDOM positions
  - seeding is fixed per lab, so rebuilds of the same lab ship the same
    list (students can resume a brute-force run across recreates)
  - bare lists, one entry per line, no comments
"""
import argparse
import os
import random

LAB_USER_SIZES = {1: 2000, 2: 1500, 3: 2500, 4: 2000, 5: 2200, 6: 1500,
                   7: 1800, 8: 1600, 9: 2000, 10: 1200, 11: 1400}
LAB_PASS_SIZES = {1: 3000, 2: 3500, 3: 2000, 4: 4000, 5: 3500, 6: 4500,
                  7: 3200, 8: 2800, 9: 2500, 10: 1500, 11: 1600}

# the entries the labs actually accept (must ALL appear in every list)
REQUIRED_USERS = ["wiener", "carlos", "administrator"]
LAB_ADMIN_PASS = {1: "dragon", 2: "football", 3: "monkey",
                  4: "sunshine", 5: "iloveyou", 6: "gandalf",
                  7: "freedom", 8: "letmein", 9: "123456",
                  10: "freedom", 11: "sunshine"}

USER_POOL = [
    "alice", "bob", "carol", "dave", "eve", "frank", "grace", "heidi", "ivan",
    "judy", "mallory", "oscar", "peggy", "trent", "victor", "walter", "xavier",
    "yvonne", "zoe", "admin", "root", "user", "guest", "test", "demo", "dev",
    "qa", "ops", "support", "sales", "marketing", "finance", "hr", "legal",
    "it", "security", "manager", "supervisor", "director", "assistant", "clerk",
    "officer", "agent", "member", "subscriber", "customer", "client", "vendor",
    "partner", "intern", "trainee", "recruit", "analyst", "engineer", "architect",
    "developer", "designer", "tester", "writer", "editor", "publisher", "blogger",
    "founder", "owner", "ceo", "cto", "cfo", "cio", "coo", "vp", "lead", "chief",
    "dana", "erin", "felix", "gina", "harry", "iris", "jack", "kate", "liam",
    "maya", "nina", "oliver", "piper", "quinn", "rose", "sam", "tara", "uma",
    "vince", "wendy", "yusuf", "zara", "ahmed", "chen", "dmitri", "emre", "fatima",
    "giovanni", "hans", "ines", "juan", "karl", "ling", "marco", "natalia", "omar",
    "pierre", "qiang", "raoul", "sophie", "tomas", "ursula", "viktor", "wei",
    "xia", "yun", "zelda", "arthur", "bruno", "celine", "diego", "elena", "farid",
    "georg", "hassan", "ida", "jonas", "klaus", "laura", "miguel", "nadia",
    "olaf", "paulo", "qadir", "rebecca", "stefan", "tina", "ulrich", "valerie",
    "werner", "xin", "yuan", "zulma", "angela", "boris", "chloe", "daniela",
    "emil", "fiona", "gabriel", "hanna", "isabel", "jorge", "katarina", "leandro",
    "marta", "nicolas", "otilia", "polina", "roberto", "silvia", "teo", "uliana",
]

PASS_POOL = [
    "123456", "password", "12345678", "qwerty", "123456789", "12345", "1234",
    "111111", "1234567", "dragon", "123123", "baseball", "abc123", "football",
    "monkey", "letmein", "shadow", "master", "666666", "qwertyuiop", "123321",
    "mustang", "1234567890", "michael", "654321", "pussy", "superman", "1qaz2wsx",
    "7777777", "fuckyou", "121212", "000000", "qazwsx", "123qwe", "killer",
    "trustno1", "jordan", "jennifer", "zxcvbnm", "asdfgh", "hunter", "buster",
    "soccer", "harley", "batman", "andrew", "tigger", "sunshine", "iloveyou",
    "fuckme", "2000", "charlie", "robert", "thomas", "hockey", "ranger",
    "daniel", "starwars", "klaster", "112233", "george", "asshole", "computer",
    "michelle", "jessica", "pepper", "1111", "zxcvbn", "555555", "11111111",
    "131313", "freedom", "777777", "pass", "fuck", "maggie", "159753",
    "aaaaaa", "ginger", "princess", "joshua", "cheese", "amanda", "summer",
    "love", "ashley", "696969", "nicole", "chelsea", "biteme", "matthew",
    "access", "yankees", "987654321", "dallas", "austin", "thunder", "taylor",
    "matrix", "william", "corvette", "hello", "martin", "heather", "secret",
    "fucker", "merlin", "diamond", "1234qwer", "gfhjkm", "hammer", "silver",
    "222222", "88888888", "anthony", "justin", "test", "bailey", "q1w2e3r4t5",
    "patrick", "internet", "scooter", "orange", "11111", "golfer", "cookie",
    "richard", "samantha", "bigdog", "guitar", "jackson", "whatever", "mickey",
    "chicken", "sparky", "snoopy", "maverick", "phoenix", "camaro", "sexy",
    "peanut", "morgan", "welcome", "falcon", "cowboy", "ferrari", "samsung",
    "andrea", "smokey", "steelers", "joseph", "mercedes", "dakota", "arsenal",
    "eagles", "melissa", "boomer", "booboo", "spider", "nascar", "monster",
    "tigers", "yellow", "xxxxxx", "123123123", "gateway", "marina", "diablo",
    "bulldog", "qwer1234", "compaq", "purple", "hardcore", "banana", "junior",
    "hannah", "123654", "porsche", "lakers", "iceman", "money", "cowboys",
]

# leet / case variants so the filler does not look machine-cycled
def variants(word):
    out = {word}
    tables = [
        str.maketrans({"a": "4", "e": "3", "i": "1", "o": "0", "s": "5"}),
        str.maketrans({"a": "@", "e": "3", "i": "!", "o": "0"}),
    ]
    out.add(word.capitalize())
    for t in tables:
        out.add(word.translate(t))
        out.add(word.translate(t).capitalize())
    out.add(word + "1")
    return sorted(out - {word})


def build_list(rng, size, required, pool):
    """size lines; every entry in `required` appears exactly once, at a
    random position; the rest is filler drawn from the pool (repeats of
    common junk are realistic and acceptable)."""
    assert size > len(required), "size must exceed required count"
    slots = list(range(size))
    rng.shuffle(slots)
    lines = [None] * size
    for entry in required:
        lines[slots.pop()] = entry
    filler = []
    step = rng.choice([3, 5, 7, 11, 13, 17])
    offset = rng.randrange(len(pool))
    i = 0
    while len(filler) < size - len(required):
        base = pool[(offset + i * step) % len(pool)]
        i += 1
        if rng.random() < 0.35:
            vs = variants(base)
            if vs:
                filler.append(rng.choice(vs))
                continue
        filler.append(base)
    for pos in slots:
        lines[pos] = filler.pop()
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lab", type=int, required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    rng = random.Random(f"student-labs-{args.lab}")

    required_passes = [LAB_ADMIN_PASS[args.lab]] + ["peter", "montoya"]
    pass_pool = [p for p in PASS_POOL if p not in required_passes]
    user_pool = [u for u in USER_POOL if u not in REQUIRED_USERS]

    users = build_list(rng, LAB_USER_SIZES[args.lab], REQUIRED_USERS, user_pool)
    pwds = build_list(rng, LAB_PASS_SIZES[args.lab], required_passes, pass_pool)

    os.makedirs(args.out, exist_ok=True)
    u_path = os.path.join(args.out, f"usernames-{args.lab:02d}.txt")
    p_path = os.path.join(args.out, f"passwords-{args.lab:02d}.txt")
    with open(u_path, "w") as f:
        f.write("\n".join(users) + "\n")
    with open(p_path, "w") as f:
        f.write("\n".join(pwds) + "\n")

    print(f"lab {args.lab}: {u_path} {len(users)} lines, "
          f"{p_path} {len(pwds)} lines")
    for e in REQUIRED_USERS:
        print(f"  user '{e}' at line {users.index(e) + 1}")
    for e in [LAB_ADMIN_PASS[args.lab], "peter", "montoya"]:
        print(f"  pass '{e}' at line {pwds.index(e) + 1}")


if __name__ == "__main__":
    main()