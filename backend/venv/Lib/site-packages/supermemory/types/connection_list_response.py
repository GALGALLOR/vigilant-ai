# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from typing_extensions import TypeAlias

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["ConnectionListResponse", "ConnectionListResponseItem"]


class ConnectionListResponseItem(BaseModel):
    id: str

    created_at: str = FieldInfo(alias="createdAt")

    provider: str

    container_tags: Optional[List[str]] = FieldInfo(alias="containerTags", default=None)

    document_limit: Optional[float] = FieldInfo(alias="documentLimit", default=None)

    email: Optional[str] = None

    expires_at: Optional[str] = FieldInfo(alias="expiresAt", default=None)

    metadata: Optional[Dict[str, object]] = None


ConnectionListResponse: TypeAlias = List[ConnectionListResponseItem]
