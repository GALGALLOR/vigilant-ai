# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["DocumentDeleteBulkResponse", "Error"]


class Error(BaseModel):
    id: str

    error: str


class DocumentDeleteBulkResponse(BaseModel):
    """Response for bulk document deletion"""

    deleted_count: float = FieldInfo(alias="deletedCount")
    """Number of documents successfully deleted"""

    success: bool
    """Whether the bulk deletion was successful"""

    container_tags: Optional[List[str]] = FieldInfo(alias="containerTags", default=None)
    """
    Container tags that were processed (only applicable when deleting by container
    tags)
    """

    errors: Optional[List[Error]] = None
    """
    Array of errors for documents that couldn't be deleted (only applicable when
    deleting by IDs)
    """
