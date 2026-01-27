#!/usr/bin/env python3
"""Smoke test against live Tuskr API.

Usage:
  export TUSKR_TENANT_ID="your-tenant-uuid"
  export TUSKR_TOKEN="your-api-token"
  export TUSKR_TEAM_EMAIL="your@email.com"
  poetry run python scripts/smoke_test.py
"""

import os
import sys
import time

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
    TuskrClient,
)
from tuskr.models.requests import ImportTestPlanOptions


def env(name: str) -> str:
    v = os.environ.get(name)
    if not v:
        print(f"Missing {name}. Set TUSKR_TENANT_ID, TUSKR_TOKEN, TUSKR_TEAM_EMAIL.")
        sys.exit(1)
    return v


def main() -> None:
    tenant_id = env("TUSKR_TENANT_ID")
    token = env("TUSKR_TOKEN")
    team_email = env("TUSKR_TEAM_EMAIL")

    client = TuskrClient(tenant_id=tenant_id, token=token)
    ts = int(time.time())
    project_name = f"tuskr-smoke-{ts}"

    print("1. List projects…")
    out = client.list_projects(ListProjectsRequest())
    print(f"   Found {out['count']} project(s)")

    print("2. Create project…")
    proj = client.create_project(
        CreateProjectRequest(name=project_name, team={team_email: "Tester"})
    )
    pid = proj["id"]
    print(f"   Created {project_name} ({pid})")

    print("3. Import test plan…")
    imp = client.import_test_plan(
        ImportTestPlanRequest(
            project=pid,
            test_cases=[
                AddTestCaseRequest(
                    project=pid,
                    test_suite="Smoke",
                    test_suite_section="Health",
                    name="API smoke check",
                    test_case_type="Functional",
                ),
            ],
            options=ImportTestPlanOptions(
                create_missing_suites=True,
                create_missing_sections=True,
            ),
        )
    )
    print(f"   Imported: {imp.get('successCount', '?')} ok")

    print("4. List suites & cases…")
    suites = client.list_test_suites(ListTestSuitesRequest(project=pid))
    cases = client.list_test_cases(ListTestCasesRequest(project=pid))
    print(f"   Suites: {suites['count']}, Cases: {cases['count']}")
    tc_key = cases["rows"][0]["key"] if cases["rows"] else None

    print("5. Create test run…")
    run_name = f"[smoke] {ts}"
    run = client.create_test_run(
        CreateTestRunRequest(project=pid, name=run_name, test_case_inclusion_type="ALL")
    )
    run_id = run["id"]
    print(f"   Run {run_id}")

    print("6. Get results, add result…")
    client.get_test_run_results(run_id, GetTestRunResultsRequest())
    if tc_key:
        client.add_test_run_results(
            AddTestRunResultsRequest(
                test_run=run_id,
                test_cases=[tc_key],
                status="PASSED",
                comments="Smoke test",
            )
        )
        print("   Added PASSED result")

    print("7. List test runs, delete run…")
    client.list_test_runs(ListTestRunsRequest(project=pid, name=run_name))
    client.delete_test_runs(
        DeleteTestRunsRequest(
            projects=[pid],
            name_starts_with="[smoke]",
            older_than_days=0,
        )
    )
    print("   Deleted")

    print("\nSmoke test OK.")
    client.close()


if __name__ == "__main__":
    main()
