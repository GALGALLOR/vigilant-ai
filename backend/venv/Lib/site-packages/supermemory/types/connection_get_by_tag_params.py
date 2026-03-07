# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._types import SequenceNotStr
from .._utils import PropertyInfo

__all__ = ["ConnectionGetByTagParams"]


class ConnectionGetByTagParams(TypedDict, total=False):
    container_tags: Required[Annotated[SequenceNotStr[str], PropertyInfo(alias="containerTags")]]
    """Comma-separated list of container tags to filter connection by"""
