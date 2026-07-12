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

- Test the new hed-python schema-version caching (PR #1351, merged) locally: editable-install
  hed-python's `main` (pin still says `hedtools>=1.1.1`, no PyPI release cut yet), run the server,
  and check performance of `get_available_hed_versions()` — see the full plan in
  `../hed-python/.status/plans/session_continuation_plan.md`.

## Completed

<!-- One-line summaries of finished plans, newest first -->

<!-- Example: 2026-02-20 - Added CLI unified entry point (hedpy) - PR #1200 -->
