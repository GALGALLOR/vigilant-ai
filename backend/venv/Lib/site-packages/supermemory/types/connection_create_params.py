# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Optional
from typing_extensions import Annotated, TypedDict

from .._types import SequenceNotStr
from .._utils import PropertyInfo

__all__ = ["ConnectionCreateParams"]


class ConnectionCreateParams(TypedDict, total=False):
    container_tags: Annotated[SequenceNotStr[str], PropertyInfo(alias="containerTags")]

    document_limit: Annotated[int, PropertyInfo(alias="documentLimit")]

    metadata: Optional[Dict[str, Union[str, float, bool]]]

    redirect_url: Annotated[str, PropertyInfo(alias="redirectUrl")]
