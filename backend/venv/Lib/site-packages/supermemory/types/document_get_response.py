# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["DocumentGetResponse"]


class DocumentGetResponse(BaseModel):
    """Document object"""

    id: str
    """Unique identifier of the document."""

    connection_id: Optional[str] = FieldInfo(alias="connectionId", default=None)
    """Optional ID of connection the document was created from.

    This is useful for identifying the source of the document.
    """

    content: Optional[str] = None
    """The content to extract and process into a document.

    This can be a URL to a website, a PDF, an image, or a video.

    Plaintext: Any plaintext format

    URL: A URL to a website, PDF, image, or video

    We automatically detect the content type from the url's response format.
    """

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

    og_image: Optional[str] = FieldInfo(alias="ogImage", default=None)

    raw: object
    """Raw content of the document"""

    source: Optional[str] = None
    """Source of the document"""

    spatial_point: object = FieldInfo(alias="spatialPoint")

    status: Literal["unknown", "queued", "extracting", "chunking", "embedding", "indexing", "done", "failed"]
    """Status of the document"""

    summary: Optional[str] = None
    """Summary of the document content"""

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

    url: Optional[str] = None
    """URL of the document"""
