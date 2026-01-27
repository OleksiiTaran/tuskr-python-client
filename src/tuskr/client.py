"""
Tuskr API client.

See https://tuskr.app/kb/latest/api for API documentation.
"""

import requests
from typing import Any, Self

from tuskr.exceptions import TuskrAPIError, TuskrAuthError, TuskrRateLimitError
from pydantic import BaseModel

from tuskr.models.list_requests import (
    BulkExportTestRunsRequest,
    GetTestRunResultsRequest,
    ListProjectsRequest,
    ListTestCasesRequest,
    ListTestRunsRequest,
    ListTestSuitesRequest,
)
from tuskr.models.requests import (
    AddTestCaseRequest,
    AddTestRunResultsRequest,
    CopyTestRunRequest,
    CreateProjectRequest,
    CreateTestRunRequest,
    DeleteTestRunsRequest,
    ImportTestPlanRequest,
    UpsertTestCaseRequest,
)
from tuskr.models.requests import dump_request as _dump_request

DEFAULT_BASE_URL = "https://api.tuskr.live"


class TuskrClient:
    """
    Client for the Tuskr test management REST API.

    All API calls require a tenant ID (your account ID) and an access token.
    Obtain both from Tuskr: Top Menu → API.
    """

    def __init__(
        self,
        tenant_id: str,
        token: str,
        base_url: str = DEFAULT_BASE_URL,
        session: requests.Session | None = None,
    ):
        self.tenant_id = tenant_id
        self.token = token
        self.base_url = base_url.rstrip("/")
        self._session = session or requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }
        )

    def _url(self, path: str) -> str:
        path = path.lstrip("/")
        return f"{self.base_url}/api/tenant/{self.tenant_id}/{path}"

    def _request(
        self,
        method: str,
        path: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        url = self._url(path)
        resp = self._session.request(method, url, json=json, params=params, **kwargs)

        if resp.status_code == 401:
            raise TuskrAuthError(
                "Invalid or expired token",
                status_code=401,
                response_body=resp.text,
            )
        if resp.status_code == 403:
            raise TuskrAPIError(
                "Forbidden: insufficient privileges",
                status_code=403,
                response_body=resp.text,
            )
        if resp.status_code == 429:
            raise TuskrRateLimitError(
                "Rate limit exceeded (10 req/s or hourly limit)",
                status_code=429,
                response_body=resp.text,
            )

        if resp.status_code >= 400:
            raise TuskrAPIError(
                resp.text or f"HTTP {resp.status_code}",
                status_code=resp.status_code,
                response_body=resp.text,
            )

        if resp.status_code == 204 or not resp.content:
            return {}

        return resp.json()

    def _post_data(self, path: str, data: BaseModel) -> dict[str, Any]:
        return self._request("POST", path, json={"data": _dump_request(data)})

    def _delete_data(self, path: str, data: BaseModel) -> dict[str, Any]:
        return self._request("DELETE", path, json={"data": _dump_request(data)})

    # -------------------------------------------------------------------------
    # Projects
    # -------------------------------------------------------------------------

    def create_project(self, request: CreateProjectRequest) -> dict[str, Any]:
        """
        Create a blank project.

        :param request: CreateProjectRequest with name, team (email → role), and optional fields.
        """
        return self._post_data("project", request)

    def list_projects(self, request: ListProjectsRequest) -> dict[str, Any]:
        """List projects. Optional filters: name (substring), status (active/archived)."""
        return self._request("GET", "project", params=request.to_params())

    # -------------------------------------------------------------------------
    # Test cases
    # -------------------------------------------------------------------------

    def add_test_case(self, request: AddTestCaseRequest) -> dict[str, Any]:
        """Add a test case to an existing suite and section."""
        return self._post_data("test-case", request)

    def upsert_test_case(self, request: UpsertTestCaseRequest) -> dict[str, Any]:
        """
        Update a test case if it exists, else create it.
        Specify either test_case_id (for update) or external_id (for upsert by external ID).
        """
        return self._post_data("test-case/upsert", request)

    def import_test_plan(self, request: ImportTestPlanRequest) -> dict[str, Any]:
        """
        Import your test plan (creates test suites, sections, and test cases).
        request.test_cases is a list of AddTestCaseRequest.
        """
        return self._post_data("test-case/import", request)

    def list_test_cases(self, request: ListTestCasesRequest) -> dict[str, Any]:
        """List test cases in a project. request.project is required."""
        return self._request("GET", "test-case", params=request.to_params())

    # -------------------------------------------------------------------------
    # Test suites
    # -------------------------------------------------------------------------

    def list_test_suites(self, request: ListTestSuitesRequest) -> dict[str, Any]:
        """List test suites and their sections in a project. request.project is required."""
        return self._request("GET", "test-suite", params=request.to_params())

    # -------------------------------------------------------------------------
    # Test runs
    # -------------------------------------------------------------------------

    def create_test_run(self, request: CreateTestRunRequest) -> dict[str, Any]:
        """
        Create a test run. test_case_inclusion_type: "ALL" or "SPECIFIC".
        If SPECIFIC, request.test_cases (IDs, keys, or names) is required.
        """
        return self._post_data("test-run", request)

    def copy_test_run(self, request: CopyTestRunRequest) -> dict[str, Any]:
        """Create a copy of an existing test run (by ID or name)."""
        return self._post_data("test-run/copy", request)

    def get_test_run_results(
        self,
        test_run_id: str,
        request: GetTestRunResultsRequest,
    ) -> dict[str, Any]:
        """
        Fetch test cases and their results in a test run.
        request.status: comma-separated result statuses (e.g. "RETEST,FAILED").
        request.test_cases: IDs, keys, or names.
        """
        return self._request(
            "GET",
            f"test-run/{test_run_id}/results",
            params=request.to_params(),
        )

    def delete_test_runs(self, request: DeleteTestRunsRequest) -> dict[str, Any]:
        """
        Delete test runs by criteria. At least one of projects, name_starts_with,
        or older_than_days must be provided.
        """
        return self._delete_data("test-run/bulk", request)

    def list_test_runs(self, request: ListTestRunsRequest) -> dict[str, Any]:
        """List test runs in a project. request.project is required."""
        return self._request("GET", "test-run", params=request.to_params())

    def bulk_export_test_runs(
        self, request: BulkExportTestRunsRequest
    ) -> dict[str, Any]:
        """Bulk export test runs with optional test case details. request.project is required."""
        return self._request("GET", "test-run/bulk-export", params=request.to_params())

    # -------------------------------------------------------------------------
    # Test run results
    # -------------------------------------------------------------------------

    def add_test_run_results(self, request: AddTestRunResultsRequest) -> dict[str, Any]:
        """
        Add results for test cases in a test run (bulk).
        status: result status key (e.g. PASSED, FAILED, RETEST).
        test_cases: list of IDs, keys, or names.
        """
        return self._post_data("test-run-result/bulk", request)

    def close(self) -> None:
        """Close the underlying HTTP session."""
        self._session.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
