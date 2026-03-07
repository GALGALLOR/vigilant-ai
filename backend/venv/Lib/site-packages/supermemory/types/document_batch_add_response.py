# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import TypeAlias

from .._models import BaseModel

__all__ = ["DocumentBatchAddResponse", "DocumentBatchAddResponseItem"]


class DocumentBatchAddResponseItem(BaseModel):
    id: str
    """Unique identifier of the document"""

    status: str
    """Status of the document"""


DocumentBatchAddResponse: TypeAlias = List[DocumentBatchAddResponseItem]
