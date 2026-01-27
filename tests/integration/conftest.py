"""Fixtures for live Tuskr API integration tests.

Set env vars to run:
  TUSKR_TENANT_ID   – your tenant UUID (Top Menu → API)
  TUSKR_TOKEN       – your API token
  TUSKR_TEAM_EMAIL  – email for create_project team (e.g. your account email)
"""

import os

import pytest

from tuskr import TuskrClient


def _env(name: str) -> str | None:
    return os.environ.get(name) or None


@pytest.fixture(scope="module")
def tuskr_env():
    tenant = _env("TUSKR_TENANT_ID")
    token = _env("TUSKR_TOKEN")
    email = _env("TUSKR_TEAM_EMAIL")
    if not tenant or not token:
        pytest.skip(
            "Set TUSKR_TENANT_ID and TUSKR_TOKEN to run integration tests"
        )
    if not email:
        pytest.skip(
            "Set TUSKR_TEAM_EMAIL (your account email) for create_project tests"
        )
    return {"tenant_id": tenant, "token": token, "team_email": email}


@pytest.fixture(scope="module")
def live_client(tuskr_env):
    return TuskrClient(
        tenant_id=tuskr_env["tenant_id"],
        token=tuskr_env["token"],
    )
