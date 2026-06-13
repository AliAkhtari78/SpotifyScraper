"""Live smoke test for the CLI (network-dependent)."""

from __future__ import annotations

import json

import pytest
from typer.testing import CliRunner

from spotify_scraper.cli.main import app

runner = CliRunner()


@pytest.mark.live
def test_cli_track_live() -> None:
    result = runner.invoke(app, ["track", "4uLU6hMCjMI75M1A2tKUQC"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.stdout)
    assert payload["name"] == "Never Gonna Give You Up"
    assert payload["id"] == "4uLU6hMCjMI75M1A2tKUQC"
