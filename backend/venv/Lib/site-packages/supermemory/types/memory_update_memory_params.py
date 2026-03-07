# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union
from typing_extensions import Required, Annotated, TypedDict

from .._types import SequenceNotStr
from .._utils import PropertyInfo

__all__ = ["MemoryUpdateMemoryParams"]


class MemoryUpdateMemoryParams(TypedDict, total=False):
    container_tag: Required[Annotated[str, PropertyInfo(alias="containerTag")]]
    """Container tag / space identifier. Required to scope the operation."""

    new_content: Required[Annotated[str, PropertyInfo(alias="newContent")]]
    """The new content that will replace the existing memory"""

    id: str
    """ID of the memory entry to operate on"""

    content: str
    """Exact content match of the memory entry to operate on.

    Use this when you don't have the ID.
    """

    metadata: Dict[str, Union[str, float, bool, SequenceNotStr[str]]]
    """Optional metadata. If not provided, inherits from the previous version."""
