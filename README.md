# Tuskr Python Client

A Python client for the [Tuskr](https://tuskr.app) test management REST API.

## Installation

```bash
pip install tuskr-python-client
```

Or with Poetry (Python 3.12+):

```bash
poetry add tuskr-python-client
```

From source:

```bash
git clone https://github.com/OleksiiTaran/tuskr-python-client.git
cd tuskr-python-client
poetry install
```

## Quick Start

You need a **Tenant ID** and an **Access Token** from Tuskr (Top Menu → API). Treat the token as a secret.

Request bodies use **Pydantic models** for validation and camelCase serialization:

```python
from tuskr import (
    TuskrClient,
    ListProjectsRequest,
    CreateProjectRequest,
    AddTestCaseRequest,
    CreateTestRunRequest,
    AddTestRunResultsRequest,
)

client = TuskrClient(tenant_id="your-tenant-uuid", token="your-api-token")

# List projects
projects = client.list_projects(ListProjectsRequest())
# With filters: ListProjectsRequest(name="Acme", status="active", page=1)

# Create a project
project = client.create_project(
    CreateProjectRequest(name="My Project", team={"user@example.com": "Tester"})
)

# Add a test case
tc = client.add_test_case(
    AddTestCaseRequest(
        project="My Project",
        test_suite="Checkout",
        test_suite_section="Payment",
        name="Valid coupon code",
        test_case_type="Functional",
        estimated_time_in_minutes=15,
    )
)

# Create a test run and add results
run = client.create_test_run(
    CreateTestRunRequest(
        project="My Project",
        name="Sprint 1 Run",
        test_case_inclusion_type="ALL",
        assigned_to="user@example.com",
    )
)
client.add_test_run_results(
    AddTestRunResultsRequest(
        test_run="Sprint 1 Run",
        test_cases=["C-1", "C-2"],
        status="PASSED",
        comments="All good",
    )
)
```

## API Coverage

- **Projects**: `create_project`, `list_projects`
- **Test cases**: `add_test_case`, `upsert_test_case`, `import_test_plan`, `list_test_cases`
- **Test suites**: `list_test_suites`
- **Test runs**: `create_test_run`, `copy_test_run`, `list_test_runs`, `get_test_run_results`, `delete_test_runs`, `bulk_export_test_runs`
- **Results**: `add_test_run_results`

See the [Tuskr API docs](https://tuskr.app/kb/latest/api) for details.

## Exceptions

- `TuskrAPIError` — base API error (4xx/5xx)
- `TuskrAuthError` — invalid or expired token (401)
- `TuskrRateLimitError` — rate limit exceeded (429)

## Rate Limits

Tuskr enforces **10 requests/second** and plan-specific hourly limits. Use bulk operations (e.g. `import_test_plan`, `add_test_run_results`) where possible.

## Development

Requires **Python 3.12+** and [Poetry](https://python-poetry.org/).

```bash
poetry install
poetry run pytest
```

### Verifying without live API (free plan / offline)

The Tuskr API is **only available on trial or paid plans**; the free plan has no API access.

You can still verify the client **without a live project**:

- **Unit tests** – request/response models, validation, HTTP error handling.
- **Contract tests** – client against **realistic mock responses** from the [API docs](https://tuskr.app/kb/latest/api) (list projects, create project, import plan, test runs, results, etc.):

```bash
poetry run pytest tests/test_client.py tests/test_contract.py -v
```

### Verifying against live Tuskr (trial or paid)

You need **Tenant ID**, **API token**, and **team email** from **Top Menu → API** (trial or paid account).

**Smoke script** (create project → import plan → run → results → cleanup):

```bash
export TUSKR_TENANT_ID="your-tenant-uuid"
export TUSKR_TOKEN="your-api-token"
export TUSKR_TEAM_EMAIL="your@email.com"
poetry run python scripts/smoke_test.py
```

**Integration tests** (skipped if env vars are missing):

```bash
export TUSKR_TENANT_ID="..." TUSKR_TOKEN="..." TUSKR_TEAM_EMAIL="..."
poetry run pytest tests/integration -v -m integration
```

**If you're on the free plan:** start a new [trial](https://tuskr.app) (e.g. with another email) to get API access temporarily, run the smoke or integration tests, then rely on unit + contract tests afterward.

## Publishing (maintainers)

**GitHub:** Create a repo at `https://github.com/OleksiiTaran/tuskr-python-client`, then:

```bash
git remote add origin https://github.com/OleksiiTaran/tuskr-python-client.git
git push -u origin main
```

**PyPI:** [Create a PyPI account](https://pypi.org/account/register/) and [API token](https://pypi.org/manage/account/token/), then:

```bash
poetry config pypi-token.pypi YOUR_TOKEN   # or use env POETRY_HTTP_BASIC_PYPI_PASSWORD
poetry build
poetry publish
```

Tag releases for versions (e.g. `git tag v0.1.0 && git push --tags`).

## License

MIT
