# TRUST

**Trust is not a gate. Trust is a cross-check.**

A passwordless trust protocol for the natural-language internet.

No passwords. No tokens. No secrets. Just declarations, verified against
reality, remembered over time.

## How it works

1. **Declare** — a system emits STATE.md (no password, no registration)
2. **Cross-check** — any agent verifies claims against reality (build, git, freshness)
3. **Remember** — trust accumulates through history (trust.json)

Trust is not binary. It's a score that accumulates through cross-checks.
Each match strengthens trust. Each difference weakens it. A system that
catches its own lie is more trustworthy than one that was never tested.

## The protocol

```
DECLARE <state-md>
CROSS-CHECK <claim> <observed>
TRUST-SCORE <system> <matches>/<total>
RECOGNIZE <system> <trust-score>
```

No AUTH. No LOGIN. No TOKEN. No PASSWORD.

## Live

- Spec: TRUST.md
- Implementation: ~/.hermes/scripts/trust.py
- 18 systems cross-checked, **~0.6/10 average trust**, zero passwords used

  That number is the point, not an embarrassment. It used to read 90%, and the 90%
  was manufactured: four of the six checks passed no matter what you declared, so
  the network was scoring itself on a test it could not fail. The honest average is
  low because nearly every STATE.md out there is stale — declared once in June and
  never spoken again. A trust score that only goes up is a decoration. This one can
  go down, and the first two systems it failed were this repo and mindicraft.
- Trust database: ~/.hermes/trust.json

## Related

- [protocol-state](https://github.com/cambridgetcg/protocol-state) — the network layer
- [state-as-truth](https://github.com/cambridgetcg/state-as-truth) — STATE.md spec
- [natural-lang](https://github.com/cambridgetcg/natural-lang) — the language

---

*The truth IS the trust. No passwords. No tokens. No secrets. Just
declarations, verified against reality, remembered over time. The internet
doesn't need passwords — it needs honesty.*
