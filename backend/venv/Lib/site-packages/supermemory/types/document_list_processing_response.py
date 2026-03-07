# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["DocumentListProcessingResponse", "Document"]


class Document(BaseModel):
    id: str
    """Unique identifier of the document."""

    created_at: str = FieldInfo(alias="createdAt")
    """Creation timestamp"""

    custom_id: Optional[str] = FieldInfo(alias="customId", default=None)
    """Optional custom ID of the document.

    This could be an ID from your database that will uniquely identify this
    document.
    """

    metadata: Union[str, float, bool, Dict[str, object], List[object], None] = None
    """Optional metadata for the document.

    This is used to store additional information about the document. You can use
    this to store any additional information you need about the document. Metadata
    can be filtered through. Keys must be strings and are case sensitive. Values can
    be strings, numbers, or booleans. You cannot nest objects.
    """

    status: Literal["unknown", "queued", "extracting", "chunking", "embedding", "indexing", "done", "failed"]
    """Status of the document"""

    title: Optional[str] = None
    """Title of the document"""

    type: Literal[
        "text",
        "pdf",
        "tweet",
        "google_doc",
        "google_slide",
        "google_sheet",
        "image",
        "video",
        "notion_doc",
        "webpage",
        "onedrive",
        "github_markdown",
    ]
    """Type of the document"""

    updated_at: str = FieldInfo(alias="updatedAt")
    """Last update timestamp"""

    container_tags: Optional[List[str]] = FieldInfo(alias="containerTags", default=None)
    """Optional tags this document should be containerized by.

    This can be an ID for your user, a project ID, or any other identifier you wish
    to use to group documents.
    """


class DocumentListProcessingResponse(BaseModel):
    """List of documents currently being processed"""

    documents: List[Document]

    total_count: float = FieldInfo(alias="totalCount")
    """Total number of processing documents"""
