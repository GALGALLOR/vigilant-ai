# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union
from typing_extensions import Annotated, TypedDict

from .._types import SequenceNotStr
from .._utils import PropertyInfo

__all__ = ["DocumentUpdateParams"]


class DocumentUpdateParams(TypedDict, total=False):
    container_tag: Annotated[str, PropertyInfo(alias="containerTag")]
    """Optional tag this document should be containerized by.

    This can be an ID for your user, a project ID, or any other identifier you wish
    to use to group documents.
    """

    container_tags: Annotated[SequenceNotStr[str], PropertyInfo(alias="containerTags")]
    """
    (DEPRECATED: Use containerTag instead) Optional tags this document should be
    containerized by. This can be an ID for your user, a project ID, or any other
    identifier you wish to use to group documents.
    """

    content: str
    """The content to extract and process into a document.

    This can be a URL to a website, a PDF, an image, or a video.

    Plaintext: Any plaintext format

    URL: A URL to a website, PDF, image, or video

    We automatically detect the content type from the url's response format.
    """

    custom_id: Annotated[str, PropertyInfo(alias="customId")]
    """Optional custom ID of the document.

    This could be an ID from your database that will uniquely identify this
    document.
    """

    metadata: Dict[str, Union[str, float, bool, SequenceNotStr[str]]]
    """Optional metadata for the document.

    This is used to store additional information about the document. You can use
    this to store any additional information you need about the document. Metadata
    can be filtered through. Keys must be strings and are case sensitive. Values can
    be strings, numbers, or booleans. You cannot nest objects.
    """
