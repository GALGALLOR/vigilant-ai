# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["MemoryForgetParams"]


class MemoryForgetParams(TypedDict, total=False):
    container_tag: Required[Annotated[str, PropertyInfo(alias="containerTag")]]
    """Container tag / space identifier. Required to scope the operation."""

    id: str
    """ID of the memory entry to operate on"""

    content: str
    """Exact content match of the memory entry to operate on.

    Use this when you don't have the ID.
    """

    reason: str
    """Optional reason for forgetting this memory"""
