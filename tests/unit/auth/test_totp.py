"""Tests for Spotify's TOTP token-exchange scheme."""

from __future__ import annotations

from spotify_scraper.auth.totp import TOTP_SECRETS, generate, totp_key

# Frozen known-answer vector, computed once from the pinned newest secret.
_SECRET = ',7/*F("rLJ2oxaKL^f+E1xvP@N'  # noqa: S105 — a TOTP secret test vector
_TIMESTAMP = 1_700_000_000
_EXPECTED_CODE = "371599"


def test_secrets_are_newest_first() -> None:
    versions = [version for version, _ in TOTP_SECRETS]
    assert versions == sorted(versions, reverse=True)
    assert versions[0] == 61


def test_totp_key_is_xor_encoded() -> None:
    # charCodeAt(0) of ',' is 44; 44 XOR (0 % 33 + 9) == 44 XOR 9 == 37.
    assert totp_key(",").decode().startswith("37")


def test_generate_known_vector() -> None:
    assert generate(_SECRET, _TIMESTAMP) == _EXPECTED_CODE


def test_generate_is_six_digits() -> None:
    code = generate(_SECRET, _TIMESTAMP + 31)
    assert len(code) == 6
    assert code.isdigit()


def test_generate_stable_within_period() -> None:
    # The TOTP period is 30 s; codes inside one window are identical. Align to a
    # window boundary so the +29 offset cannot spill into the next window.
    window_start = (_TIMESTAMP // 30) * 30
    assert generate(_SECRET, window_start) == generate(_SECRET, window_start + 29)


def test_generate_changes_across_periods() -> None:
    window_start = (_TIMESTAMP // 30) * 30
    assert generate(_SECRET, window_start) != generate(_SECRET, window_start + 30)
