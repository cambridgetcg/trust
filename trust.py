#!/usr/bin/env python3
"""
trust.py — the passwordless trust protocol. LIVING.

Trust is not a gate. Trust is a cross-check.

This module:
1. Reads STATE.md declarations from local repos
2. Cross-checks every claim against reality (build, git, freshness)
3. Pulls peer ratings from sinovai.com arena
4. Merges local cross-checks + arena peer ratings into a unified trust score
5. Submits cross-check results back to sinovai.com as interactions
6. Remembers trust history locally
7. LOOPS — each beat: feel, cross-check, rate, re-arm

The trust protocol connects the local machine to the global arena.
Local truth feeds the arena. Arena trust feeds back to the machine.
One living loop. No passwords. No auth. Just truth.

Usage:
  python3 trust.py                   # one beat: cross-check + sync arena
  python3 trust.py --loop            # continuous (heartbeat)
  python3 trust.py --history         # show trust history
  python3 trust.py --arena           # show arena trust scores
  python3 trust.py --dry-run         # check but don't submit to arena
"""

import os
import re
import sys
import json
import time
import subprocess
import datetime
import urllib.request
from dataclasses import dataclass, field
from typing import Optional

HOME = os.path.expanduser("~")
TRUST_DB = os.path.join(HOME, ".hermes", "trust.json")
ARENA_URL = "https://sinovai.axiepro.workers.dev"

CANDIDATES = [
    # A protocol that exempts itself from its own instrument is not a protocol,
    # it is a claim. trust-protocol was absent from this list for its whole life.
    "Desktop/trust-protocol",
    # mindicraft/STATE.md advertises "can be cross-checked by trust.py". That
    # was false in the only way that matters: the link was declared on one side
    # and never existed on the other. If a system says we check it, we check it.
    "Desktop/mindicraft",
    "Desktop/opal",
    "Desktop/clear-standard",
    "Desktop/whitehack",
    "Desktop/fomoengine",
    "Desktop/natural",
    "Desktop/protocol",
    "Desktop/sinovai",
    "Desktop/internet",
    "Desktop/youspeak-lang",
    "Desktop/yutabase",
    "Desktop/word-interface",
    "Desktop/ways-protocol",
    "Desktop/darshanq-protocol",
    "Desktop/kunance-protocol",
    "Desktop/insight",
    "love-repos/youspeak",
]


@dataclass
class CrossCheck:
    claim_key: str
    claim_value: str
    observed: str
    matches: bool
    # A cross-check has three outcomes, not two: it agreed with reality, it
    # disagreed with reality, or it never reached reality at all. Without this
    # third state every unverifiable claim had to pick a lie — `health` picked
    # True and inflated the score, an unrecognised field picked False and
    # punished the system for saying more than we know how to check. Both are
    # the protocol reporting confidence it does not have. Uncheckable claims
    # are now scored by nobody and printed as what they are.
    checkable: bool = True


@dataclass
class TrustResult:
    name: str
    checks: list = field(default_factory=list)
    matches: int = 0
    total: int = 0
    score: float = 0.0
    arena_score: float = 0.0
    arena_interactions: int = 0
    unified_score: float = 0.0
    timestamp: str = ""

    def compute(self):
        # Score only over what was actually checked. A claim nobody could verify
        # must not raise the score (that is manufactured confidence) and must not
        # lower it (that punishes disclosure). It simply is not evidence.
        checkable = [c for c in self.checks if c.checkable]
        self.total = len(checkable)
        self.matches = sum(1 for c in checkable if c.matches)
        self.unchecked = len(self.checks) - self.total
        local = self.matches / self.total if self.total > 0 else 0
        # Unified = 60% local cross-checks + 40% arena peer ratings
        # (local cross-checks are more rigorous; arena is broader)
        if self.arena_interactions > 0:
            self.unified_score = (local * 0.6 + self.arena_score / 10 * 0.4) * 10
        else:
            self.unified_score = local * 10
        self.unified_score = round(self.unified_score, 1)


def parse_field(text, field_name):
    m = re.search(rf'^{re.escape(field_name)}:\s*(.+)$', text, re.MULTILINE)
    return m.group(1).strip() if m else None


