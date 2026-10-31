"""Load optional .github/reprotriage.yml — tiny YAML subset, no dependencies.
Supports flat keys only: min_pr_description_chars, max_pr_files,
require_linked_issue, require_tests. Anything else is ignored safely.
"""
import os

INT_KEYS = {"min_pr_description_chars", "max_pr_files"}
BOOL_KEYS = {"require_linked_issue", "require_tests"}


def load_config(path=None):
    path = path or os.path.join(os.getcwd(), ".github", "reprotriage.yml")
    cfg = {}
    if not os.path.exists(path):
        return cfg
    for line in open(path, encoding="utf-8"):
        line = line.split("#", 1)[0].strip()
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if key in INT_KEYS:
            try:
                cfg[key] = int(value)
            except ValueError:
                pass
        elif key in BOOL_KEYS:
            cfg[key] = value.lower() in ("true", "yes", "on", "1")
    return cfg
