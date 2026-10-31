"""Minimal GitHub REST client using only the standard library.
Runs inside the adopting repo's own Actions runner with its GITHUB_TOKEN.
No code or issue content ever leaves GitHub — calls go to api.github.com only.
"""
import json
import urllib.request

API = "https://api.github.com"
MARKER = "<!-- reprotriage -->"


class GitHub:
    def __init__(self, repo, token):
        self.repo = repo  # "owner/name"
        self.token = token

    def _call(self, method, path, payload=None):
        req = urllib.request.Request(
            API + path,
            method=method,
            data=json.dumps(payload).encode() if payload is not None else None,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "Content-Type": "application/json",
                "User-Agent": "ReproTriage",
            },
        )
        with urllib.request.urlopen(req) as resp:
            raw = resp.read()
            return json.loads(raw) if raw else {}

    def pr_files(self, number):
        data = self._call("GET", f"/repos/{self.repo}/pulls/{number}/files?per_page=100")
        return [f["filename"] for f in data]

    def open_issue_titles(self, exclude_number):
        data = self._call("GET", f"/repos/{self.repo}/issues?state=open&per_page=50")
        return [i["title"] for i in data if i["number"] != exclude_number and "pull_request" not in i]

    def upsert_comment(self, number, body):
        """Create the ReproTriage comment, or update it on re-runs (no spam)."""
        full = MARKER + "\n" + body
        comments = self._call("GET", f"/repos/{self.repo}/issues/{number}/comments?per_page=100")
        for c in comments:
            if MARKER in (c.get("body") or ""):
                return self._call("PATCH", f"/repos/{self.repo}/issues/comments/{c['id']}", {"body": full})
        return self._call("POST", f"/repos/{self.repo}/issues/{number}/comments", {"body": full})

    def add_labels(self, number, labels):
        if labels:
            return self._call("POST", f"/repos/{self.repo}/issues/{number}/labels", {"labels": labels})
        return {}