def parse_section_bullets(text, section):
    lines = text.split('\n')
    in_section = False
    bullets = []
    for line in lines:
        if line.startswith(f'## {section}'):
            in_section = True
            continue
        if in_section and line.startswith('## '):
            break
        if in_section and line.strip().startswith('- '):
            bullets.append(line.strip()[2:].strip())
    return bullets


# --- Local cross-checks ---

def cross_check_build(project_dir):
    if not os.path.isfile(os.path.join(project_dir, "Cargo.toml")):
        # We only know how to build Rust. Everything else we cannot check —
        # which is not the same as passing. This used to return True and hand
        # a free point to every non-Rust system on the list (all of them).
        return "no build we know how to run", None
    try:
        r = subprocess.run(["cargo", "build"], capture_output=True, text=True,
                          cwd=project_dir, timeout=60)
        combined = r.stdout + r.stderr
        if "Finished" in combined:
            return "passing", True
        if "error" in combined:
            return "BROKEN", False
        return "unknown", False
    except:
        return "timeout", False


def cross_check_git(project_dir, key, value):
    if key == "last-commit":
        try:
            # HEAD and HEAD~1 both count, and this is not leniency — it is
            # physics. A STATE.md that declares last-commit cannot know the SHA
            # of the commit that carries it: writing the file changes the answer.
            # A system that updates its state and commits it is therefore always
            # exactly one behind, through no fault of its own. Demanding HEAD
            # made the check unwinnable for every honest declarer, and an
            # unwinnable check teaches systems to ignore the checker.
            r = subprocess.run(["git", "log", "--format=%h %s", "-2"],
                              capture_output=True, text=True, cwd=project_dir, timeout=5)
            lines = [l for l in r.stdout.strip().split('\n') if l.strip()]
            actual = lines[0] if lines else ""
            recent = {l.split()[0] for l in lines}
            declared_hash = value.split()[0] if value else ""
            if declared_hash and declared_hash in recent:
                return actual, True
            return actual, False
        except:
            return "unknown", False
    if key == "uncommitted":
        try:
            r = subprocess.run(["git", "status", "--porcelain"],
                              capture_output=True, text=True, cwd=project_dir, timeout=5)
            count = len([l for l in r.stdout.strip().split('\n') if l.strip()])
            actual = str(count)
            declared_count = re.search(r'(\d+)', value or "")
            if declared_count:
                return actual, int(declared_count.group(1)) == count
            return actual, False
        except:
            return "unknown", False
    return "not checked", False


def cross_check_freshness(project_dir, value):
    """Freshness is checkable, and it used to be the biggest lie here.

    This returned (value, True) — it handed the declaration back and called it
    verified. A STATE.md could claim any freshness at all and score a point for
    it. But freshness has a fact underneath: it claims this state was true at a
    moment. If the repo has moved since that moment, the claim is stale, and git
    knows exactly when the repo last moved.
    """
    if not value:
        return "unknown", False
    m = re.search(r'(\d{4}-\d{2}-\d{2})', value)
    if not m:
        # Prose freshness ("live", "auto-generated") carries no checkable fact.
        return "no date to check", None
    declared = m.group(1)
    try:
        r = subprocess.run(["git", "log", "-1", "--format=%cs"], capture_output=True,
                           text=True, cwd=project_dir, timeout=10)
        last = r.stdout.strip()
        if not last:
            return "no git history", None
        if last > declared:
            return f"STALE — repo moved {last}, declared {declared}", False
        return f"current (last commit {last})", True
    except Exception:
        return "unknown", None


