# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._types import FileTypes
from .._utils import PropertyInfo

__all__ = ["DocumentUploadFileParams"]


class DocumentUploadFileParams(TypedDict, total=False):
    file: Required[FileTypes]
    """File to upload and process"""

    container_tags: Annotated[str, PropertyInfo(alias="containerTags")]
    """Optional container tags.

    Can be either a JSON string of an array (e.g., '["user_123", "project_123"]') or
    a single string (e.g., 'user_123'). Single strings will be automatically
    converted to an array.
    """

    file_type: Annotated[str, PropertyInfo(alias="fileType")]
    """Optional file type override to force specific processing behavior.

    Valid values: text, pdf, tweet, google_doc, google_slide, google_sheet, image,
    video, notion_doc, webpage, onedrive
    """

    metadata: str
    """Optional metadata for the document as a JSON string.

    This is used to store additional information about the document. Keys must be
    strings and values can be strings, numbers, or booleans.
    """

    mime_type: Annotated[str, PropertyInfo(alias="mimeType")]
    """Required when fileType is 'image' or 'video'.

    Specifies the exact MIME type to use (e.g., 'image/png', 'image/jpeg',
    'video/mp4', 'video/webm')
    """

    use_advanced_processing: Annotated[str, PropertyInfo(alias="useAdvancedProcessing")]
    """DEPRECATED: This field is no longer used.

    Advanced PDF processing is now automatic with our hybrid Mistral OCR + Gemini
    pipeline. This parameter will be accepted but ignored for backwards
    compatibility.
    """
