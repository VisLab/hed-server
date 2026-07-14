# Changelog

All notable changes to the `hed-server` project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 2026-07-13

### Added

- **New Operations Architecture:** Implemented new operation handlers (`event_operations.py`, `schema_operations.py`, `sidecar_operations.py`, `spreadsheet_operations.py`, `string_operations.py`) to modularize logic previously contained in general files.
- **Process Management:** Added `process_form.py` and `process_service.py` to streamline form handling and backend service processing.
- **Service Testing Framework:** Created a dedicated `service_tests` suite with comprehensive tests for event remodeling, event search, sidecars, strings, and spreadsheets.
- **Modernized Documentation:**
  - Overhauled documentation structure using ReadTheDocs and Sphinx, located in the `docs/` directory.
  - Added new `deployment.md` and `user_guide.md` files.
  - Migrated to new custom HTML templates, CSS, and sidebar navigation.
- **Frontend Enhancements:**
  - Integrated Bootstrap 5 grid and utility classes for responsive UI.
  - **UI Help Facility:** Introduced comprehensive `ui_help.json` resource providing contextual help information for all interface elements, improving user experience with integrated documentation.
  - Added new search interface components (`hed-search.js`, `osa-chat-widget.js`, `search.html`).
  - Added new JS template files for form handling (`schemas-form.js`, `sidecars-form.js`, `spreadsheets-form.js`, `strings-form.js`).
  - **External Definitions Support:** Added support for external HED definitions via dedicated `definitions-input.html` template, enabling users to work with custom definition libraries.
- **CI/CD & Repository Management:**
  - Added `.rules` directory for contributor guidelines (`ci_cd.md`, `code_review.md`, `git.md`, `python.md`, `testing.md`).
  - Implemented GitHub Actions workflows for tests, formatting (Ruff, Markdown), link checking, and typos.
  - Added `pyproject.toml` and `lychee.toml` for modern Python packaging and link validation.
- **Deployment Profiles:** Added new Docker deployment configurations and scripts in `deploy/`.
- **HED Schema Caching Fallback:** Implemented resilient fallback mechanism to recover from schema cache failures; when online and local schema sources are unavailable, the application now falls back to installed hedtools cache with improved logging for better debugging.
- **Developer Guidelines:** Added review response conventions to `copilot-instructions.md` for improved code review collaboration and clarity.
- **Schema Version Endpoint Tests:** Added comprehensive test coverage for schema version endpoint fallback scenarios (`test_routes_schema_versions.py`), including validation of the installed cache fallback mechanism.

### Changed

- **Pluralized Naming Convention:** Renamed multiple core modules and templates for consistency (e.g., `schema.py` to `schemas.py`, `sidecar.py` to `sidecars.py`, `spreadsheet.py` to `spreadsheets.py`).
- **Test Suite Restructuring:** Major refactoring of the `tests/` directory to align with the new pluralized route and operation architecture.
- **Web Utilities:** Extensive updates to `web_util.py`, `routes.py`, and `columns.py` to support the new operation handlers.
- **Constants Reorganization:** Updated constants across `base_constants.py`, `file_constants.py`, `page_constants.py`, and `route_constants.py`.
- **Dataset Examples:** Updated `service_tests/data` and `tests/data` with new BIDS/HED sample datasets and event files.

### Removed

- **Deprecated Architecture:** Removed legacy `events.py`, `schema.py`, `services.py`, `sidecar.py`, `spreadsheet.py`, and `strings.py` in favor of the new operations-based structure.
- **Legacy Deployment Scripts:** Removed old specific deployment directories (`deploy_hed/`, `deploy_hed_dev/`).
- **Old Configuration Files:** Removed `setup.cfg`, `readthedocs.yml`, `versioneer.py`, and `.codeclimate.yml`.
- **Outdated Static Assets:** Removed obsolete CSS files (`schema-form.css`, `dictionary-form.css`) and various legacy tutorial/error screenshot images from `static/img/`.

## [0.2.0] - 2024-06-25

- Prior release state before the standalone repository migration and structural overhaul.
