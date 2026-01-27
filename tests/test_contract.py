"""Contract tests: client against realistic Tuskr API response shapes.

Uses mock responses based on the official API docs. No live API needed.
Useful when you're on the free plan (API not available) or offline.
"""

import pytest
import requests
from unittest.mock import Mock, patch

from tuskr import (
    AddTestCaseRequest,
    AddTestRunResultsRequest,
    BulkExportTestRunsRequest,
    CreateProjectRequest,
    CreateTestRunRequest,
    GetTestRunResultsRequest,
    ImportTestPlanRequest,
    ListProjectsRequest,
    ListTestCasesRequest,
    ListTestRunsRequest,
    ListTestSuitesRequest,
    TuskrClient,
)
from tuskr.models.requests import ImportTestPlanOptions


@pytest.fixture
def client():
    return TuskrClient(tenant_id="tid", token="tok")


def _mock_json(data):
    return lambda: data


# --- List projects (rows, count, meta) ---


@patch.object(requests.Session, "request")
def test_list_projects_response_shape(mock_req, client):
    mock_req.return_value = Mock(
        status_code=200,
        json=_mock_json({
            "rows": [{"id": "p1", "name": "Acme"}],
            "count": 1,
            "meta": {"total": 1, "pages": 1},
        }),
    )
    out = client.list_projects(ListProjectsRequest())
    assert "rows" in out and "count" in out and "meta" in out
    assert out["meta"]["total"] == 1
    assert len(out["rows"]) == 1
    assert out["rows"][0]["name"] == "Acme"


# --- Create project ---


@patch.object(requests.Session, "request")
def test_create_project_response_shape(mock_req, client):
    mock_req.return_value = Mock(
        status_code=200,
        json=_mock_json({"id": "proj-uuid", "name": "New Project"}),
    )
    req = CreateProjectRequest(name="New Project", team={"u@e.com": "Tester"})
    out = client.create_project(req)
    assert out["id"] == "proj-uuid"
    assert out["name"] == "New Project"


# --- Import test plan ---


@patch.object(requests.Session, "request")
def test_import_test_plan_response_shape(mock_req, client):
    mock_req.return_value = Mock(
        status_code=200,
        json=_mock_json({
            "totalTestCases": 1,
            "successCount": 1,
            "errorCount": 0,
            "rowsWithError": [],
        }),
    )
    req = ImportTestPlanRequest(
        project="proj-1",
        test_cases=[
            AddTestCaseRequest(
                project="proj-1",
                test_suite="S",
                test_suite_section="Sec",
                name="TC1",
            ),
        ],
        options=ImportTestPlanOptions(
            create_missing_suites=True,
            create_missing_sections=True,
        ),
    )
    out = client.import_test_plan(req)
    assert out["totalTestCases"] == 1
    assert out["successCount"] == 1
    assert "rowsWithError" in out


# --- List test cases ---


@patch.object(requests.Session, "request")
def test_list_test_cases_response_shape(mock_req, client):
    mock_req.return_value = Mock(
        status_code=200,
        json=_mock_json({
            "rows": [{"id": "tc1", "key": "C-1", "name": "Login"}],
            "count": 1,
            "meta": {"total": 1, "pages": 1},
        }),
    )
    out = client.list_test_cases(ListTestCasesRequest(project="proj-1"))
    assert "rows" in out and "count" in out and "meta" in out
    assert out["rows"][0]["key"] == "C-1"


# --- List test suites ---


@patch.object(requests.Session, "request")
def test_list_test_suites_response_shape(mock_req, client):
    mock_req.return_value = Mock(
        status_code=200,
        json=_mock_json({
            "rows": [{"id": "s1", "name": "E2E", "sections": []}],
            "count": 1,
            "meta": {"total": 1, "pages": 1},
        }),
    )
    out = client.list_test_suites(ListTestSuitesRequest(project="proj-1"))
    assert "rows" in out
    assert out["rows"][0]["name"] == "E2E"


# --- Create test run ---


@patch.object(requests.Session, "request")
def test_create_test_run_response_shape(mock_req, client):
    mock_req.return_value = Mock(
        status_code=200,
        json=_mock_json({"id": "run-uuid", "name": "Sprint 1", "key": "R-1"}),
    )
    req = CreateTestRunRequest(project="proj-1", name="Sprint 1")
    out = client.create_test_run(req)
    assert out["id"] == "run-uuid"
    assert out["name"] == "Sprint 1"


# --- Get test run results ---


@patch.object(requests.Session, "request")
def test_get_test_run_results_response_shape(mock_req, client):
    mock_req.return_value = Mock(
        status_code=200,
        json=_mock_json({
            "data": [
                {"testCase": {"id": "tc1", "key": "C-1"}, "latestStatus": "PASSED"},
            ],
            "meta": {"total": 1, "pages": 1},
        }),
    )
    out = client.get_test_run_results(
        "run-uuid",
        GetTestRunResultsRequest(),
    )
    assert "data" in out and "meta" in out
    assert out["data"][0]["latestStatus"] == "PASSED"


# --- Add test run results (bulk) ---


@patch.object(requests.Session, "request")
def test_add_test_run_results_request_and_success(mock_req, client):
    mock_req.return_value = Mock(status_code=200, json=_mock_json({}))
    req = AddTestRunResultsRequest(
        test_run="R-1",
        test_cases=["C-1", "C-2"],
        status="PASSED",
        comments="All good",
    )
    client.add_test_run_results(req)
    call = mock_req.call_args
    body = call[1]["json"]
    assert "data" in body
    assert body["data"]["testRun"] == "R-1"
    assert body["data"]["testCases"] == ["C-1", "C-2"]
    assert body["data"]["status"] == "PASSED"


# --- List test runs ---


@patch.object(requests.Session, "request")
def test_list_test_runs_response_shape(mock_req, client):
    mock_req.return_value = Mock(
        status_code=200,
        json=_mock_json({
            "rows": [{"id": "r1", "name": "Sprint 1", "key": "R-1"}],
            "count": 1,
            "meta": {"total": 1, "pages": 1},
        }),
    )
    out = client.list_test_runs(ListTestRunsRequest(project="proj-1"))
    assert "rows" in out
    assert out["rows"][0]["key"] == "R-1"


# --- Bulk export test runs ---


@patch.object(requests.Session, "request")
def test_bulk_export_test_runs_response_shape(mock_req, client):
    mock_req.return_value = Mock(
        status_code=200,
        json=_mock_json({
            "count": 1,
            "rows": [{"ID": "r1", "Name": "Run 1", "testCases": []}],
            "meta": {"total": 1, "pages": 1},
        }),
    )
    out = client.bulk_export_test_runs(
        BulkExportTestRunsRequest(project="proj-1"),
    )
    assert "rows" in out and "meta" in out
