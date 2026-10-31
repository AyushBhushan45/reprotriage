import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "src"))
from triage import assess_issue, assess_pr, find_duplicate_candidates
from config import load_config
from main import build_report

GOOD_ISSUE = """Steps to reproduce: run demo.py
Expected: it prints ok
Actual: error traceback
Version: 1.2.3, OS: Ubuntu, Python 3.12
```python
import demo; demo.run()
```
Error: Traceback (most recent call last)
"""

def test_good_issue_scores_high():
    r = assess_issue("Bug in demo", GOOD_ISSUE)
    assert r.score >= 80
    assert r.missing == []

def test_empty_issue_scores_low_and_asks_for_repro():
    r = assess_issue("it broke", "help it does not work")
    assert r.score < 60
    assert "needs-repro" in r.suggested_labels
    assert len(r.missing) >= 3

def test_good_pr_is_ready():
    body = "Fixes #42\n\nThis change fixes the crash by validating input before parsing. Tested with the full test suite locally and in CI."
    r = assess_pr("Fix crash", body, ["src/fix.py", "tests/test_fix.py"])
    assert r.score >= 75
    assert "ready-for-review" in r.suggested_labels

def test_pr_without_issue_or_tests_is_flagged():
    r = assess_pr("stuff", "wip", ["src/a.py"])
    assert r.score < 75
    assert len(r.missing) >= 2

def test_docs_only_pr_does_not_need_tests():
    body = "Fixes #7\n\nThis updates the README installation section and fixes two broken links. No code changes, docs only, rendered and checked locally."
    r = assess_pr("Docs update", body, ["README.md"])
    test_check = [c for c in r.checks if c.name == "Tests touched"][0]
    assert test_check.passed

def test_huge_pr_is_flagged_for_size():
    body = "Fixes #9\n\nLarge refactor across many modules with full test coverage and a detailed migration guide for users upgrading from the previous major version."
    files = [f"src/mod{i}.py" for i in range(40)] + ["tests/test_all.py"]
    r = assess_pr("Big refactor", body, files)
    size = [c for c in r.checks if c.name == "Reviewable size"][0]
    assert not size.passed

def test_config_can_relax_pr_description():
    body = "Fixes #3 short"
    strict = assess_pr("x", body, ["tests/test_x.py"])
    relaxed = assess_pr("x", body, ["tests/test_x.py"], {"min_pr_description_chars": 5})
    desc_strict = [c for c in strict.checks if c.name == "Description"][0]
    desc_relaxed = [c for c in relaxed.checks if c.name == "Description"][0]
    assert not desc_strict.passed and desc_relaxed.passed

def test_duplicate_candidates():
    dups = find_duplicate_candidates("Crash on login with empty password",
        ["Login crash when password is empty", "Add dark mode", "Crash on login page"])
    assert "Login crash when password is empty" in dups
    assert "Add dark mode" not in dups

def test_markdown_report_is_explainable_and_safe():
    md = assess_issue("x", "y").to_markdown()
    assert "ReproTriage report" in md
    assert "auto-closed" in md
    assert "Readiness:" in md

def test_build_report_from_issue_event():
    event = {"action": "opened", "issue": {"number": 5, "title": "Bug", "body": GOOD_ISSUE}}
    result, number, kind = build_report(event, {})
    assert number == 5 and kind == "issue" and result.score >= 80

def test_build_report_from_pr_event_uses_files():
    event = {"pull_request": {"number": 9, "title": "Fix",
        "body": "Fixes #42\n\nThis change fixes the crash by validating input before parsing. Tested with the full test suite locally and in CI."}}
    result, number, kind = build_report(event, {}, files_fetcher=lambda n: ["src/fix.py", "tests/test_fix.py"])
    assert number == 9 and kind == "pr" and "ready-for-review" in result.suggested_labels

def test_build_report_skips_other_events():
    result, number, kind = build_report({"release": {}}, {})
    assert result is None

def test_default_config_loads_when_missing(tmp_path=None):
    cfg = load_config("/nonexistent/reprotriage.yml")
    assert cfg == {}
