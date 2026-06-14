"""Sans-io result type for the plural batch helpers.

:class:`BatchItem` is the load-bearing partial-failure wrapper returned by the
plural ``get_*s`` helpers on both client facades. It echoes the input ``value``
back alongside either the fetched model (``result``) or the captured library
error (``error``), so a single dead or malformed input never aborts the batch.

This is a *control wrapper*, not Spotify data, so it deliberately carries no
``to_dict()`` — the JSON-safe rule applies to entity models, not to this.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

_T = TypeVar("_T")


@dataclass(frozen=True, slots=True)
class BatchItem(Generic[_T]):
    """One ordered, index-aligned outcome from a plural batch helper.

    Exactly one of ``result`` / ``error`` is populated: the model on success,
    or the captured :class:`~spotify_scraper.errors.SpotifyScraperError` on
    failure. The input ``value`` is echoed back so callers can correlate the
    outcome with the input even after reordering or deduplication.

    Attributes:
        value: The input URL, URI, or ID, echoed back.
        result: The fetched model on success, else ``None``.
        error: The captured exception on failure, else ``None``.
    """

    value: str
    result: _T | None = None
    error: Exception | None = None

    @property
    def ok(self) -> bool:
        """Whether the fetch succeeded (``error is None``)."""
        return self.error is None

    def unwrap(self) -> _T:
        """Return the model on success, or re-raise the captured error.

        Returns:
            The fetched model when this item succeeded.

        Raises:
            Exception: The captured error when this item failed.
        """
        if self.error is not None:
            raise self.error
        assert self.result is not None  # noqa: S101
        return self.result
