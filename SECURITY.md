# Security Policy

## How ReproTriage handles your repo
- It runs **inside your own GitHub Actions runner** with your workflow's `GITHUB_TOKEN`.
- The deterministic layer makes **no external calls** except to `api.github.com`.
- It requests only `issues: write` and `pull-requests: write`. It never needs `contents: write`.
- It never executes code from an issue or PR. Reproduction-running is a future opt-in feature and will only ever run in the adopting repo's own sandbox, under its own permissions.
- Report-only by default: it cannot close, merge, or reject anything — it has no code path that does so.

## Reporting a vulnerability
Open a private security advisory on this repository, or open an issue titled `security:` without exploit details and a maintainer will follow up.
