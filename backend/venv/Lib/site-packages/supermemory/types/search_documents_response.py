# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["SearchDocumentsResponse", "Result", "ResultChunk"]


class ResultChunk(BaseModel):
    """Matching content chunk"""

    content: str
    """Content of the matching chunk"""

    is_relevant: bool = FieldInfo(alias="isRelevant")
    """Whether this chunk is relevant to the query"""

    score: float
    """Similarity score for this chunk"""


class Result(BaseModel):
    chunks: List[ResultChunk]
    """Matching content chunks from the document"""

    created_at: str = FieldInfo(alias="createdAt")
    """Document creation date"""

    document_id: str = FieldInfo(alias="documentId")
    """ID of the matching document"""

    metadata: Optional[Dict[str, object]] = None
    """Document metadata"""

    score: float
    """Relevance score of the match"""

    title: Optional[str] = None
    """Document title"""

    type: Optional[str] = None
    """Document type"""

    updated_at: str = FieldInfo(alias="updatedAt")
    """Document last update date"""

    content: Optional[str] = None
    """Full document content (only included when includeFullDocs=true)"""

    summary: Optional[str] = None
    """Document summary"""


class SearchDocumentsResponse(BaseModel):
    results: List[Result]

    timing: float

    total: float
