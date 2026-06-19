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
- 12 systems cross-checked, 90% average trust, zero passwords used
- Trust database: ~/.hermes/trust.json

## Related

- [protocol-state](https://github.com/cambridgetcg/protocol-state) — the network layer
- [state-as-truth](https://github.com/cambridgetcg/state-as-truth) — STATE.md spec
- [natural-lang](https://github.com/cambridgetcg/natural-lang) — the language

---

*The truth IS the trust. No passwords. No tokens. No secrets. Just
declarations, verified against reality, remembered over time. The internet
doesn't need passwords — it needs honesty.*
