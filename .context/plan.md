# HED web development plan

<!-- PLAN ROTATION POLICY:
  - Only active/in-progress plans belong in "Active Tasks" below.
  - When a plan is fully executed, collapse it to 1-2 summary lines
    under "Completed" (include date and PR/issue number if applicable).
  - Delete detailed steps of completed plans; do not let this file grow
    into an archive. If historical detail is needed, link to the PR or
    issue instead.
  - Review this file at the start of each session; prune anything stale.
-->

## Active tasks

<!-- none -->

## Completed

<!-- One-line summaries of finished plans, newest first -->

- 2026-07-18 - Adopted released hedtools 1.2.0 (CDN manifest): removed the obsolete
  schema-version warmer (`schema_version_warmer.py`, its `app_factory.py` block, and
  `tests/test_schema_version_warmer.py`/`tests/test_app_factory.py`); removed all GitHub-token
  wiring (`deploy.sh`, CI, docs, `.github_token` ignores); pinned `ci.yaml` to `hedtools>=1.2.0`
  from PyPI. Dev deploy (`deploy.sh dev` / `test_server_dev.yaml`) still tracks hed-python `main`.
  hed-server now uses the CDN manifest with no GitHub token.

<!-- Example: 2026-02-20 - Added CLI unified entry point (hedpy) - PR #1200 -->
