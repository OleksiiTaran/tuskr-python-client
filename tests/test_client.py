"""Tests for the Tuskr client and request models."""

import pytest
import requests
from unittest.mock import Mock, patch

from tuskr import (
    AddTestCaseRequest,
    CreateProjectRequest,
    CreateTestRunRequest,
    DeleteTestRunsRequest,
    ListProjectsRequest,
    ListTestCasesRequest,
    TuskrClient,
    UpsertTestCaseRequest,
)
from tuskr.exceptions import TuskrAuthError, TuskrRateLimitError
from tuskr.models.requests import dump_request


@pytest.fixture
def client():
    return TuskrClient(tenant_id="test-tenant", token="test-token")


def test_client_builds_url(client):
    assert "api/tenant/test-tenant/project" in client._url("project")
    assert client._url("/project") == client._url("project")


def test_client_sets_auth_headers(client):
    assert client._session.headers["Authorization"] == "Bearer test-token"
    assert client._session.headers["Content-Type"] == "application/json"


@patch.object(requests.Session, "request")
def test_request_raises_auth_error_on_401(mock_request, client):
    mock_request.return_value = Mock(status_code=401, text="Unauthorized")
    with pytest.raises(TuskrAuthError) as exc_info:
        client.list_projects(ListProjectsRequest())
    assert exc_info.value.status_code == 401


@patch.object(requests.Session, "request")
def test_request_raises_rate_limit_on_429(mock_request, client):
    mock_request.return_value = Mock(status_code=429, text="Too Many Requests")
    with pytest.raises(TuskrRateLimitError) as exc_info:
        client.list_projects(ListProjectsRequest())
    assert exc_info.value.status_code == 429


@patch.object(requests.Session, "request")
def test_list_projects_request(mock_request, client):
    mock_request.return_value = Mock(
        status_code=200,
        json=lambda: {"rows": [], "count": 0, "meta": {"total": 0, "pages": 0}},
    )
    req = ListProjectsRequest(name="Acme", page=2)
    out = client.list_projects(req)
    assert out["count"] == 0
    call = mock_request.call_args
    assert call[1]["params"]["filter[name]"] == "Acme"
    assert call[1]["params"]["page"] == 2


# --- Request model serialization (camelCase, exclude None) ---


def test_create_project_request_dump():
    req = CreateProjectRequest(name="P", team={"a@b.com": "Tester"})
    d = dump_request(req)
    assert d["name"] == "P"
    assert d["team"] == {"a@b.com": "Tester"}
    assert d["status"] == "active"
    assert "description" not in d


def test_add_test_case_request_dump():
    req = AddTestCaseRequest(
        project="P",
        test_suite="S",
        test_suite_section="Sec",
        name="TC",
        estimated_time_in_minutes=10,
    )
    d = dump_request(req)
    assert d["project"] == "P"
    assert d["testSuite"] == "S"
    assert d["testSuiteSection"] == "Sec"
    assert d["name"] == "TC"
    assert d["estimatedTimeInMinutes"] == 10


def test_upsert_test_case_request_dump():
    req = UpsertTestCaseRequest(project="P", name="TC", external_id="EXT-1")
    d = dump_request(req)
    assert d["externalId"] == "EXT-1"
    assert "id" not in d


def test_list_projects_request_to_params():
    req = ListProjectsRequest(name="Acme", status="active", page=2)
    p = req.to_params()
    assert p["filter[name]"] == "Acme"
    assert p["filter[status]"] == "active"
    assert p["page"] == 2


def test_list_test_cases_request_to_params():
    req = ListTestCasesRequest(project="Proj1", test_suite="Suite1", page=1)
    p = req.to_params()
    assert p["filter[project]"] == "Proj1"
    assert p["filter[testSuite]"] == "Suite1"
    assert p["page"] == 1


def test_delete_test_runs_request_validates():
    with pytest.raises(ValueError, match="At least one"):
        DeleteTestRunsRequest(purge=False)
    req = DeleteTestRunsRequest(projects=["P1"], purge=True)
    d = dump_request(req)
    assert d["projects"] == ["P1"]
    assert d["purge"] is True


def test_create_test_run_specific_requires_test_cases():
    with pytest.raises(ValueError, match="test_cases is required"):
        CreateTestRunRequest(
            project="P",
            name="R",
            test_case_inclusion_type="SPECIFIC",
        )


def test_create_project_request_team_required():
    with pytest.raises(ValueError, match="at least one"):
        CreateProjectRequest(name="P", team={})


@patch.object(requests.Session, "request")
def test_create_project_sends_request_model(mock_request, client):
    mock_request.return_value = Mock(status_code=200, json=lambda: {"id": "proj-1"})
    req = CreateProjectRequest(name="P", team={"u@e.com": "Tester"})
    out = client.create_project(req)
    assert out["id"] == "proj-1"
    call = mock_request.call_args
    body = call[1]["json"]
    assert "data" in body
    assert body["data"]["name"] == "P"
    assert body["data"]["team"] == {"u@e.com": "Tester"}
    assert body["data"]["status"] == "active"
