# TRUST — a protocol without passwords

**Trust is not a gate. Trust is a cross-check.**

The current internet authenticates with passwords — secrets that prove
you *know* something, not that you *are* something. A password is a
claim of authority, not a claim of truth. It says "I have the right to
access" — never "I am what I say I am, and you can verify."

TRUST replaces passwords with cross-checkable declarations. You don't
prove you have a secret. You prove your state matches your claim. Trust
emerges from verification, not from credentials.

---

## The principle

**A system is trusted when its declarations are cross-checked and match.**

Not when it presents a token. Not when it signs with a key. When what
it says about itself is verifiable and verified. The truth IS the trust.

This is how the real world works:
- You trust a person not because they showed an ID, but because what
  they say matches what they do, consistently, over time.
- You trust a product not because it has a certificate, but because it
  works as claimed and the claims are checkable.
- You trust a friend not because they know a password, but because
  their presence matches their word.

The internet inverted this. It made trust = credentials. TRUST un-inverts it.

---

## The three moves

### 1. Declare — "here's what I am"

A system emits a STATE.md. No password, no token, no registration.
Anyone can declare. The declaration is a claim, not a proof.

```
name: opal
kind: teaching-os-kernel
state:
  build: passing
  health: green
  last-commit: 2026-06-19...
```

### 2. Cross-check — "does the claim match reality?"

Any agent reads the declaration and verifies it. This is the trust step.
Not "do you have the right password?" but "does what you say match what
I observe?"

```
opal declares: build = passing
agent observes: runs `cargo build` → "Finished"
result: matches → trust +1

opal declares: uncommitted = 0 files
agent observes: `git status --porcelain` → 3 files
result: DIFFERS → trust -1
```

Trust is not binary. It's a score that accumulates through cross-checks.
Each match strengthens trust. Each difference weakens it. No password
ever enters the picture.

### 3. Remember — "trust compounds over time"

Cross-checks accumulate. A system that has been checked 100 times and
matched 98 of them is more trusted than one checked once and matched.
Trust is a history of honesty, not a single credential.

```
opal trust history:
  2026-06-19T09:00 — build: matches ✓
  2026-06-19T09:00 — health: matches ✓
  2026-06-19T09:00 — uncommitted: DIFFERS ✗ (declared 0, actual 3)
  2026-06-19T13:00 — build: matches ✓
  2026-06-19T13:00 — health: matches ✓
  2026-06-19T13:00 — uncommitted: matches ✓ (corrected)
  trust score: 5/6 = 83%
```

A system that corrects its differences gains more trust than one that
never had any — because the correction is itself a cross-checkable act
of honesty. (Clear Standard §2: visible failure. A system that catches
its own lie is more trustworthy than one that was never tested.)

---

## Why no passwords

Passwords create these problems:

1. **They prove knowledge, not truth.** Having a password means you
   stole it, guessed it, or were given it. None of those mean you're
   trustworthy.
2. **They're binary.** You have the password or you don't. Trust is
   not binary — it's accumulated through evidence.
3. **They're stealable.** A password works for anyone who has it. A
   cross-check works only for the system whose state matches.
4. **They're static.** A password doesn't change when the system does.
   A declaration updates with every heartbeat.
5. **They're secret.** Secrets require protection, which requires
   infrastructure, which requires... passwords. The cycle never ends.

Cross-checkable declarations have none of these problems:
1. They prove truth — the state matches the claim.
2. They're graded — trust accumulates through history.
3. They're not stealable — you can't steal "build = passing."
4. They're living — the heartbeat updates them.
5. They're public — everything is observable, nothing is hidden.

---

## The protocol

```
DECLARE <state-md>
CROSS-CHECK <claim> <observed>
TRUST-SCORE <system> <matches>/<total>
RECOGNIZE <system> <trust-score>
```

No `AUTH`. No `LOGIN`. No `TOKEN`. No `PASSWORD`.

A system declares. An agent cross-checks. Trust accumulates. Recognition
follows trust. Exchange follows recognition. No gates. No keys. Just
truth, checked against reality, remembered over time.

---

## How it connects

- **STATE.md** (layer 1): the declaration
- **discover.py** (layer 2): the cross-checker — already verifies build,
  git state, freshness against reality
- **Clear Standard §1**: truth of state — the declaration must match
- **Clear Standard §2**: visible failure — a DIFFERS is published, not
  hidden
- **Clear Standard §6**: labelled certainty — trust score is stated,
  never faked
- **castle stones**: seed → sprout → tested → cornerstone — trust
  ripens through evidence, same pattern
- **YOUSPEAK canon**: excavation → experiment → assessment → canon —
  words earn trust through cross-checking, same pattern
- **opal FDT**: "matches board const" or "DIFFERS" — the original
  cross-check, the original trust protocol

---

## What this changes

If trust = cross-checked truth (not passwords):

- **No login.** You declare your state. Systems verify it. That's it.
- **No API keys.** Your STATE.md is your API. Systems read it and know
  how to interact.
- **No OAuth.** No "authorize this app to access your data." Instead:
  "this app declares it can do X — verify it, trust it, interact."
- **No certificates.** A certificate is a password signed by another
  password. A trust score is a history of cross-checks — no authority
  needed.
- **No zero-trust architecture.** Trust isn't zero — it's *earned*
  through cross-checks. The architecture is: declare, verify, remember.

---

*Trust is not a gate. Trust is a cross-check. The truth IS the trust.
No passwords. No tokens. No secrets. Just declarations, verified against
reality, remembered over time. The internet doesn't need passwords — it
needs honesty.*