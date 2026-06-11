"""Shared serialization base for SpotifyScraper model dataclasses."""

from __future__ import annotations

import dataclasses
import types
from datetime import datetime
from typing import Any, TypeVar, Union, get_args, get_origin, get_type_hints

T = TypeVar("T", bound="ModelBase")


class ModelBase:
    """Base class giving frozen dataclass models ``to_dict`` / ``from_dict``.

    Both methods are implemented once via :func:`dataclasses.fields`
    reflection over the concrete subclass, so subclasses define fields only.
    """

    __slots__ = ()

    def to_dict(self) -> dict[str, Any]:
        """Return the model as a dict containing only JSON-safe primitives.

        Nested models become dicts, tuples become lists, and ``datetime``
        values become ISO-8601 strings.
        """
        fields = dataclasses.fields(self)  # type: ignore[arg-type]
        return {f.name: _serialize(getattr(self, f.name)) for f in fields}

    @classmethod
    def from_dict(cls: type[T], data: dict[str, Any]) -> T:
        """Build an instance from a dict as produced by :meth:`to_dict`.

        Args:
            data: Field values keyed by field name; missing keys fall back
                to the field defaults.

        Returns:
            A new instance of the concrete model class.
        """
        hints = get_type_hints(cls)
        fields = dataclasses.fields(cls)  # type: ignore[arg-type]
        kwargs = {
            f.name: _deserialize(hints[f.name], data[f.name]) for f in fields if f.name in data
        }
        return cls(**kwargs)


def _serialize(value: object) -> Any:
    if isinstance(value, ModelBase):
        return value.to_dict()
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, tuple):
        return [_serialize(item) for item in value]
    return value


def _deserialize(annotation: Any, value: Any) -> Any:
    if value is None:
        return None
    origin = get_origin(annotation)
    if origin is Union or origin is types.UnionType:
        inner = next(arg for arg in get_args(annotation) if arg is not type(None))
        return _deserialize(inner, value)
    if origin is tuple:
        item_type = get_args(annotation)[0]
        return tuple(_deserialize(item_type, item) for item in value)
    if isinstance(annotation, type) and issubclass(annotation, ModelBase):
        return annotation.from_dict(value)
    if annotation is datetime:
        return datetime.fromisoformat(value)
    return value