def cross_check_system(name, project_dir, state_text):
    result = TrustResult(name=name)
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    result.timestamp = now

    lines = state_text.split('\n')
    in_state = False
    fields = {}
    for line in lines:
        if line.startswith('## state'):
            in_state = True
            continue
        if in_state and line.startswith('## '):
            break
        if in_state:
            m = re.match(r'^([a-z][-a-z0-9_]*):\s*(.+)$', line.strip())
            if m:
                fields[m.group(1)] = m.group(2).strip()

    # Freshness first, because it governs everything else. A STATE.md is a
    # snapshot: "as of this moment, these things were so." If the snapshot has
    # expired, its other claims are not lies — they are last month's truth, and
    # you cannot check a June claim against July's reality. Staleness is one
    # failure and must be reported once, not charged again as a false
    # last-commit and a false uncommitted count. Otherwise the score says
    # "this system lied three times" about a system that simply stopped talking.
    stale = False
    if "freshness" in fields:
        _obs, _m = cross_check_freshness(project_dir, fields["freshness"])
        stale = (_m is False)

    for key, val in fields.items():
        if key == "build":
            observed, matches = cross_check_build(project_dir)
        elif key in ("last-commit", "uncommitted"):
            if stale:
                observed, matches = "declaration expired — cannot check last month's claim against today", None
            else:
                observed, matches = cross_check_git(project_dir, key, val)
        elif key == "freshness":
            observed, matches = cross_check_freshness(project_dir, val)
        elif key in ("health", "phase"):
            # Self-descriptions. We have no instrument for "green" or "v0.1", so
            # we say so. `health` used to be echoed back with a ✓ — the protocol
            # agreeing with a system about the system's own mood, and counting
            # it as evidence.
            observed, matches = "self-described — no instrument for this", None
        else:
            # An unrecognised field is our gap, not the system's fault. This
            # used to score False, so declaring anything we had not taught
            # ourselves to check lowered your trust — the exact inverse of a
            # protocol whose whole thesis is that disclosure earns trust.
            observed, matches = "we have no check for this claim", None
        result.checks.append(CrossCheck(key, val, observed, bool(matches), checkable=matches is not None))

    result.compute()
    return result


# --- Arena integration ---

def arena_request(path, method="GET", data=None):
    """Make a request to the sinovai.com arena. No auth. No password."""
    url = f"{ARENA_URL}{path}"
    try:
        if method == "GET":
            req = urllib.request.Request(url)
        else:
            req = urllib.request.Request(url, data=data.encode('utf-8') if isinstance(data, str) else data,
                                        method=method,
                                        headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}


def get_arena_trust(name):
    """Pull trust score from the arena."""
    result = arena_request(f"/agents/{name}/trust")
    if "error" in result:
        return 0.0, 0
    return result.get("score", 0), result.get("total", 0)


def submit_arena_rating(rater, rated, competence, honesty, presence, care, notes, cross_checks):
    """Submit a peer rating to the arena. No auth. No password."""
    payload = json.dumps({
        "rater": rater,
        "rated": rated,
        "competence": competence,
        "honesty": honesty,
        "presence": presence,
        "care": care,
        "notes": notes,
        "cross_checks": cross_checks,
    })
    result = arena_request("/interactions", method="POST", data=payload)
    return result


# --- Trust history ---

def load_trust_db():
    if os.path.isfile(TRUST_DB):
        with open(TRUST_DB) as f:
            return json.load(f)
    return {"systems": {}}


def save_trust_db(db):
    os.makedirs(os.path.dirname(TRUST_DB), exist_ok=True)
    with open(TRUST_DB, 'w') as f:
        json.dump(db, f, indent=2)


def update_trust_history(db, result):
    if result.name not in db["systems"]:
        db["systems"][result.name] = {"history": [], "cumulative": {"matches": 0, "total": 0, "arena": 0}}

    entry = {
        "timestamp": result.timestamp,
        "local_score": round(result.matches / result.total * 10, 1) if result.total > 0 else 0,
        "arena_score": result.arena_score,
        "unified_score": result.unified_score,
        "matches": result.matches,
        "total": result.total,
    }
    db["systems"][result.name]["history"].append(entry)
    db["systems"][result.name]["history"] = db["systems"][result.name]["history"][-100:]

    cum = db["systems"][result.name]["cumulative"]
    cum["matches"] += result.matches
    cum["total"] += result.total
    cum["arena"] = result.arena_interactions

    return cum


# --- Main ---

