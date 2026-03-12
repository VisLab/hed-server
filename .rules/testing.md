# Testing standards

## Framework

- **unittest** is the project standard for writing and running tests
- Unit test files are flat under `tests/` (no subdirectory nesting)
- Test file naming: `test_<module>.py`
- Uses unittest's `setUp`/`setUpClass` (no pytest fixtures or conftest.py)

## Test organization

```
tests/
  data/                - Test data files (HED files, sidecars, TSVs, spreadsheets)
  test_routes/         - Route-specific test fixtures and helpers
  test_columns.py      - Column processing tests
  test_events.py       - Event operations tests
  test_runserver.py    - Server startup tests
  test_schemas.py      - Schema operation tests
  test_services.py     - REST service tests
  test_sidecars.py     - Sidecar operation tests
  test_spreadsheets.py - Spreadsheet operation tests
  test_strings.py      - HED string operation tests
  test_web_base.py     - Base web functionality tests
  test_web_util.py     - Web utility function tests

service_tests/
  data/                        - Test data for REST service tests
  run_service_tests.py         - Test runner (starts server automatically)
  test_service_base.py         - Base class for service tests
  test_service_event_remodeling.py
  test_service_event_search.py
  test_service_event_services.py
  test_service_get_services.py
  test_service_library.py
  test_service_sidecars.py
  test_service_spreadsheet.py
  test_service_strings.py
```

## Running tests

```powershell
# All unit tests
python -m unittest discover -s tests -p "test*.py" -v

# Specific test file
python -m unittest tests.test_events -v

# Specific test case
python -m unittest tests.test_events.TestEvents.test_assemble_dispatch -v

# Service tests (requires a running server or starts one automatically)
python service_tests/run_service_tests.py --verbose
```

## Test patterns

- Use `setUpClass` to create the Flask test client (shared across test methods)
- Unit tests use Flask's built-in test client: `app.test_client()`
- Each test should be independent and isolated
- Test both success and failure/error cases
- Service tests hit the REST API over HTTP; they require a running server

## Coverage

- Branch coverage enabled (`.coveragerc`)
- Source: `hedweb` package
- CI runs unit tests and service tests separately, merges coverage
- CI uploads combined coverage report
