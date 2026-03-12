# Code review process

## Before creating a PR

1. All tests pass: `python -m unittest discover -s tests -p "test*.py" -v`
2. Linting clean: `ruff check . --fix`
3. Formatting clean: `ruff format --check .`
4. Spelling clean: `uvx typos`
5. New functionality has tests (real data, no mocks)

## PR review with pr-review-toolkit

Run `/review-pr` with all subagents in parallel:

- **Code reviewer:** bugs, logic errors, security vulnerabilities, code quality, project conventions
- **Silent failure hunter:** error handling, catch blocks, fallback behavior
- **Code simplifier:** unnecessary complexity
- **Comment analyzer:** comment accuracy and maintainability
- **Test analyzer:** test coverage quality and completeness
- **Type design analyzer:** type design quality (encapsulation, invariants)

## Review standards

- Address all critical and important findings (fix or explain why skipped)
- Consider nice-to-haves if they improve quality without major effort
- Document unaddressed items in PR comments
- All 8 CI workflows must be green before merge
