# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["MemoryForgetResponse"]


class MemoryForgetResponse(BaseModel):
    """Response after forgetting a memory"""

    id: str
    """ID of the memory that was forgotten"""

    forgotten: bool
    """Indicates the memory was successfully forgotten"""
