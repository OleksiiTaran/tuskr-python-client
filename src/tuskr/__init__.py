"""
Tuskr Python client — access the Tuskr test management REST API from Python.
"""

from tuskr.client import TuskrClient
from tuskr.exceptions import (
    TuskrAPIError,
    TuskrAuthError,
    TuskrRateLimitError,
)
from tuskr.models import (
    AddTestCaseRequest,
    AddTestRunResultsRequest,
    BulkExportTestRunsRequest,
    CopyTestRunRequest,
    CreateProjectRequest,
    CreateTestRunRequest,
    DeleteTestRunsRequest,
    GetTestRunResultsRequest,
    ImportTestPlanRequest,
    ListProjectsRequest,
    ListTestCasesRequest,
    ListTestRunsRequest,
    ListTestSuitesRequest,
    UpsertTestCaseRequest,
)

__version__ = "0.1.0"
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
    "TuskrClient",
    "TuskrAPIError",
    "TuskrAuthError",
    "TuskrRateLimitError",
    "UpsertTestCaseRequest",
]
