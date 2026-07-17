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

- **Warmer removal (blocked on hedtools release).** The schema-version manifest fast path is
  merged to hed-python `main`, so `get_available_hed_versions()` no longer does the metered
  GitHub crawl the background warmer was built to hide. The warmer is now *bypassed* (gated
  behind `SCHEMA_VERSION_WARM_ENABLED`, default off in `app_factory.py`) but the code/tests are
  left in place. Once a manifest-capable hedtools PyPI release is cut: delete
  `hedweb/schema_version_warmer.py`, its start block in `app_factory.py`, the
  `SCHEMA_VERSION_WARM_ENABLED`/`SCHEMA_VERSION_WARM_INTERVAL` config keys,
  `tests/test_schema_version_warmer.py`, the warmer assertions in `tests/test_app_factory.py`,
  and `.status/schema-version-cache-warming.md`.
- **Repin hedtools.** `pyproject.toml` currently installs hedtools from
  `git+https://github.com/hed-standard/hed-python.git@main` (the manifest isn't on PyPI yet).
  Pin back to a released `hedtools>=X.Y.Z` once that release exists.
- **GitHub token:** leaving `HED_GITHUB_TOKEN` handling untouched pending more testing (only
  affects the rare REST-API fallback now that the manifest is primary).

## Completed

<!-- One-line summaries of finished plans, newest first -->

<!-- Example: 2026-02-20 - Added CLI unified entry point (hedpy) - PR #1200 -->