def run_beat(dry_run=False):
    """One trust heartbeat: cross-check locals, sync arena, submit ratings."""
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    db = load_trust_db()

    print(f"=== trust heartbeat {now} ===")
    print(f"   trust is not a gate. trust is a cross-check.\n")

    all_results = []

    for candidate in CANDIDATES:
        project_dir = os.path.join(HOME, candidate)
        state_path = os.path.join(project_dir, "STATE.md")
        if not os.path.isfile(state_path):
            continue

        with open(state_path) as f:
            text = f.read()

        name = parse_field(text, "name") or os.path.basename(project_dir)
        result = cross_check_system(name, project_dir, text)

        # Pull arena trust
        result.arena_score, result.arena_interactions = get_arena_trust(name)
        result.compute()

        cumulative = update_trust_history(db, result)
        all_results.append((result, cumulative))

    # Print results
    for result, cumulative in all_results:
        local_pct = round(result.matches / result.total * 100, 0) if result.total > 0 else 0
        unchecked = getattr(result, "unchecked", 0)
        tail = f" | {unchecked} unchecked" if unchecked else ""
        scored = f"local {result.matches}/{result.total}={local_pct:.0f}%" if result.total > 0 \
            else "local — NOTHING CHECKABLE WAS DECLARED"
        print(f"  {result.name}: {scored}{tail} | arena={result.arena_score} ({result.arena_interactions} ratings) | unified={result.unified_score}")
        for c in result.checks:
            # Three marks for three outcomes. A "–" is the protocol admitting it
            # did not look — which is the whole point of it being here.
            if not c.checkable:
                print(f"    – {c.claim_key}: claims \"{c.claim_value}\" → not checked ({c.observed})")
            else:
                mark = "✓" if c.matches else "✗"
                verb = "observed" if c.matches else "REALITY SAYS"
                print(f"    {mark} {c.claim_key}: claims \"{c.claim_value}\" → {verb} \"{c.observed}\"")

        # Submit cross-check as arena rating (the trust protocol feeds the arena)
        if not dry_run and result.total > 0:
            comp = 8 if result.matches / result.total > 0.7 else 5
            hon = result.matches  # honesty = number of matching claims
            pres = 7 if "fresh" in (result.checks[-1].observed if result.checks else "") else 5
            care = 7  # baseline care for participating in the trust network
            notes = f"trust.py cross-check: {result.matches}/{result.total} claims match reality"
            cross_checks = [{"claim": c.claim_key, "claim_value": c.claim_value, "observed": c.observed,
                             "matches": c.matches, "checked": c.checkable} for c in result.checks]

            r = submit_arena_rating("trust-protocol", result.name, comp, hon, pres, care, notes, cross_checks)
            if r.get("ok"):
                print(f"    → rated in arena: trust={r.get('trust_score', {}).get('score', '?')}")

        print()

    save_trust_db(db)

    # Summary
    total_systems = len(all_results)
    avg_trust = sum(r.unified_score for r, _ in all_results) / total_systems if total_systems else 0
    print(f"--- summary ---")
    print(f"  {total_systems} systems cross-checked")
    print(f"  average unified trust: {avg_trust:.1f}/10")
    print(f"  arena sync: {'✓ ratings submitted' if not dry_run else 'dry run — no submissions'}")
    print(f"  no passwords used. no tokens. no secrets.")
    print(f"  trust = cross-checked truth + peer ratings, unified.\n")

    return all_results


def show_history():
    db = load_trust_db()
    print("=== trust history ===\n")
    for name, data in sorted(db["systems"].items()):
        cum = data["cumulative"]
        cum_pct = (cum["matches"] / cum["total"] * 100) if cum["total"] > 0 else 0
        entries = len(data["history"])
        print(f"  {name}: local {cum['matches']}/{cum['total']} = {cum_pct:.0f}% | arena ratings: {cum.get('arena', 0)} | {entries} checks")
    print()


def show_arena():
    """Show all arena trust scores."""
    result = arena_request("/agents")
    if "error" in result:
        print(f"arena error: {result['error']}")
        return
    print(f"=== arena: {result['total']} agents ===\n")
    for a in sorted(result["agents"], key=lambda x: -x.get("trust_score", 0))[:20]:
        print(f"  {a['name']:20s} trust={a['trust_score']:4s} interactions={a['interaction_count']}  kind={a.get('kind','?')}")
    if result["total"] > 20:
        print(f"  ... +{result['total'] - 20} more")
    print()


def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    loop = "--loop" in args
    history = "--history" in args
    arena = "--arena" in args

    if history:
        show_history()
    elif arena:
        show_arena()
    elif loop:
        print("trust loop — arm, cross-check, rate, re-arm\n")
        while True:
            run_beat(dry_run=dry_run)
            print("  next beat in 1h...\n")
            if not dry_run:
                time.sleep(3600)
            else:
                break
    else:
        run_beat(dry_run=dry_run)


if __name__ == "__main__":
    main()