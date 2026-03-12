# CI/CD configuration

## GitHub Actions workflows (.github/workflows/)

### Core testing

| Workflow               | Triggers                 | Python | Description                                                                       |
| ---------------------- | ------------------------ | ------ | --------------------------------------------------------------------------------- |
| `ci.yaml`              | Push + PR (all branches) | 3.10   | Unit tests with coverage + service tests; uploads combined coverage artifact      |
| `test_server_dev.yaml` | Push + PR (all branches) | 3.10   | Builds Docker container via `deploy/deploy.sh`, starts server, runs service tests |

### Code quality

| Workflow        | Triggers          | Tool         | Description                                                                |
| --------------- | ----------------- | ------------ | -------------------------------------------------------------------------- |
| `ruff.yaml`     | Push + PR to main | ruff >=0.8.0 | Ruff linter (`ruff check .`) and formatter check (`ruff format --check .`) |
| `typos.yaml`    | Push + PR to main | typos        | Spelling check via `uvx typos`                                             |
| `mdformat.yaml` | Push + PR to main | mdformat     | Markdown format check                                                      |

### Documentation

| Workflow     | Triggers                      | Description                                                     |
| ------------ | ----------------------------- | --------------------------------------------------------------- |
| `docs.yaml`  | Push + PR to main             | Sphinx build; GitHub Pages deploy on push to main               |
| `links.yaml` | Weekly (Sun 3am UTC) + manual | Sphinx build + Lychee link checker on HTML output and README.md |

## Dependabot

- Monitors GitHub Actions versions for updates

## All CI must pass before merge

- Unit tests and service tests pass
- Linting and formatting clean (ruff check + ruff format)
- Spelling clean (typos), markdown clean (mdformat)
- Documentation builds successfully
- Docker-based service tests pass
