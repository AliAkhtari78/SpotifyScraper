"""Pure, hermetic tests for :func:`parse_account` over synthetic product-state.

The fixtures below are scrubbed and synthetic — no real ``accessToken``,
``clientId``, cookie, or PII. They mirror the live product-state contract: a flat
object with hyphenated keys (``product``, ``catalogue``, ``country``,
``on-demand``, ``preferred-locale``, ``selected-language``) where booleans may
arrive stringy.
"""

from __future__ import annotations

from typing import Any

import pytest

from spotify_scraper.api.parse_entities import parse_account
from spotify_scraper.models.account import Account

# A full, scrubbed Premium product-state body with stringy booleans.
PREMIUM_BODY: dict[str, Any] = {
    "product": "premium",
    "catalogue": "premium",
    "country": "CA",
    "on-demand": "1",
    "ads": "0",
    "is-standalone-audiobooks": "0",
    "preferred-locale": "en",
    "selected-language": "en",
    "multiuserplan-current-size": "1",
    "multiuserplan-member-type": "STANDALONE",
}


def test_full_premium_body_maps_every_field() -> None:
    account = parse_account(PREMIUM_BODY)
    assert account.product == "premium"
    assert account.catalogue == "premium"
    assert account.country == "CA"
    assert account.on_demand is True
    assert account.preferred_locale == "en"
    assert account.selected_language == "en"
    assert account.is_premium is True


def test_free_product_is_not_premium() -> None:
    account = parse_account({**PREMIUM_BODY, "product": "free"})
    assert account.product == "free"
    assert account.is_premium is False


def test_open_product_is_not_premium() -> None:
    account = parse_account({"product": "open", "country": "US"})
    assert account.is_premium is False
    assert account.country == "US"


def test_empty_body_yields_all_none() -> None:
    account = parse_account({})
    assert account == Account()
    assert account.product is None
    assert account.country is None
    assert account.on_demand is None
    assert account.is_premium is False


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("1", True),
        ("true", True),
        ("TRUE", True),
        (True, True),
        ("0", False),
        ("false", False),
        ("False", False),
        (False, False),
        ("maybe", None),
        (None, None),
        (2, None),
    ],
)
def test_on_demand_bool_coercion(raw: Any, expected: bool | None) -> None:
    account = parse_account({"product": "premium", "on-demand": raw})
    assert account.on_demand is expected


def test_missing_on_demand_key_is_none() -> None:
    account = parse_account({"product": "premium"})
    assert account.on_demand is None


def test_hyphenated_keys_map_to_snake_case() -> None:
    account = parse_account(
        {"preferred-locale": "fr-CA", "selected-language": "fr", "on-demand": "0"}
    )
    assert account.preferred_locale == "fr-CA"
    assert account.selected_language == "fr"
    assert account.on_demand is False


def test_round_trip_excludes_is_premium() -> None:
    account = parse_account(PREMIUM_BODY)
    data = account.to_dict()
    assert "is_premium" not in data
    assert set(data) == {
        "product",
        "catalogue",
        "country",
        "on_demand",
        "preferred_locale",
        "selected_language",
    }
    assert Account.from_dict(data) == account
