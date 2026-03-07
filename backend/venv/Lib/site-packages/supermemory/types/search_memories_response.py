# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = [
    "SearchMemoriesResponse",
    "Result",
    "ResultChunk",
    "ResultContext",
    "ResultContextChild",
    "ResultContextParent",
    "ResultDocument",
]


class ResultChunk(BaseModel):
    content: str
    """Content of the chunk"""

    document_id: str = FieldInfo(alias="documentId")
    """ID of the document this chunk belongs to"""

    position: float
    """Position of chunk in the document (0-indexed)"""

    score: float
    """Similarity score between the query and chunk"""


class ResultContextChild(BaseModel):
    memory: str
    """The contextual memory content"""

    relation: Literal["updates", "extends", "derives"]
    """Relation type between this memory and its parent/child"""

    updated_at: str = FieldInfo(alias="updatedAt")
    """Contextual memory last update date"""

    metadata: Optional[Dict[str, object]] = None
    """Contextual memory metadata"""

    version: Optional[float] = None
    """
    Relative version distance from the primary memory (+1 for direct child, +2 for
    grand-child, etc.)
    """


class ResultContextParent(BaseModel):
    memory: str
    """The contextual memory content"""

    relation: Literal["updates", "extends", "derives"]
    """Relation type between this memory and its parent/child"""

    updated_at: str = FieldInfo(alias="updatedAt")
    """Contextual memory last update date"""

    metadata: Optional[Dict[str, object]] = None
    """Contextual memory metadata"""

    version: Optional[float] = None
    """
    Relative version distance from the primary memory (-1 for direct parent, -2 for
    grand-parent, etc.)
    """


class ResultContext(BaseModel):
    """Object containing arrays of parent and child contextual memories"""

    children: Optional[List[ResultContextChild]] = None

    parents: Optional[List[ResultContextParent]] = None


class ResultDocument(BaseModel):
    id: str
    """Document ID"""

    created_at: str = FieldInfo(alias="createdAt")
    """Document creation date"""

    updated_at: str = FieldInfo(alias="updatedAt")
    """Document last update date"""

    metadata: Optional[Dict[str, object]] = None
    """Document metadata (only included when documents=true)"""

    summary: Optional[str] = None
    """Document summary (only included when summaries=true)"""

    title: Optional[str] = None
    """Document title (only included when documents=true)"""

    type: Optional[str] = None
    """Document type (only included when documents=true)"""


class Result(BaseModel):
    id: str
    """Memory entry ID or chunk ID"""

    metadata: Optional[Dict[str, object]] = None
    """Memory metadata"""

    similarity: float
    """Similarity score between the query and memory entry"""

    updated_at: str = FieldInfo(alias="updatedAt")
    """Memory last update date"""

    chunk: Optional[str] = None
    """The chunk content (only present for chunk results from hybrid search)"""

    chunks: Optional[List[ResultChunk]] = None
    """Relevant chunks from associated documents (only included when chunks=true)"""

    context: Optional[ResultContext] = None
    """Object containing arrays of parent and child contextual memories"""

    documents: Optional[List[ResultDocument]] = None
    """Associated documents for this memory entry"""

    memory: Optional[str] = None
    """The memory content (only present for memory results)"""

    version: Optional[float] = None
    """Version number of this memory entry"""


class SearchMemoriesResponse(BaseModel):
    results: List[Result]
    """Array of matching memory entries and chunks with similarity scores.

    Contains memory results when searchMode='memories', both memory and chunk
    results when searchMode='hybrid', or only chunk results when
    searchMode='documents'. Memory results have 'memory' field, chunk results have
    'chunk' field. BACKWARD COMPATIBILITY: When using deprecated
    include.chunks=true, only memory results are returned with chunks embedded in
    them (old format).
    """

    timing: float
    """Search execution time in milliseconds"""

    total: float
    """Total number of results returned"""
