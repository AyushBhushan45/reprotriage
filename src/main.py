"""ReproTriage GitHub Action entrypoint.

Reads the webhook payload from GITHUB_EVENT_PATH, runs deterministic triage,
posts ONE updatable report comment, and (only in `label` mode) adds labels.
Dry-run mode (INPUT_DRY_RUN=true or no token) prints the report instead —
used by examples and tests, and handy for trying it on a fork first.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from triage import assess_issue, assess_pr, find_duplicate_candidates
from config import load_config


def build_report(event, config, files_fetcher=None, titles_fetcher=None):
    if "issue" in event and event.get("action") in (None, "opened", "edited"):
        issue = event["issue"]
        result = assess_issue(issue.get("title", ""), issue.get("body") or "", config)
        number = issue["number"]
        kind = "issue"
        if titles_fetcher:
            try:
                dups = find_duplicate_candidates(issue.get("title", ""), titles_fetcher(number))
            except Exception:
                dups = []
            if dups:
                result.missing.append("Possible duplicates to check first: " + "; ".join(dups))
    elif "pull_request" in event:
        pr = event["pull_request"]
        number = pr["number"]
        files = []
        if files_fetcher:
            try:
                files = files_fetcher(number)
            except Exception:
                files = []
        result = assess_pr(pr.get("title", ""), pr.get("body") or "", files, config)
        kind = "pr"
    else:
        return None, None, None
    return result, number, kind


def main():
    event_path = os.environ.get("GITHUB_EVENT_PATH", "")
    if not event_path or not os.path.exists(event_path):
        print("No event payload — run `python examples/demo.py` for a local demo.")
        return 0
    event = json.load(open(event_path, encoding="utf-8"))
    config = load_config()
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    token = os.environ.get("INPUT_GITHUB-TOKEN") or os.environ.get("GITHUB_TOKEN", "")
    mode = os.environ.get("INPUT_MODE", "report-only")
    dry_run = os.environ.get("INPUT_DRY_RUN", "").lower() == "true" or not token or not repo

    gh = None
    if not dry_run:
        from github_client import GitHub
        gh = GitHub(repo, token)

    result, number, _ = build_report(
        event, config,
        files_fetcher=(gh.pr_files if gh else None),
        titles_fetcher=(gh.open_issue_titles if gh else None),
    )
    if result is None:
        print("Event is not a new/edited issue or PR — skipping.")
        return 0

    report = result.to_markdown()
    print(report)
    if dry_run:
        print("\n[dry-run] Would post the report above as a comment"
              + (f" and add labels {result.suggested_labels}." if mode == "label" else "."))
        return 0
    gh.upsert_comment(number, report)
    if mode == "label":
        gh.add_labels(number, result.suggested_labels)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
