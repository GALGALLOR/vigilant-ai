# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["MemoryUpdateMemoryResponse"]


class MemoryUpdateMemoryResponse(BaseModel):
    """Response after updating a memory"""

    id: str
    """ID of the newly created memory version"""

    created_at: str = FieldInfo(alias="createdAt")
    """When this memory version was created"""

    memory: str
    """The content of the new memory version"""

    parent_memory_id: Optional[str] = FieldInfo(alias="parentMemoryId", default=None)
    """ID of the memory this version updates"""

    root_memory_id: Optional[str] = FieldInfo(alias="rootMemoryId", default=None)
    """ID of the first memory in this version chain"""

    version: float
    """Version number of this memory entry"""
