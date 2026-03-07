# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import TypeAlias

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["ConnectionListDocumentsResponse", "ConnectionListDocumentsResponseItem"]


class ConnectionListDocumentsResponseItem(BaseModel):
    id: str

    created_at: str = FieldInfo(alias="createdAt")

    status: str

    summary: Optional[str] = None

    title: Optional[str] = None

    type: str

    updated_at: str = FieldInfo(alias="updatedAt")


ConnectionListDocumentsResponse: TypeAlias = List[ConnectionListDocumentsResponseItem]
