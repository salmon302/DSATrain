## Security & Sensitive Data Removal

This repository previously contained sensitive artifacts (API keys, cookies, and SQLite database files). Before publishing or sharing this repo, follow these steps:

1. Git history scrub (if secrets were committed):
   - Use `git-filter-repo` or the BFG Repo-Cleaner on your local clone to remove secrets and large binary files from history.
   - Example (requires installation):
     - git clone --mirror <repo>
     - git-filter-repo --invert-paths --paths dsatrain_phase4.db

2. Use environment variables or a secrets manager for secrets. Do NOT commit real API keys in `config/user_settings.json`.

3. Add CI checks to prevent secrets in commits (e.g., GitHub Actions with truffleHog or detect-secrets).

4. Replace any removed database or log files with placeholders (`*.REMOVED` files are present in the repo root).

5. Rotate any exposed API credentials immediately.

If you want, I can prepare a git-filter-repo script to fully scrub history; run it locally because it requires force-pushing rewritten history.
