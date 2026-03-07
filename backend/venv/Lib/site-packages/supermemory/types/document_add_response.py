# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["DocumentAddResponse"]


class DocumentAddResponse(BaseModel):
    id: str
    """Unique identifier of the document"""

    status: str
    """Status of the document"""
