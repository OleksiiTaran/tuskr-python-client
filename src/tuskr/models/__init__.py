"""Pydantic models for Tuskr API requests (and optionally responses)."""

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

__all__ = [
    "AddTestCaseRequest",
    "AddTestRunResultsRequest",
    "BulkExportTestRunsRequest",
    "CopyTestRunRequest",
    "CreateProjectRequest",
    "CreateTestRunRequest",
    "DeleteTestRunsRequest",
    "GetTestRunResultsRequest",
    "ImportTestPlanRequest",
    "ListProjectsRequest",
    "ListTestCasesRequest",
    "ListTestRunsRequest",
    "ListTestSuitesRequest",
    "UpsertTestCaseRequest",
]
