History scrub runbook (PowerShell, local)

Important safety notes:
- Run these steps locally in a fresh clone or mirror clone.
- Inform all collaborators before force-pushing rewritten history.
- Backup your repo before starting.

1) Prepare a local replace.txt safely (do NOT commit it):

   # In PowerShell, set environment variables for secrets you found
   $env:REDACT_OPENAI = 'sk-REPLACE_ME_OPENAI'
   $env:REDACT_OPENROUTER = 'sk-or-REPLACE_ME_OPENROUTER'
   $env:REDACT_CF_COOKIE = 'JSESSIONID=...; cf_clearance=...'

   # Run the helper to produce replace.txt locally
   .\scripts\generate_replace_from_env.ps1

2) Mirror-clone the repository (clean workspace):

   git clone --mirror https://github.com/<owner>/DSATrain.git dsatrain-mirror.git
   cd dsatrain-mirror.git

3) Run git-filter-repo with replace.txt and path removals:

   # Replace text matches from replace.txt
   git filter-repo --replace-text ../replace.txt

   # Also remove large binary DB files and sensitive scripts entirely from history
   git filter-repo --invert-paths --paths dsatrain_phase4.db --paths dsatrain_phase4_backup_pre_redesign.db --paths config/user_settings.json --paths continuous_cf_backfill.bat

4) Cleanup and force-push to origin (coordinate with team):

   git reflog expire --expire=now --all
   git gc --prune=now --aggressive
   git remote add cleaned https://github.com/<owner>/DSATrain.git
   git push --force cleaned refs/heads/*
   git push --force cleaned --tags

5) After pushing:
   - Rotate any credentials that were exposed.
   - Notify collaborators to reclone or run `git fetch --all && git reset --hard origin/main`.

If you'd like, I can generate the exact `replace.txt` content for the secrets we discovered but I will not add those sensitive strings to the repo — you'll run the helper locally to create `replace.txt` from environment variables.
