# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["DocumentUploadFileResponse"]


class DocumentUploadFileResponse(BaseModel):
    id: str
    """Unique identifier of the document"""

    status: str
    """Status of the document"""
