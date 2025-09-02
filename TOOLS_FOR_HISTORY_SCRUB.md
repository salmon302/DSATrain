History scrub helper (local only)

Important: Rewriting git history is destructive and requires coordination. Run these steps locally in a clone and force-push the rewritten history to the remote after informing collaborators.

Option A (git-filter-repo, recommended):

1. Install git-filter-repo (see https://github.com/newren/git-filter-repo).
2. Create a mirror clone:

   git clone --mirror <your-repo-url> dsatrain-mirror.git
   cd dsatrain-mirror.git

3. Remove sensitive files from history (example):

   git filter-repo --invert-paths --paths dsatrain_phase4.db --paths dsatrain_phase4_backup_pre_redesign.db --paths config/user_settings.json --paths continuous_cf_backfill.bat

4. Review, then force-push:

   git remote add cleaned <your-repo-url>
   git push --force --all cleaned
   git push --force --tags cleaned

Option B (BFG Repo-Cleaner):

1. Install BFG and run (simpler for large files):

   git clone --mirror <your-repo-url> dsatrain-mirror.git
   java -jar bfg.jar --delete-files dsatrain_phase4.db --delete-files dsatrain_phase4_backup_pre_redesign.db dsatrain-mirror.git
   cd dsatrain-mirror.git
   git reflog expire --expire=now --all && git gc --prune=now --aggressive
   git push --force

Replace API keys in commits by pattern (if needed):

  - Use git-filter-repo with --replace-text mapping file. Create a replace file `replace.txt` with entries like:

    literal:sk-12345678901234567890==>REDACTED_OPENAI_KEY

  - Run:

    git filter-repo --replace-text replace.txt

I can generate the exact `replace.txt` and a PowerShell wrapper if you'd like; I won't run these steps for you because they modify remote history and require your credentials and coordination.
