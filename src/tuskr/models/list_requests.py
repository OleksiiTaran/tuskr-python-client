"""Pydantic models for Tuskr API list/get query parameters.

Each model has to_params() returning the query dict for GET requests.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict


class _ListBase(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )


# -----------------------------------------------------------------------------
# List projects
# -----------------------------------------------------------------------------


class ListProjectsRequest(_ListBase):
    """Query params for « List projects »."""

    name: str | None = None
    status: str | None = None  # active | archived
    page: int = 1

    def to_params(self) -> dict[str, Any]:
        params: dict[str, Any] = {"page": self.page}
        if self.name is not None:
            params["filter[name]"] = self.name
        if self.status is not None:
            params["filter[status]"] = self.status
        return params


# -----------------------------------------------------------------------------
# List test cases
# -----------------------------------------------------------------------------


class ListTestCasesRequest(_ListBase):
    """Query params for « List test cases ». project is required."""

    project: str
    test_suite: str | None = None
    test_suite_section: str | None = None
    key: str | None = None
    test_case_type: str | None = None
    name: str | None = None
    custom_fields: dict[str, str | int | float | list[str]] | None = None
    page: int = 1

    def to_params(self) -> dict[str, Any]:
        params: dict[str, Any] = {"filter[project]": self.project, "page": self.page}
        if self.test_suite is not None:
            params["filter[testSuite]"] = self.test_suite
        if self.test_suite_section is not None:
            params["filter[testSuiteSection]"] = self.test_suite_section
        if self.key is not None:
            params["filter[key]"] = self.key
        if self.test_case_type is not None:
            params["filter[testCaseType]"] = self.test_case_type
        if self.name is not None:
            params["filter[name]"] = self.name
        if self.custom_fields is not None:
            for k, v in self.custom_fields.items():
                params[f"filter[customFields][{k}]"] = v
        return params


# -----------------------------------------------------------------------------
# List test suites
# -----------------------------------------------------------------------------


class ListTestSuitesRequest(_ListBase):
    """Query params for « List test suites and sections ». project is required."""

    project: str
    name: str | None = None
    page: int = 1

    def to_params(self) -> dict[str, Any]:
        params: dict[str, Any] = {"filter[project]": self.project, "page": self.page}
        if self.name is not None:
            params["filter[name]"] = self.name
        return params


# -----------------------------------------------------------------------------
# List test runs
# -----------------------------------------------------------------------------


class ListTestRunsRequest(_ListBase):
    """Query params for « List test runs ». project is required."""

    project: str
    name: str | None = None
    key: str | None = None
    status: str | None = None  # active | archived
    assigned_to: str | None = None
    page: int = 1

    def to_params(self) -> dict[str, Any]:
        params: dict[str, Any] = {"filter[project]": self.project, "page": self.page}
        if self.name is not None:
            params["filter[name]"] = self.name
        if self.key is not None:
            params["filter[key]"] = self.key
        if self.status is not None:
            params["filter[status]"] = self.status
        if self.assigned_to is not None:
            params["filter[assignedTo]"] = self.assigned_to
        return params


# -----------------------------------------------------------------------------
# Get test run results
# -----------------------------------------------------------------------------


class GetTestRunResultsRequest(_ListBase):
    """Query params for « Get results in a test run ». test_run_id is in the path."""

    status: str | None = None  # comma-separated, e.g. RETEST,FAILED
    test_cases: list[str] | None = None  # IDs, keys, or names
    page: int = 1

    def to_params(self) -> dict[str, Any]:
        params: dict[str, Any] = {"page": self.page}
        if self.status is not None:
            params["status"] = self.status
        if self.test_cases is not None:
            params["testCases"] = ",".join(self.test_cases)
        return params


# -----------------------------------------------------------------------------
# Bulk export test runs
# -----------------------------------------------------------------------------


class BulkExportTestRunsRequest(_ListBase):
    """Query params for « Bulk export test runs ». project is required."""

    project: str
    exclude_test_cases: bool | None = None
    assigned_to: str | None = None
    ids: list[str] | None = None
    status: str | None = None  # active | archived
    completion_status: str | None = None  # completed | incomplete
    page: int = 1

    def to_params(self) -> dict[str, Any]:
        params: dict[str, Any] = {"filter[project]": self.project, "page": self.page}
        if self.exclude_test_cases is not None:
            params["filter[excludeTestCases]"] = str(self.exclude_test_cases).lower()
        if self.assigned_to is not None:
            params["filter[assignedTo]"] = self.assigned_to
        if self.ids is not None:
            params["filter[ids]"] = ",".join(self.ids)
        if self.status is not None:
            params["filter[status]"] = self.status
        if self.completion_status is not None:
            params["filter[completionStatus]"] = self.completion_status
        return params
