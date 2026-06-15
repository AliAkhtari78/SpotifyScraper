"""The authenticated account's product-state model.

:class:`Account` mirrors Spotify's flat ``melody/v1/product_state`` body. Every
field is ``| None`` because the body is per-account and Spotify may omit any key.
The derived :attr:`Account.is_premium` is a property (not a stored field), so it
is excluded from :meth:`~spotify_scraper.models.base.ModelBase.to_dict` and the
serialized form stays a faithful mirror of the wire body.
"""

from __future__ import annotations

from dataclasses import dataclass

from spotify_scraper.models.base import ModelBase


@dataclass(frozen=True, slots=True)
class Account(ModelBase):
    """The logged-in account's product tier and locale, from product-state.

    All fields are ``| None`` because the flat product-state body makes each
    key independently optional. ``is_premium`` is a derived ``@property`` rather
    than a stored field, so it is not part of ``dataclasses.fields()`` and is
    therefore absent from :meth:`to_dict` (and the ``from_dict`` round-trip).
    """

    product: str | None = None
    catalogue: str | None = None
    country: str | None = None
    on_demand: bool | None = None
    preferred_locale: str | None = None
    selected_language: str | None = None

    @property
    def is_premium(self) -> bool:
        """Return ``True`` when the account's product tier is Premium.

        This is derived from :attr:`product` (``== "premium"``); it is not a
        wire field and is intentionally absent from :meth:`to_dict`.
        """
        return self.product == "premium"
