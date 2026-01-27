"""Pydantic request models for Tuskr API payloads.

All models use camelCase aliases for JSON serialization to match the API.
Use model_dump(exclude_none=True, by_alias=True) when sending.
"""

from typing import Any, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


def _to_camel(name: str) -> str:
    parts = name.split("_")
    return parts[0].lower() + "".join(p.capitalize() for p in parts[1:])


def _dump(req: BaseModel) -> dict[str, Any]:
    """Serialize a request model to API-ready dict (camelCase, exclude None)."""
    return req.model_dump(exclude_none=True, by_alias=True)


# Re-export for client use
dump_request = _dump


class _TuskrBase(BaseModel):
    model_config = ConfigDict(
        alias_generator=_to_camel,
        populate_by_name=True,
        str_strip_whitespace=True,
        extra="forbid",
    )


# -----------------------------------------------------------------------------
# Projects
# -----------------------------------------------------------------------------


class CreateProjectRequest(_TuskrBase):
    """Request body for creating a project."""

    name: str
    team: dict[str, str]  # email -> role; at least one required
    status: str = "active"  # "active" | "archived"
    description: str | None = None

    @model_validator(mode="after")
    def check_team_non_empty(self) -> Self:
        if not self.team:
            raise ValueError("team must contain at least one email -> role")
        return self
    external_id: str | None = None
    integration_data: str | None = None
    issue_url_template: str | None = None
    reference_url_template: str | None = None


# -----------------------------------------------------------------------------
# Test cases
# -----------------------------------------------------------------------------


class AddTestCaseRequest(_TuskrBase):
    """Request body for adding a single test case."""

    project: str
    test_suite: str
    test_suite_section: str
    name: str
    description: str | None = None
    test_case_type: str | None = None
    estimated_time_in_minutes: int | None = None
    custom_fields: dict[str, Any] | None = None


class UpsertTestCaseOptions(_TuskrBase):
    """Options for upsert test case (create missing suite/section)."""

    create_missing_suite: bool = False
    create_missing_section: bool = False


class UpsertTestCaseRequest(_TuskrBase):
    """Request body for upserting a test case (update or create by id/externalId)."""

    project: str
    name: str
    test_case_id: str | None = Field(None, alias="id")
    external_id: str | None = None
    test_suite: str | None = None
    test_suite_section: str | None = None
    description: str | None = None
    test_case_type: str | None = None
    estimated_time_in_minutes: int | None = None
    custom_fields: dict[str, Any] | None = None
    options: UpsertTestCaseOptions = UpsertTestCaseOptions()


class ImportTestPlanOptions(_TuskrBase):
    """Options for import test plan (create missing suites/sections)."""

    create_missing_suites: bool = False
    create_missing_sections: bool = False


class ImportTestPlanRequest(_TuskrBase):
    """Request body for « Import your test plan » (creates suites, sections, test cases)."""

    project: str
    test_cases: list[AddTestCaseRequest]  # API key: testCases
    options: ImportTestPlanOptions = ImportTestPlanOptions()


# -----------------------------------------------------------------------------
# Test runs
# -----------------------------------------------------------------------------


class CreateTestRunRequest(_TuskrBase):
    """Request body for creating a test run."""

    project: str
    name: str
    test_case_inclusion_type: str = "ALL"  # ALL | SPECIFIC
    test_cases: list[str] | None = None  # required if SPECIFIC
    description: str | None = None
    deadline: str | None = None
    assigned_to: str | None = None

    @model_validator(mode="after")
    def check_specific_has_test_cases(self) -> Self:
        if self.test_case_inclusion_type == "SPECIFIC" and not self.test_cases:
            msg = "test_cases is required when test_case_inclusion_type is SPECIFIC"
            raise ValueError(msg)
        return self


class CopyTestRunRequest(_TuskrBase):
    """Request body for copying a test run."""

    test_run: str
    name: str | None = None
    description: str | None = None
    deadline: str | None = None
    assigned_to: str | None = None


class DeleteTestRunsRequest(_TuskrBase):
    """Request body for bulk-deleting test runs. At least one filter required."""

    projects: list[str] | None = None
    name_starts_with: str | None = None
    older_than_days: int | float | None = None
    purge: bool = False

    @model_validator(mode="after")
    def check_at_least_one_filter(self) -> Self:
        if all(
            x is None
            for x in (self.projects, self.name_starts_with, self.older_than_days)
        ):
            msg = "At least one of projects, name_starts_with, or older_than_days is required"
            raise ValueError(msg)
        return self


# -----------------------------------------------------------------------------
# Test run results
# -----------------------------------------------------------------------------


class AddTestRunResultsRequest(_TuskrBase):
    """Request body for « Add results for test cases in a test run » (bulk)."""

    test_run: str
    test_cases: list[str]
    status: str  # e.g. PASSED, FAILED, RETEST
    comments: str | None = None
    time_spent_in_minutes: int | None = None
    assigned_to: str | None = None
    custom_fields: dict[str, Any] | None = None
