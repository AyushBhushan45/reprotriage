"""ReproTriage core — deterministic, reproduction-first triage.

Design rules (non-negotiable):
- No API key required for this layer.
- Report-only by default: never auto-close, never auto-reject.
- Every check is explainable in one line. No black-box "AI slop" verdicts:
  we check *readiness* (is it linked, tested, described, reproducible?),
  never whether a human or an AI wrote it.
"""
import re
from dataclasses import dataclass, field

DEFAULT_CONFIG = {
    "min_pr_description_chars": 80,
    "max_pr_files": 30,
    "require_linked_issue": True,
    "require_tests": True,
    "labels": {"needs_info": "needs-info", "needs_repro": "needs-repro", "ready": "ready-for-review"},
}


@dataclass
class Check:
    name: str
    passed: bool
    detail: str


@dataclass
class TriageResult:
    kind: str
    score: int
    checks: list = field(default_factory=list)
    missing: list = field(default_factory=list)
    suggested_labels: list = field(default_factory=list)

    def to_markdown(self):
        lines = [
            "### ReproTriage report",
            "",
            f"**Readiness: {self.score}/100**",
            "",
            "| Check | Result | Detail |",
            "|---|---|---|",
        ]
        for c in self.checks:
            mark = "✅ Pass" if c.passed else "❌ Missing"
            lines.append(f"| {c.name} | {mark} | {c.detail} |")
        if self.missing:
            lines += ["", "**To help maintainers review this faster, please add:**"]
            lines += [f"- {m}" for m in self.missing]
        lines += [
            "",
            "---",
            "_ReproTriage is report-only: nothing was auto-closed or auto-rejected. "
            "A maintainer makes the final call._",
        ]
        return "\n".join(lines)


ISSUE_SECTIONS = [
    ("Reproduction steps", [r"steps to reproduce", r"reproduc", r"how to reproduce"],
     "Clear steps to reproduce the problem"),
    ("Expected behaviour", [r"expected"], "What you expected to happen"),
    ("Actual behaviour", [r"actual", r"error", r"traceback", r"exception"],
     "What actually happened, with the full error / traceback if there is one"),
    ("Environment / version", [r"version", r"environment", r"\bos\b", r"python \d", r"node \d", r"browser"],
     "Version of this project + your OS / runtime / browser"),
]

LOG_MARKERS = ["traceback", "stack trace", "```log", "error:"]


def assess_issue(title, body, config=None):
    cfg = {**DEFAULT_CONFIG, **(config or {})}
    text = f"{title}\n{body or ''}".lower()
    checks, missing = [], []
    for name, patterns, ask in ISSUE_SECTIONS:
        ok = any(re.search(p, text) for p in patterns)
        checks.append(Check(name, ok, "found" if ok else "not found"))
        if not ok:
            missing.append(ask)
    has_code = "```" in (body or "")
    checks.append(Check("Minimal example", has_code,
                         "code block found" if has_code else "no code block / minimal example"))
    if not has_code:
        missing.append("A minimal code example that triggers the issue")
    has_log = any(m in text for m in LOG_MARKERS)
    checks.append(Check("Logs / error output", has_log,
                         "log or error output found" if has_log else "no logs attached (add them if the issue involves an error)"))
    score = round(100 * sum(c.passed for c in checks) / len(checks)) if checks else 0
    labels = []
    if score < 60:
        labels.append(cfg["labels"]["needs_info"])
    if not checks[0].passed:
        labels.append(cfg["labels"]["needs_repro"])
    return TriageResult("issue", score, checks, missing, labels)


def assess_pr(title, body, changed_files, config=None):
    cfg = {**DEFAULT_CONFIG, **(config or {})}
    body = body or ""
    files = changed_files or []
    checks, missing = [], []

    linked = bool(re.search(r"(closes|fixes|resolves)\s+#\d+", body.lower()))
    if cfg["require_linked_issue"]:
        checks.append(Check("Linked issue", linked, "linked issue found" if linked else "no 'Fixes #123' link"))
        if not linked:
            missing.append("Link the issue this PR addresses, e.g. `Fixes #123`")

    tests = any(("test" in f.lower() or "spec" in f.lower()) for f in files)
    def is_code(f):
        fl = f.lower()
        if "test" in fl or "spec" in fl:
            return False
        if fl.endswith((".md", ".rst", ".txt")) or fl.startswith("docs/") or "license" in fl:
            return False
        return True
    code_changed = any(is_code(f) for f in files)
    if cfg["require_tests"]:
        ok = tests or not code_changed
        checks.append(Check("Tests touched", ok,
                             "test files changed" if tests else ("docs/config only — no tests needed" if not code_changed else "code changed but no test files changed")))
        if not ok:
            missing.append("Add or update tests for this change, or explain in the description why tests are not needed")

    desc_len = len(body.strip())
    desc_ok = desc_len >= cfg["min_pr_description_chars"]
    checks.append(Check("Description", desc_ok, f"{desc_len} characters"))
    if not desc_ok:
        missing.append("A fuller description: what changed, why, and how you tested it")

    size_ok = len(files) <= cfg["max_pr_files"]
    checks.append(Check("Reviewable size", size_ok, f"{len(files)} files changed (soft limit {cfg['max_pr_files']})"))
    if not size_ok:
        missing.append(f"Consider splitting this PR — {len(files)} files is a heavy review for a maintainer")

    breaking = bool(re.search(r"breaking change", body.lower()))
    checks.append(Check("Breaking change noted", True,
                         "declared in description" if breaking else "none declared (fine if this is not a breaking change)"))

    score = round(100 * sum(c.passed for c in checks) / len(checks)) if checks else 0
    labels = []
    if score < 75:
        labels.append(cfg["labels"]["needs_info"])
    else:
        labels.append(cfg["labels"]["ready"])
    return TriageResult("pr", score, checks, missing, labels)


def find_duplicate_candidates(title, other_titles, limit=3):
    """Very small, explainable duplicate hint: shared rare words in titles.
    Not a verdict — a shortlist for a human to glance at."""
    def words(t):
        return {w for w in re.findall(r"[a-z0-9]+", (t or "").lower()) if len(w) > 3}
    mine = words(title)
    if not mine:
        return []
    scored = []
    for other in other_titles or []:
        overlap = mine & words(other)
        if len(overlap) >= 2:
            scored.append((len(overlap), other))
    scored.sort(reverse=True)
    return [t for _, t in scored[:limit]]
