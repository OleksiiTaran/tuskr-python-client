"""Live Tuskr API integration tests.

Run with:
  TUSKR_TENANT_ID=... TUSKR_TOKEN=... TUSKR_TEAM_EMAIL=... \\
  poetry run pytest tests/integration -v -m integration
"""

import time

import pytest

from tuskr import (
    AddTestCaseRequest,
    AddTestRunResultsRequest,
    CreateProjectRequest,
    CreateTestRunRequest,
    DeleteTestRunsRequest,
    GetTestRunResultsRequest,
    ImportTestPlanRequest,
    ListProjectsRequest,
    ListTestCasesRequest,
    ListTestRunsRequest,
    ListTestSuitesRequest,
)
from tuskr.models.requests import ImportTestPlanOptions


@pytest.mark.integration
def test_list_projects(live_client, tuskr_env):
    """List projects returns 200 and rows/count/meta structure."""
    out = live_client.list_projects(ListProjectsRequest())
    assert "rows" in out
    assert "count" in out
    assert "meta" in out
    assert "total" in out["meta"]
    assert "pages" in out["meta"]


@pytest.mark.integration
def test_create_project_and_list(live_client, tuskr_env):
    """Create a project, then list and find it by name."""
    name = f"tuskr-client-test-{int(time.time())}"
    team = {tuskr_env["team_email"]: "Tester"}
    created = live_client.create_project(
        CreateProjectRequest(name=name, team=team)
    )
    assert "id" in created
    assert created.get("name") == name

    listed = live_client.list_projects(ListProjectsRequest(name=name))
    assert listed["count"] >= 1
    ids = [r["id"] for r in listed["rows"] if r.get("name") == name]
    assert created["id"] in ids


@pytest.mark.integration
def test_import_test_plan_then_list_suites_and_cases(live_client, tuskr_env):
    """Create project, import plan, list suites and test cases."""
    name = f"tuskr-import-test-{int(time.time())}"
    team = {tuskr_env["team_email"]: "Tester"}
    proj = live_client.create_project(
        CreateProjectRequest(name=name, team=team)
    )
    project_id = proj["id"]

    import_req = ImportTestPlanRequest(
        project=project_id,
        test_cases=[
            AddTestCaseRequest(
                project=project_id,
                test_suite="E2E",
                test_suite_section="Checkout",
                name="Pay with card",
                test_case_type="Functional",
                estimated_time_in_minutes=5,
            ),
        ],
        options=ImportTestPlanOptions(
            create_missing_suites=True,
            create_missing_sections=True,
        ),
    )
    imp = live_client.import_test_plan(import_req)
    assert imp.get("successCount", imp.get("totalTestCases", 0)) >= 1

    suites = live_client.list_test_suites(
        ListTestSuitesRequest(project=project_id)
    )
    assert suites["count"] >= 1
    assert any(s.get("name") == "E2E" for s in suites["rows"])

    cases = live_client.list_test_cases(
        ListTestCasesRequest(project=project_id)
    )
    assert cases["count"] >= 1
    assert any(
        c.get("name") == "Pay with card" for c in cases["rows"]
    )


@pytest.mark.integration
def test_create_run_add_results_and_cleanup(live_client, tuskr_env):
    """Create project + plan, create test run, add results, delete run."""
    name = f"tuskr-run-test-{int(time.time())}"
    team = {tuskr_env["team_email"]: "Tester"}
    proj = live_client.create_project(
        CreateProjectRequest(name=name, team=team)
    )
    project_id = proj["id"]

    import_req = ImportTestPlanRequest(
        project=project_id,
        test_cases=[
            AddTestCaseRequest(
                project=project_id,
                test_suite="Smoke",
                test_suite_section="Login",
                name="Login with valid credentials",
                test_case_type="Functional",
            ),
        ],
        options=ImportTestPlanOptions(
            create_missing_suites=True,
            create_missing_sections=True,
        ),
    )
    live_client.import_test_plan(import_req)

    cases = live_client.list_test_cases(
        ListTestCasesRequest(project=project_id)
    )
    assert cases["count"] >= 1
    tc_key = cases["rows"][0].get("key")
    assert tc_key

    run_name = f"[tuskr-client-test] {int(time.time())}"
    run_req = CreateTestRunRequest(
        project=project_id,
        name=run_name,
        test_case_inclusion_type="ALL",
    )
    run = live_client.create_test_run(run_req)
    assert "id" in run
    run_id = run["id"]

    results = live_client.get_test_run_results(
        run_id, GetTestRunResultsRequest()
    )
    assert "data" in results
    assert "meta" in results

    add_req = AddTestRunResultsRequest(
        test_run=run_id,
        test_cases=[tc_key],
        status="PASSED",
        comments="Integration test",
    )
    live_client.add_test_run_results(add_req)

    runs = live_client.list_test_runs(
        ListTestRunsRequest(project=project_id, name=run_name)
    )
    assert runs["count"] >= 1

    deleted = live_client.delete_test_runs(
        DeleteTestRunsRequest(
            projects=[project_id],
            name_starts_with="[tuskr-client-test]",
            older_than_days=0,
        )
    )
    # API returns number of deleted runs or similar
    assert deleted is not None
