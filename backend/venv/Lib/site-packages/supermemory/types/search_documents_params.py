# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from .._types import SequenceNotStr
from .._utils import PropertyInfo

__all__ = [
    "SearchDocumentsParams",
    "Filters",
    "FiltersOr",
    "FiltersOrOr",
    "FiltersOrOrUnionMember0",
    "FiltersOrOrOr",
    "FiltersOrOrOrOr",
    "FiltersOrOrOrOrUnionMember0",
    "FiltersOrOrOrOrOr",
    "FiltersOrOrOrOrOrOr",
    "FiltersOrOrOrOrOrOrUnionMember0",
    "FiltersOrOrOrOrOrOrOr",
    "FiltersOrOrOrOrOrOrOrOr",
    "FiltersOrOrOrOrOrOrOrOrUnionMember0",
    "FiltersOrOrOrOrOrOrOrOrOr",
    "FiltersOrOrOrOrOrOrOrOrOrOr",
    "FiltersOrOrOrOrOrOrOrOrOrOrUnionMember0",
    "FiltersOrOrOrOrOrOrOrOrOrOrOr",
    "FiltersOrOrOrOrOrOrOrOrOrOrOrOr",
    "FiltersOrOrOrOrOrOrOrOrOrOrAnd",
    "FiltersOrOrOrOrOrOrOrOrOrOrAndAnd",
    "FiltersOrOrOrOrOrOrOrOrAnd",
    "FiltersOrOrOrOrOrOrOrOrAndAnd",
    "FiltersOrOrOrOrOrOrOrOrAndAndUnionMember0",
    "FiltersOrOrOrOrOrOrOrOrAndAndOr",
    "FiltersOrOrOrOrOrOrOrOrAndAndOrOr",
    "FiltersOrOrOrOrOrOrOrOrAndAndAnd",
    "FiltersOrOrOrOrOrOrOrOrAndAndAndAnd",
    "FiltersOrOrOrOrOrOrAnd",
    "FiltersOrOrOrOrOrOrAndAnd",
    "FiltersOrOrOrOrOrOrAndAndUnionMember0",
    "FiltersOrOrOrOrOrOrAndAndOr",
    "FiltersOrOrOrOrOrOrAndAndOrOr",
    "FiltersOrOrOrOrOrOrAndAndOrOrUnionMember0",
    "FiltersOrOrOrOrOrOrAndAndOrOrOr",
    "FiltersOrOrOrOrOrOrAndAndOrOrOrOr",
    "FiltersOrOrOrOrOrOrAndAndOrOrAnd",
    "FiltersOrOrOrOrOrOrAndAndOrOrAndAnd",
    "FiltersOrOrOrOrOrOrAndAndAnd",
    "FiltersOrOrOrOrOrOrAndAndAndAnd",
    "FiltersOrOrOrOrOrOrAndAndAndAndUnionMember0",
    "FiltersOrOrOrOrOrOrAndAndAndAndOr",
    "FiltersOrOrOrOrOrOrAndAndAndAndOrOr",
    "FiltersOrOrOrOrOrOrAndAndAndAndAnd",
    "FiltersOrOrOrOrOrOrAndAndAndAndAndAnd",
    "FiltersOrOrOrOrAnd",
    "FiltersOrOrOrOrAndAnd",
    "FiltersOrOrOrOrAndAndUnionMember0",
    "FiltersOrOrOrOrAndAndOr",
    "FiltersOrOrOrOrAndAndOrOr",
    "FiltersOrOrOrOrAndAndOrOrUnionMember0",
    "FiltersOrOrOrOrAndAndOrOrOr",
    "FiltersOrOrOrOrAndAndOrOrOrOr",
    "FiltersOrOrOrOrAndAndOrOrOrOrUnionMember0",
    "FiltersOrOrOrOrAndAndOrOrOrOrOr",
    "FiltersOrOrOrOrAndAndOrOrOrOrOrOr",
    "FiltersOrOrOrOrAndAndOrOrOrOrAnd",
    "FiltersOrOrOrOrAndAndOrOrOrOrAndAnd",
    "FiltersOrOrOrOrAndAndOrOrAnd",
    "FiltersOrOrOrOrAndAndOrOrAndAnd",
    "FiltersOrOrOrOrAndAndOrOrAndAndUnionMember0",
    "FiltersOrOrOrOrAndAndOrOrAndAndOr",
    "FiltersOrOrOrOrAndAndOrOrAndAndOrOr",
    "FiltersOrOrOrOrAndAndOrOrAndAndAnd",
    "FiltersOrOrOrOrAndAndOrOrAndAndAndAnd",
    "FiltersOrOrOrOrAndAndAnd",
    "FiltersOrOrOrOrAndAndAndAnd",
    "FiltersOrOrOrOrAndAndAndAndUnionMember0",
    "FiltersOrOrOrOrAndAndAndAndOr",
    "FiltersOrOrOrOrAndAndAndAndOrOr",
    "FiltersOrOrOrOrAndAndAndAndOrOrUnionMember0",
    "FiltersOrOrOrOrAndAndAndAndOrOrOr",
    "FiltersOrOrOrOrAndAndAndAndOrOrOrOr",
    "FiltersOrOrOrOrAndAndAndAndOrOrAnd",
    "FiltersOrOrOrOrAndAndAndAndOrOrAndAnd",
    "FiltersOrOrOrOrAndAndAndAndAnd",
    "FiltersOrOrOrOrAndAndAndAndAndAnd",
    "FiltersOrOrOrOrAndAndAndAndAndAndUnionMember0",
    "FiltersOrOrOrOrAndAndAndAndAndAndOr",
    "FiltersOrOrOrOrAndAndAndAndAndAndOrOr",
    "FiltersOrOrOrOrAndAndAndAndAndAndAnd",
    "FiltersOrOrOrOrAndAndAndAndAndAndAndAnd",
    "FiltersOrOrAnd",
    "FiltersOrOrAndAnd",
    "FiltersOrOrAndAndUnionMember0",
    "FiltersOrOrAndAndOr",
    "FiltersOrOrAndAndOrOr",
    "FiltersOrOrAndAndOrOrUnionMember0",
    "FiltersOrOrAndAndOrOrOr",
    "FiltersOrOrAndAndOrOrOrOr",
    "FiltersOrOrAndAndOrOrOrOrUnionMember0",
    "FiltersOrOrAndAndOrOrOrOrOr",
    "FiltersOrOrAndAndOrOrOrOrOrOr",
    "FiltersOrOrAndAndOrOrOrOrOrOrUnionMember0",
    "FiltersOrOrAndAndOrOrOrOrOrOrOr",
    "FiltersOrOrAndAndOrOrOrOrOrOrOrOr",
    "FiltersOrOrAndAndOrOrOrOrOrOrAnd",
    "FiltersOrOrAndAndOrOrOrOrOrOrAndAnd",
    "FiltersOrOrAndAndOrOrOrOrAnd",
    "FiltersOrOrAndAndOrOrOrOrAndAnd",
    "FiltersOrOrAndAndOrOrOrOrAndAndUnionMember0",
    "FiltersOrOrAndAndOrOrOrOrAndAndOr",
    "FiltersOrOrAndAndOrOrOrOrAndAndOrOr",
    "FiltersOrOrAndAndOrOrOrOrAndAndAnd",
    "FiltersOrOrAndAndOrOrOrOrAndAndAndAnd",
    "FiltersOrOrAndAndOrOrAnd",
    "FiltersOrOrAndAndOrOrAndAnd",
    "FiltersOrOrAndAndOrOrAndAndUnionMember0",
    "FiltersOrOrAndAndOrOrAndAndOr",
    "FiltersOrOrAndAndOrOrAndAndOrOr",
    "FiltersOrOrAndAndOrOrAndAndOrOrUnionMember0",
    "FiltersOrOrAndAndOrOrAndAndOrOrOr",
    "FiltersOrOrAndAndOrOrAndAndOrOrOrOr",
    "FiltersOrOrAndAndOrOrAndAndOrOrAnd",
    "FiltersOrOrAndAndOrOrAndAndOrOrAndAnd",
    "FiltersOrOrAndAndOrOrAndAndAnd",
    "FiltersOrOrAndAndOrOrAndAndAndAnd",
    "FiltersOrOrAndAndOrOrAndAndAndAndUnionMember0",
    "FiltersOrOrAndAndOrOrAndAndAndAndOr",
    "FiltersOrOrAndAndOrOrAndAndAndAndOrOr",
    "FiltersOrOrAndAndOrOrAndAndAndAndAnd",
    "FiltersOrOrAndAndOrOrAndAndAndAndAndAnd",
    "FiltersOrOrAndAndAnd",
    "FiltersOrOrAndAndAndAnd",
    "FiltersOrOrAndAndAndAndUnionMember0",
    "FiltersOrOrAndAndAndAndOr",
    "FiltersOrOrAndAndAndAndOrOr",
    "FiltersOrOrAndAndAndAndOrOrUnionMember0",
    "FiltersOrOrAndAndAndAndOrOrOr",
    "FiltersOrOrAndAndAndAndOrOrOrOr",
    "FiltersOrOrAndAndAndAndOrOrOrOrUnionMember0",
    "FiltersOrOrAndAndAndAndOrOrOrOrOr",
    "FiltersOrOrAndAndAndAndOrOrOrOrOrOr",
    "FiltersOrOrAndAndAndAndOrOrOrOrAnd",
    "FiltersOrOrAndAndAndAndOrOrOrOrAndAnd",
    "FiltersOrOrAndAndAndAndOrOrAnd",
    "FiltersOrOrAndAndAndAndOrOrAndAnd",
    "FiltersOrOrAndAndAndAndOrOrAndAndUnionMember0",
    "FiltersOrOrAndAndAndAndOrOrAndAndOr",
    "FiltersOrOrAndAndAndAndOrOrAndAndOrOr",
    "FiltersOrOrAndAndAndAndOrOrAndAndAnd",
    "FiltersOrOrAndAndAndAndOrOrAndAndAndAnd",
    "FiltersOrOrAndAndAndAndAnd",
    "FiltersOrOrAndAndAndAndAndAnd",
    "FiltersOrOrAndAndAndAndAndAndUnionMember0",
    "FiltersOrOrAndAndAndAndAndAndOr",
    "FiltersOrOrAndAndAndAndAndAndOrOr",
    "FiltersOrOrAndAndAndAndAndAndOrOrUnionMember0",
    "FiltersOrOrAndAndAndAndAndAndOrOrOr",
    "FiltersOrOrAndAndAndAndAndAndOrOrOrOr",
    "FiltersOrOrAndAndAndAndAndAndOrOrAnd",
    "FiltersOrOrAndAndAndAndAndAndOrOrAndAnd",
    "FiltersOrOrAndAndAndAndAndAndAnd",
    "FiltersOrOrAndAndAndAndAndAndAndAnd",
    "FiltersOrOrAndAndAndAndAndAndAndAndUnionMember0",
    "FiltersOrOrAndAndAndAndAndAndAndAndOr",
    "FiltersOrOrAndAndAndAndAndAndAndAndOrOr",
    "FiltersOrOrAndAndAndAndAndAndAndAndAnd",
    "FiltersOrOrAndAndAndAndAndAndAndAndAndAnd",
    "FiltersAnd",
    "FiltersAndAnd",
    "FiltersAndAndUnionMember0",
    "FiltersAndAndOr",
    "FiltersAndAndOrOr",
    "FiltersAndAndOrOrUnionMember0",
    "FiltersAndAndOrOrOr",
    "FiltersAndAndOrOrOrOr",
    "FiltersAndAndOrOrOrOrUnionMember0",
    "FiltersAndAndOrOrOrOrOr",
    "FiltersAndAndOrOrOrOrOrOr",
    "FiltersAndAndOrOrOrOrOrOrUnionMember0",
    "FiltersAndAndOrOrOrOrOrOrOr",
    "FiltersAndAndOrOrOrOrOrOrOrOr",
    "FiltersAndAndOrOrOrOrOrOrOrOrUnionMember0",
    "FiltersAndAndOrOrOrOrOrOrOrOrOr",
    "FiltersAndAndOrOrOrOrOrOrOrOrOrOr",
    "FiltersAndAndOrOrOrOrOrOrOrOrAnd",
    "FiltersAndAndOrOrOrOrOrOrOrOrAndAnd",
    "FiltersAndAndOrOrOrOrOrOrAnd",
    "FiltersAndAndOrOrOrOrOrOrAndAnd",
    "FiltersAndAndOrOrOrOrOrOrAndAndUnionMember0",
    "FiltersAndAndOrOrOrOrOrOrAndAndOr",
    "FiltersAndAndOrOrOrOrOrOrAndAndOrOr",
    "FiltersAndAndOrOrOrOrOrOrAndAndAnd",
    "FiltersAndAndOrOrOrOrOrOrAndAndAndAnd",
    "FiltersAndAndOrOrOrOrAnd",
    "FiltersAndAndOrOrOrOrAndAnd",
    "FiltersAndAndOrOrOrOrAndAndUnionMember0",
    "FiltersAndAndOrOrOrOrAndAndOr",
    "FiltersAndAndOrOrOrOrAndAndOrOr",
    "FiltersAndAndOrOrOrOrAndAndOrOrUnionMember0",
    "FiltersAndAndOrOrOrOrAndAndOrOrOr",
    "FiltersAndAndOrOrOrOrAndAndOrOrOrOr",
    "FiltersAndAndOrOrOrOrAndAndOrOrAnd",
    "FiltersAndAndOrOrOrOrAndAndOrOrAndAnd",
    "FiltersAndAndOrOrOrOrAndAndAnd",
    "FiltersAndAndOrOrOrOrAndAndAndAnd",
    "FiltersAndAndOrOrOrOrAndAndAndAndUnionMember0",
    "FiltersAndAndOrOrOrOrAndAndAndAndOr",
    "FiltersAndAndOrOrOrOrAndAndAndAndOrOr",
    "FiltersAndAndOrOrOrOrAndAndAndAndAnd",
    "FiltersAndAndOrOrOrOrAndAndAndAndAndAnd",
    "FiltersAndAndOrOrAnd",
    "FiltersAndAndOrOrAndAnd",
    "FiltersAndAndOrOrAndAndUnionMember0",
    "FiltersAndAndOrOrAndAndOr",
    "FiltersAndAndOrOrAndAndOrOr",
    "FiltersAndAndOrOrAndAndOrOrUnionMember0",
    "FiltersAndAndOrOrAndAndOrOrOr",
    "FiltersAndAndOrOrAndAndOrOrOrOr",
    "FiltersAndAndOrOrAndAndOrOrOrOrUnionMember0",
    "FiltersAndAndOrOrAndAndOrOrOrOrOr",
    "FiltersAndAndOrOrAndAndOrOrOrOrOrOr",
    "FiltersAndAndOrOrAndAndOrOrOrOrAnd",
    "FiltersAndAndOrOrAndAndOrOrOrOrAndAnd",
    "FiltersAndAndOrOrAndAndOrOrAnd",
    "FiltersAndAndOrOrAndAndOrOrAndAnd",
    "FiltersAndAndOrOrAndAndOrOrAndAndUnionMember0",
    "FiltersAndAndOrOrAndAndOrOrAndAndOr",
    "FiltersAndAndOrOrAndAndOrOrAndAndOrOr",
    "FiltersAndAndOrOrAndAndOrOrAndAndAnd",
    "FiltersAndAndOrOrAndAndOrOrAndAndAndAnd",
    "FiltersAndAndOrOrAndAndAnd",
    "FiltersAndAndOrOrAndAndAndAnd",
    "FiltersAndAndOrOrAndAndAndAndUnionMember0",
    "FiltersAndAndOrOrAndAndAndAndOr",
    "FiltersAndAndOrOrAndAndAndAndOrOr",
    "FiltersAndAndOrOrAndAndAndAndOrOrUnionMember0",
    "FiltersAndAndOrOrAndAndAndAndOrOrOr",
    "FiltersAndAndOrOrAndAndAndAndOrOrOrOr",
    "FiltersAndAndOrOrAndAndAndAndOrOrAnd",
    "FiltersAndAndOrOrAndAndAndAndOrOrAndAnd",
    "FiltersAndAndOrOrAndAndAndAndAnd",
    "FiltersAndAndOrOrAndAndAndAndAndAnd",
    "FiltersAndAndOrOrAndAndAndAndAndAndUnionMember0",
    "FiltersAndAndOrOrAndAndAndAndAndAndOr",
    "FiltersAndAndOrOrAndAndAndAndAndAndOrOr",
    "FiltersAndAndOrOrAndAndAndAndAndAndAnd",
    "FiltersAndAndOrOrAndAndAndAndAndAndAndAnd",
    "FiltersAndAndAnd",
    "FiltersAndAndAndAnd",
    "FiltersAndAndAndAndUnionMember0",
    "FiltersAndAndAndAndOr",
    "FiltersAndAndAndAndOrOr",
    "FiltersAndAndAndAndOrOrUnionMember0",
    "FiltersAndAndAndAndOrOrOr",
    "FiltersAndAndAndAndOrOrOrOr",
    "FiltersAndAndAndAndOrOrOrOrUnionMember0",
    "FiltersAndAndAndAndOrOrOrOrOr",
    "FiltersAndAndAndAndOrOrOrOrOrOr",
    "FiltersAndAndAndAndOrOrOrOrOrOrUnionMember0",
    "FiltersAndAndAndAndOrOrOrOrOrOrOr",
    "FiltersAndAndAndAndOrOrOrOrOrOrOrOr",
    "FiltersAndAndAndAndOrOrOrOrOrOrAnd",
    "FiltersAndAndAndAndOrOrOrOrOrOrAndAnd",
    "FiltersAndAndAndAndOrOrOrOrAnd",
    "FiltersAndAndAndAndOrOrOrOrAndAnd",
    "FiltersAndAndAndAndOrOrOrOrAndAndUnionMember0",
    "FiltersAndAndAndAndOrOrOrOrAndAndOr",
    "FiltersAndAndAndAndOrOrOrOrAndAndOrOr",
    "FiltersAndAndAndAndOrOrOrOrAndAndAnd",
    "FiltersAndAndAndAndOrOrOrOrAndAndAndAnd",
    "FiltersAndAndAndAndOrOrAnd",
    "FiltersAndAndAndAndOrOrAndAnd",
    "FiltersAndAndAndAndOrOrAndAndUnionMember0",
    "FiltersAndAndAndAndOrOrAndAndOr",
    "FiltersAndAndAndAndOrOrAndAndOrOr",
    "FiltersAndAndAndAndOrOrAndAndOrOrUnionMember0",
    "FiltersAndAndAndAndOrOrAndAndOrOrOr",
    "FiltersAndAndAndAndOrOrAndAndOrOrOrOr",
    "FiltersAndAndAndAndOrOrAndAndOrOrAnd",
    "FiltersAndAndAndAndOrOrAndAndOrOrAndAnd",
    "FiltersAndAndAndAndOrOrAndAndAnd",
    "FiltersAndAndAndAndOrOrAndAndAndAnd",
    "FiltersAndAndAndAndOrOrAndAndAndAndUnionMember0",
    "FiltersAndAndAndAndOrOrAndAndAndAndOr",
    "FiltersAndAndAndAndOrOrAndAndAndAndOrOr",
    "FiltersAndAndAndAndOrOrAndAndAndAndAnd",
    "FiltersAndAndAndAndOrOrAndAndAndAndAndAnd",
    "FiltersAndAndAndAndAnd",
    "FiltersAndAndAndAndAndAnd",
    "FiltersAndAndAndAndAndAndUnionMember0",
    "FiltersAndAndAndAndAndAndOr",
    "FiltersAndAndAndAndAndAndOrOr",
    "FiltersAndAndAndAndAndAndOrOrUnionMember0",
    "FiltersAndAndAndAndAndAndOrOrOr",
    "FiltersAndAndAndAndAndAndOrOrOrOr",
    "FiltersAndAndAndAndAndAndOrOrOrOrUnionMember0",
    "FiltersAndAndAndAndAndAndOrOrOrOrOr",
    "FiltersAndAndAndAndAndAndOrOrOrOrOrOr",
    "FiltersAndAndAndAndAndAndOrOrOrOrAnd",
    "FiltersAndAndAndAndAndAndOrOrOrOrAndAnd",
    "FiltersAndAndAndAndAndAndOrOrAnd",
    "FiltersAndAndAndAndAndAndOrOrAndAnd",
    "FiltersAndAndAndAndAndAndOrOrAndAndUnionMember0",
    "FiltersAndAndAndAndAndAndOrOrAndAndOr",
    "FiltersAndAndAndAndAndAndOrOrAndAndOrOr",
    "FiltersAndAndAndAndAndAndOrOrAndAndAnd",
    "FiltersAndAndAndAndAndAndOrOrAndAndAndAnd",
    "FiltersAndAndAndAndAndAndAnd",
    "FiltersAndAndAndAndAndAndAndAnd",
    "FiltersAndAndAndAndAndAndAndAndUnionMember0",
    "FiltersAndAndAndAndAndAndAndAndOr",
    "FiltersAndAndAndAndAndAndAndAndOrOr",
    "FiltersAndAndAndAndAndAndAndAndOrOrUnionMember0",
    "FiltersAndAndAndAndAndAndAndAndOrOrOr",
    "FiltersAndAndAndAndAndAndAndAndOrOrOrOr",
    "FiltersAndAndAndAndAndAndAndAndOrOrAnd",
    "FiltersAndAndAndAndAndAndAndAndOrOrAndAnd",
    "FiltersAndAndAndAndAndAndAndAndAnd",
    "FiltersAndAndAndAndAndAndAndAndAndAnd",
    "FiltersAndAndAndAndAndAndAndAndAndAndUnionMember0",
    "FiltersAndAndAndAndAndAndAndAndAndAndOr",
    "FiltersAndAndAndAndAndAndAndAndAndAndOrOr",
    "FiltersAndAndAndAndAndAndAndAndAndAndAnd",
    "FiltersAndAndAndAndAndAndAndAndAndAndAndAnd",
]


class SearchDocumentsParams(TypedDict, total=False):
    q: Required[str]
    """Search query string"""

    categories_filter: Annotated[SequenceNotStr[str], PropertyInfo(alias="categoriesFilter")]
    """DEPRECATED: Optional category filters"""

    chunk_threshold: Annotated[float, PropertyInfo(alias="chunkThreshold")]
    """Threshold / sensitivity for chunk selection.

    0 is least sensitive (returns most chunks, more results), 1 is most sensitive
    (returns lesser chunks, accurate results)
    """

    container_tags: Annotated[SequenceNotStr[str], PropertyInfo(alias="containerTags")]
    """Optional tags this search should be containerized by.

    This can be an ID for your user, a project ID, or any other identifier you wish
    to use to filter documents.
    """

    doc_id: Annotated[str, PropertyInfo(alias="docId")]
    """Optional document ID to search within.

    You can use this to find chunks in a very large document.
    """

    document_threshold: Annotated[float, PropertyInfo(alias="documentThreshold")]
    """DEPRECATED: This field is no longer used in v3 search.

    The search now uses chunkThreshold only. This parameter will be ignored.
    """

    filters: Filters
    """Optional filters to apply to the search. Can be a JSON string or Query object."""

    include_full_docs: Annotated[bool, PropertyInfo(alias="includeFullDocs")]
    """If true, include full document in the response.

    This is helpful if you want a chatbot to know the full context of the document.
    """

    include_summary: Annotated[bool, PropertyInfo(alias="includeSummary")]
    """If true, include document summary in the response.

    This is helpful if you want a chatbot to know the full context of the document.
    """

    limit: int
    """Maximum number of results to return"""

    only_matching_chunks: Annotated[bool, PropertyInfo(alias="onlyMatchingChunks")]
    """If true, only return matching chunks without context.

    Normally, we send the previous and next chunk to provide more context for LLMs.
    If you only want the matching chunk, set this to true.
    """

    rerank: bool
    """If true, rerank the results based on the query.

    This is helpful if you want to ensure the most relevant results are returned.
    """

    rewrite_query: Annotated[bool, PropertyInfo(alias="rewriteQuery")]
    """If true, rewrites the query to make it easier to find documents.

    This increases the latency by about 400ms
    """


class FiltersOrOrUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrOrOrUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrOrOrOrOrUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrOrOrOrOrOrOrUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrOrOrOrOrOrOrOrOrUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrOrOrOrOrOrOrOrOrOrOr(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrOrOrOrOrOrOrOrOrOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersOrOrOrOrOrOrOrOrOrOrOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions"""


class FiltersOrOrOrOrOrOrOrOrOrOrAndAnd(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrOrOrOrOrOrOrOrOrAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersOrOrOrOrOrOrOrOrOrOrAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions"""


FiltersOrOrOrOrOrOrOrOrOrOr: TypeAlias = Union[
    FiltersOrOrOrOrOrOrOrOrOrOrUnionMember0, FiltersOrOrOrOrOrOrOrOrOrOrOr, FiltersOrOrOrOrOrOrOrOrOrOrAnd
]


class FiltersOrOrOrOrOrOrOrOrOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersOrOrOrOrOrOrOrOrOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions or nested expressions"""


class FiltersOrOrOrOrOrOrOrOrAndAndUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrOrOrOrOrOrOrAndAndOrOr(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrOrOrOrOrOrOrAndAndOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersOrOrOrOrOrOrOrOrAndAndOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions"""


class FiltersOrOrOrOrOrOrOrOrAndAndAndAnd(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrOrOrOrOrOrOrAndAndAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersOrOrOrOrOrOrOrOrAndAndAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions"""


FiltersOrOrOrOrOrOrOrOrAndAnd: TypeAlias = Union[
    FiltersOrOrOrOrOrOrOrOrAndAndUnionMember0, FiltersOrOrOrOrOrOrOrOrAndAndOr, FiltersOrOrOrOrOrOrOrOrAndAndAnd
]


class FiltersOrOrOrOrOrOrOrOrAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersOrOrOrOrOrOrOrOrAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions or nested expressions"""


FiltersOrOrOrOrOrOrOrOr: TypeAlias = Union[
    FiltersOrOrOrOrOrOrOrOrUnionMember0, FiltersOrOrOrOrOrOrOrOrOr, FiltersOrOrOrOrOrOrOrOrAnd
]


class FiltersOrOrOrOrOrOrOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersOrOrOrOrOrOrOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions or nested expressions"""


class FiltersOrOrOrOrOrOrAndAndUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrOrOrOrOrAndAndOrOrUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrOrOrOrOrAndAndOrOrOrOr(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrOrOrOrOrAndAndOrOrOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersOrOrOrOrOrOrAndAndOrOrOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions"""


class FiltersOrOrOrOrOrOrAndAndOrOrAndAnd(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrOrOrOrOrAndAndOrOrAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersOrOrOrOrOrOrAndAndOrOrAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions"""


FiltersOrOrOrOrOrOrAndAndOrOr: TypeAlias = Union[
    FiltersOrOrOrOrOrOrAndAndOrOrUnionMember0, FiltersOrOrOrOrOrOrAndAndOrOrOr, FiltersOrOrOrOrOrOrAndAndOrOrAnd
]


class FiltersOrOrOrOrOrOrAndAndOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersOrOrOrOrOrOrAndAndOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions or nested expressions"""


class FiltersOrOrOrOrOrOrAndAndAndAndUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrOrOrOrOrAndAndAndAndOrOr(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrOrOrOrOrAndAndAndAndOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersOrOrOrOrOrOrAndAndAndAndOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions"""


class FiltersOrOrOrOrOrOrAndAndAndAndAndAnd(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrOrOrOrOrAndAndAndAndAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersOrOrOrOrOrOrAndAndAndAndAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions"""


FiltersOrOrOrOrOrOrAndAndAndAnd: TypeAlias = Union[
    FiltersOrOrOrOrOrOrAndAndAndAndUnionMember0, FiltersOrOrOrOrOrOrAndAndAndAndOr, FiltersOrOrOrOrOrOrAndAndAndAndAnd
]


class FiltersOrOrOrOrOrOrAndAndAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersOrOrOrOrOrOrAndAndAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions or nested expressions"""


FiltersOrOrOrOrOrOrAndAnd: TypeAlias = Union[
    FiltersOrOrOrOrOrOrAndAndUnionMember0, FiltersOrOrOrOrOrOrAndAndOr, FiltersOrOrOrOrOrOrAndAndAnd
]


class FiltersOrOrOrOrOrOrAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersOrOrOrOrOrOrAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions or nested expressions"""


FiltersOrOrOrOrOrOr: TypeAlias = Union[FiltersOrOrOrOrOrOrUnionMember0, FiltersOrOrOrOrOrOrOr, FiltersOrOrOrOrOrOrAnd]


class FiltersOrOrOrOrOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersOrOrOrOrOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions or nested expressions"""


class FiltersOrOrOrOrAndAndUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrOrOrAndAndOrOrUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrOrOrAndAndOrOrOrOrUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrOrOrAndAndOrOrOrOrOrOr(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrOrOrAndAndOrOrOrOrOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersOrOrOrOrAndAndOrOrOrOrOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions"""


class FiltersOrOrOrOrAndAndOrOrOrOrAndAnd(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrOrOrAndAndOrOrOrOrAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersOrOrOrOrAndAndOrOrOrOrAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions"""


FiltersOrOrOrOrAndAndOrOrOrOr: TypeAlias = Union[
    FiltersOrOrOrOrAndAndOrOrOrOrUnionMember0, FiltersOrOrOrOrAndAndOrOrOrOrOr, FiltersOrOrOrOrAndAndOrOrOrOrAnd
]


class FiltersOrOrOrOrAndAndOrOrOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersOrOrOrOrAndAndOrOrOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions or nested expressions"""


class FiltersOrOrOrOrAndAndOrOrAndAndUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrOrOrAndAndOrOrAndAndOrOr(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrOrOrAndAndOrOrAndAndOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersOrOrOrOrAndAndOrOrAndAndOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions"""


class FiltersOrOrOrOrAndAndOrOrAndAndAndAnd(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrOrOrAndAndOrOrAndAndAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersOrOrOrOrAndAndOrOrAndAndAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions"""


FiltersOrOrOrOrAndAndOrOrAndAnd: TypeAlias = Union[
    FiltersOrOrOrOrAndAndOrOrAndAndUnionMember0, FiltersOrOrOrOrAndAndOrOrAndAndOr, FiltersOrOrOrOrAndAndOrOrAndAndAnd
]


class FiltersOrOrOrOrAndAndOrOrAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersOrOrOrOrAndAndOrOrAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions or nested expressions"""


FiltersOrOrOrOrAndAndOrOr: TypeAlias = Union[
    FiltersOrOrOrOrAndAndOrOrUnionMember0, FiltersOrOrOrOrAndAndOrOrOr, FiltersOrOrOrOrAndAndOrOrAnd
]


class FiltersOrOrOrOrAndAndOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersOrOrOrOrAndAndOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions or nested expressions"""


class FiltersOrOrOrOrAndAndAndAndUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrOrOrAndAndAndAndOrOrUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrOrOrAndAndAndAndOrOrOrOr(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrOrOrAndAndAndAndOrOrOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersOrOrOrOrAndAndAndAndOrOrOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions"""


class FiltersOrOrOrOrAndAndAndAndOrOrAndAnd(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrOrOrAndAndAndAndOrOrAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersOrOrOrOrAndAndAndAndOrOrAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions"""


FiltersOrOrOrOrAndAndAndAndOrOr: TypeAlias = Union[
    FiltersOrOrOrOrAndAndAndAndOrOrUnionMember0, FiltersOrOrOrOrAndAndAndAndOrOrOr, FiltersOrOrOrOrAndAndAndAndOrOrAnd
]


class FiltersOrOrOrOrAndAndAndAndOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersOrOrOrOrAndAndAndAndOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions or nested expressions"""


class FiltersOrOrOrOrAndAndAndAndAndAndUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrOrOrAndAndAndAndAndAndOrOr(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrOrOrAndAndAndAndAndAndOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersOrOrOrOrAndAndAndAndAndAndOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions"""


class FiltersOrOrOrOrAndAndAndAndAndAndAndAnd(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrOrOrAndAndAndAndAndAndAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersOrOrOrOrAndAndAndAndAndAndAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions"""


FiltersOrOrOrOrAndAndAndAndAndAnd: TypeAlias = Union[
    FiltersOrOrOrOrAndAndAndAndAndAndUnionMember0,
    FiltersOrOrOrOrAndAndAndAndAndAndOr,
    FiltersOrOrOrOrAndAndAndAndAndAndAnd,
]


class FiltersOrOrOrOrAndAndAndAndAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersOrOrOrOrAndAndAndAndAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions or nested expressions"""


FiltersOrOrOrOrAndAndAndAnd: TypeAlias = Union[
    FiltersOrOrOrOrAndAndAndAndUnionMember0, FiltersOrOrOrOrAndAndAndAndOr, FiltersOrOrOrOrAndAndAndAndAnd
]


class FiltersOrOrOrOrAndAndAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersOrOrOrOrAndAndAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions or nested expressions"""


FiltersOrOrOrOrAndAnd: TypeAlias = Union[
    FiltersOrOrOrOrAndAndUnionMember0, FiltersOrOrOrOrAndAndOr, FiltersOrOrOrOrAndAndAnd
]


class FiltersOrOrOrOrAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersOrOrOrOrAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions or nested expressions"""


FiltersOrOrOrOr: TypeAlias = Union[FiltersOrOrOrOrUnionMember0, FiltersOrOrOrOrOr, FiltersOrOrOrOrAnd]


class FiltersOrOrOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersOrOrOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions or nested expressions"""


class FiltersOrOrAndAndUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrAndAndOrOrUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrAndAndOrOrOrOrUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrAndAndOrOrOrOrOrOrUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrAndAndOrOrOrOrOrOrOrOr(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrAndAndOrOrOrOrOrOrOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersOrOrAndAndOrOrOrOrOrOrOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions"""


class FiltersOrOrAndAndOrOrOrOrOrOrAndAnd(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrAndAndOrOrOrOrOrOrAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersOrOrAndAndOrOrOrOrOrOrAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions"""


FiltersOrOrAndAndOrOrOrOrOrOr: TypeAlias = Union[
    FiltersOrOrAndAndOrOrOrOrOrOrUnionMember0, FiltersOrOrAndAndOrOrOrOrOrOrOr, FiltersOrOrAndAndOrOrOrOrOrOrAnd
]


class FiltersOrOrAndAndOrOrOrOrOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersOrOrAndAndOrOrOrOrOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions or nested expressions"""


class FiltersOrOrAndAndOrOrOrOrAndAndUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrAndAndOrOrOrOrAndAndOrOr(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrAndAndOrOrOrOrAndAndOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersOrOrAndAndOrOrOrOrAndAndOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions"""


class FiltersOrOrAndAndOrOrOrOrAndAndAndAnd(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrAndAndOrOrOrOrAndAndAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersOrOrAndAndOrOrOrOrAndAndAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions"""


FiltersOrOrAndAndOrOrOrOrAndAnd: TypeAlias = Union[
    FiltersOrOrAndAndOrOrOrOrAndAndUnionMember0, FiltersOrOrAndAndOrOrOrOrAndAndOr, FiltersOrOrAndAndOrOrOrOrAndAndAnd
]


class FiltersOrOrAndAndOrOrOrOrAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersOrOrAndAndOrOrOrOrAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions or nested expressions"""


FiltersOrOrAndAndOrOrOrOr: TypeAlias = Union[
    FiltersOrOrAndAndOrOrOrOrUnionMember0, FiltersOrOrAndAndOrOrOrOrOr, FiltersOrOrAndAndOrOrOrOrAnd
]


class FiltersOrOrAndAndOrOrOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersOrOrAndAndOrOrOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions or nested expressions"""


class FiltersOrOrAndAndOrOrAndAndUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrAndAndOrOrAndAndOrOrUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrAndAndOrOrAndAndOrOrOrOr(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrAndAndOrOrAndAndOrOrOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersOrOrAndAndOrOrAndAndOrOrOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions"""


class FiltersOrOrAndAndOrOrAndAndOrOrAndAnd(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrAndAndOrOrAndAndOrOrAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersOrOrAndAndOrOrAndAndOrOrAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions"""


FiltersOrOrAndAndOrOrAndAndOrOr: TypeAlias = Union[
    FiltersOrOrAndAndOrOrAndAndOrOrUnionMember0, FiltersOrOrAndAndOrOrAndAndOrOrOr, FiltersOrOrAndAndOrOrAndAndOrOrAnd
]


class FiltersOrOrAndAndOrOrAndAndOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersOrOrAndAndOrOrAndAndOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions or nested expressions"""


class FiltersOrOrAndAndOrOrAndAndAndAndUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrAndAndOrOrAndAndAndAndOrOr(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrAndAndOrOrAndAndAndAndOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersOrOrAndAndOrOrAndAndAndAndOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions"""


class FiltersOrOrAndAndOrOrAndAndAndAndAndAnd(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrAndAndOrOrAndAndAndAndAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersOrOrAndAndOrOrAndAndAndAndAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions"""


FiltersOrOrAndAndOrOrAndAndAndAnd: TypeAlias = Union[
    FiltersOrOrAndAndOrOrAndAndAndAndUnionMember0,
    FiltersOrOrAndAndOrOrAndAndAndAndOr,
    FiltersOrOrAndAndOrOrAndAndAndAndAnd,
]


class FiltersOrOrAndAndOrOrAndAndAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersOrOrAndAndOrOrAndAndAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions or nested expressions"""


FiltersOrOrAndAndOrOrAndAnd: TypeAlias = Union[
    FiltersOrOrAndAndOrOrAndAndUnionMember0, FiltersOrOrAndAndOrOrAndAndOr, FiltersOrOrAndAndOrOrAndAndAnd
]


class FiltersOrOrAndAndOrOrAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersOrOrAndAndOrOrAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions or nested expressions"""


FiltersOrOrAndAndOrOr: TypeAlias = Union[
    FiltersOrOrAndAndOrOrUnionMember0, FiltersOrOrAndAndOrOrOr, FiltersOrOrAndAndOrOrAnd
]


class FiltersOrOrAndAndOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersOrOrAndAndOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions or nested expressions"""


class FiltersOrOrAndAndAndAndUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrAndAndAndAndOrOrUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrAndAndAndAndOrOrOrOrUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrAndAndAndAndOrOrOrOrOrOr(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrAndAndAndAndOrOrOrOrOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersOrOrAndAndAndAndOrOrOrOrOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions"""


class FiltersOrOrAndAndAndAndOrOrOrOrAndAnd(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrAndAndAndAndOrOrOrOrAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersOrOrAndAndAndAndOrOrOrOrAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions"""


FiltersOrOrAndAndAndAndOrOrOrOr: TypeAlias = Union[
    FiltersOrOrAndAndAndAndOrOrOrOrUnionMember0, FiltersOrOrAndAndAndAndOrOrOrOrOr, FiltersOrOrAndAndAndAndOrOrOrOrAnd
]


class FiltersOrOrAndAndAndAndOrOrOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersOrOrAndAndAndAndOrOrOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions or nested expressions"""


class FiltersOrOrAndAndAndAndOrOrAndAndUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrAndAndAndAndOrOrAndAndOrOr(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrAndAndAndAndOrOrAndAndOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersOrOrAndAndAndAndOrOrAndAndOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions"""


class FiltersOrOrAndAndAndAndOrOrAndAndAndAnd(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrAndAndAndAndOrOrAndAndAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersOrOrAndAndAndAndOrOrAndAndAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions"""


FiltersOrOrAndAndAndAndOrOrAndAnd: TypeAlias = Union[
    FiltersOrOrAndAndAndAndOrOrAndAndUnionMember0,
    FiltersOrOrAndAndAndAndOrOrAndAndOr,
    FiltersOrOrAndAndAndAndOrOrAndAndAnd,
]


class FiltersOrOrAndAndAndAndOrOrAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersOrOrAndAndAndAndOrOrAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions or nested expressions"""


FiltersOrOrAndAndAndAndOrOr: TypeAlias = Union[
    FiltersOrOrAndAndAndAndOrOrUnionMember0, FiltersOrOrAndAndAndAndOrOrOr, FiltersOrOrAndAndAndAndOrOrAnd
]


class FiltersOrOrAndAndAndAndOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersOrOrAndAndAndAndOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions or nested expressions"""


class FiltersOrOrAndAndAndAndAndAndUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrAndAndAndAndAndAndOrOrUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrAndAndAndAndAndAndOrOrOrOr(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrAndAndAndAndAndAndOrOrOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersOrOrAndAndAndAndAndAndOrOrOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions"""


class FiltersOrOrAndAndAndAndAndAndOrOrAndAnd(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrAndAndAndAndAndAndOrOrAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersOrOrAndAndAndAndAndAndOrOrAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions"""


FiltersOrOrAndAndAndAndAndAndOrOr: TypeAlias = Union[
    FiltersOrOrAndAndAndAndAndAndOrOrUnionMember0,
    FiltersOrOrAndAndAndAndAndAndOrOrOr,
    FiltersOrOrAndAndAndAndAndAndOrOrAnd,
]


class FiltersOrOrAndAndAndAndAndAndOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersOrOrAndAndAndAndAndAndOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions or nested expressions"""


class FiltersOrOrAndAndAndAndAndAndAndAndUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrAndAndAndAndAndAndAndAndOrOr(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrAndAndAndAndAndAndAndAndOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersOrOrAndAndAndAndAndAndAndAndOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions"""


class FiltersOrOrAndAndAndAndAndAndAndAndAndAnd(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersOrOrAndAndAndAndAndAndAndAndAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersOrOrAndAndAndAndAndAndAndAndAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions"""


FiltersOrOrAndAndAndAndAndAndAndAnd: TypeAlias = Union[
    FiltersOrOrAndAndAndAndAndAndAndAndUnionMember0,
    FiltersOrOrAndAndAndAndAndAndAndAndOr,
    FiltersOrOrAndAndAndAndAndAndAndAndAnd,
]


class FiltersOrOrAndAndAndAndAndAndAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersOrOrAndAndAndAndAndAndAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions or nested expressions"""


FiltersOrOrAndAndAndAndAndAnd: TypeAlias = Union[
    FiltersOrOrAndAndAndAndAndAndUnionMember0, FiltersOrOrAndAndAndAndAndAndOr, FiltersOrOrAndAndAndAndAndAndAnd
]


class FiltersOrOrAndAndAndAndAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersOrOrAndAndAndAndAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions or nested expressions"""


FiltersOrOrAndAndAndAnd: TypeAlias = Union[
    FiltersOrOrAndAndAndAndUnionMember0, FiltersOrOrAndAndAndAndOr, FiltersOrOrAndAndAndAndAnd
]


class FiltersOrOrAndAndAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersOrOrAndAndAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions or nested expressions"""


FiltersOrOrAndAnd: TypeAlias = Union[FiltersOrOrAndAndUnionMember0, FiltersOrOrAndAndOr, FiltersOrOrAndAndAnd]


class FiltersOrOrAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersOrOrAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions or nested expressions"""


FiltersOrOr: TypeAlias = Union[FiltersOrOrUnionMember0, FiltersOrOrOr, FiltersOrOrAnd]


class FiltersOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersOrOr], PropertyInfo(alias="OR")]]
    """Array of OR filter expressions"""


class FiltersAndAndUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndOrOrUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndOrOrOrOrUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndOrOrOrOrOrOrUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndOrOrOrOrOrOrOrOrUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndOrOrOrOrOrOrOrOrOrOr(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndOrOrOrOrOrOrOrOrOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersAndAndOrOrOrOrOrOrOrOrOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions"""


class FiltersAndAndOrOrOrOrOrOrOrOrAndAnd(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndOrOrOrOrOrOrOrOrAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersAndAndOrOrOrOrOrOrOrOrAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions"""


FiltersAndAndOrOrOrOrOrOrOrOr: TypeAlias = Union[
    FiltersAndAndOrOrOrOrOrOrOrOrUnionMember0, FiltersAndAndOrOrOrOrOrOrOrOrOr, FiltersAndAndOrOrOrOrOrOrOrOrAnd
]


class FiltersAndAndOrOrOrOrOrOrOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersAndAndOrOrOrOrOrOrOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions or nested expressions"""


class FiltersAndAndOrOrOrOrOrOrAndAndUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndOrOrOrOrOrOrAndAndOrOr(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndOrOrOrOrOrOrAndAndOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersAndAndOrOrOrOrOrOrAndAndOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions"""


class FiltersAndAndOrOrOrOrOrOrAndAndAndAnd(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndOrOrOrOrOrOrAndAndAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersAndAndOrOrOrOrOrOrAndAndAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions"""


FiltersAndAndOrOrOrOrOrOrAndAnd: TypeAlias = Union[
    FiltersAndAndOrOrOrOrOrOrAndAndUnionMember0, FiltersAndAndOrOrOrOrOrOrAndAndOr, FiltersAndAndOrOrOrOrOrOrAndAndAnd
]


class FiltersAndAndOrOrOrOrOrOrAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersAndAndOrOrOrOrOrOrAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions or nested expressions"""


FiltersAndAndOrOrOrOrOrOr: TypeAlias = Union[
    FiltersAndAndOrOrOrOrOrOrUnionMember0, FiltersAndAndOrOrOrOrOrOrOr, FiltersAndAndOrOrOrOrOrOrAnd
]


class FiltersAndAndOrOrOrOrOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersAndAndOrOrOrOrOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions or nested expressions"""


class FiltersAndAndOrOrOrOrAndAndUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndOrOrOrOrAndAndOrOrUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndOrOrOrOrAndAndOrOrOrOr(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndOrOrOrOrAndAndOrOrOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersAndAndOrOrOrOrAndAndOrOrOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions"""


class FiltersAndAndOrOrOrOrAndAndOrOrAndAnd(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndOrOrOrOrAndAndOrOrAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersAndAndOrOrOrOrAndAndOrOrAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions"""


FiltersAndAndOrOrOrOrAndAndOrOr: TypeAlias = Union[
    FiltersAndAndOrOrOrOrAndAndOrOrUnionMember0, FiltersAndAndOrOrOrOrAndAndOrOrOr, FiltersAndAndOrOrOrOrAndAndOrOrAnd
]


class FiltersAndAndOrOrOrOrAndAndOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersAndAndOrOrOrOrAndAndOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions or nested expressions"""


class FiltersAndAndOrOrOrOrAndAndAndAndUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndOrOrOrOrAndAndAndAndOrOr(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndOrOrOrOrAndAndAndAndOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersAndAndOrOrOrOrAndAndAndAndOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions"""


class FiltersAndAndOrOrOrOrAndAndAndAndAndAnd(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndOrOrOrOrAndAndAndAndAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersAndAndOrOrOrOrAndAndAndAndAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions"""


FiltersAndAndOrOrOrOrAndAndAndAnd: TypeAlias = Union[
    FiltersAndAndOrOrOrOrAndAndAndAndUnionMember0,
    FiltersAndAndOrOrOrOrAndAndAndAndOr,
    FiltersAndAndOrOrOrOrAndAndAndAndAnd,
]


class FiltersAndAndOrOrOrOrAndAndAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersAndAndOrOrOrOrAndAndAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions or nested expressions"""


FiltersAndAndOrOrOrOrAndAnd: TypeAlias = Union[
    FiltersAndAndOrOrOrOrAndAndUnionMember0, FiltersAndAndOrOrOrOrAndAndOr, FiltersAndAndOrOrOrOrAndAndAnd
]


class FiltersAndAndOrOrOrOrAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersAndAndOrOrOrOrAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions or nested expressions"""


FiltersAndAndOrOrOrOr: TypeAlias = Union[
    FiltersAndAndOrOrOrOrUnionMember0, FiltersAndAndOrOrOrOrOr, FiltersAndAndOrOrOrOrAnd
]


class FiltersAndAndOrOrOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersAndAndOrOrOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions or nested expressions"""


class FiltersAndAndOrOrAndAndUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndOrOrAndAndOrOrUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndOrOrAndAndOrOrOrOrUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndOrOrAndAndOrOrOrOrOrOr(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndOrOrAndAndOrOrOrOrOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersAndAndOrOrAndAndOrOrOrOrOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions"""


class FiltersAndAndOrOrAndAndOrOrOrOrAndAnd(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndOrOrAndAndOrOrOrOrAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersAndAndOrOrAndAndOrOrOrOrAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions"""


FiltersAndAndOrOrAndAndOrOrOrOr: TypeAlias = Union[
    FiltersAndAndOrOrAndAndOrOrOrOrUnionMember0, FiltersAndAndOrOrAndAndOrOrOrOrOr, FiltersAndAndOrOrAndAndOrOrOrOrAnd
]


class FiltersAndAndOrOrAndAndOrOrOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersAndAndOrOrAndAndOrOrOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions or nested expressions"""


class FiltersAndAndOrOrAndAndOrOrAndAndUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndOrOrAndAndOrOrAndAndOrOr(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndOrOrAndAndOrOrAndAndOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersAndAndOrOrAndAndOrOrAndAndOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions"""


class FiltersAndAndOrOrAndAndOrOrAndAndAndAnd(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndOrOrAndAndOrOrAndAndAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersAndAndOrOrAndAndOrOrAndAndAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions"""


FiltersAndAndOrOrAndAndOrOrAndAnd: TypeAlias = Union[
    FiltersAndAndOrOrAndAndOrOrAndAndUnionMember0,
    FiltersAndAndOrOrAndAndOrOrAndAndOr,
    FiltersAndAndOrOrAndAndOrOrAndAndAnd,
]


class FiltersAndAndOrOrAndAndOrOrAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersAndAndOrOrAndAndOrOrAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions or nested expressions"""


FiltersAndAndOrOrAndAndOrOr: TypeAlias = Union[
    FiltersAndAndOrOrAndAndOrOrUnionMember0, FiltersAndAndOrOrAndAndOrOrOr, FiltersAndAndOrOrAndAndOrOrAnd
]


class FiltersAndAndOrOrAndAndOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersAndAndOrOrAndAndOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions or nested expressions"""


class FiltersAndAndOrOrAndAndAndAndUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndOrOrAndAndAndAndOrOrUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndOrOrAndAndAndAndOrOrOrOr(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndOrOrAndAndAndAndOrOrOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersAndAndOrOrAndAndAndAndOrOrOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions"""


class FiltersAndAndOrOrAndAndAndAndOrOrAndAnd(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndOrOrAndAndAndAndOrOrAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersAndAndOrOrAndAndAndAndOrOrAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions"""


FiltersAndAndOrOrAndAndAndAndOrOr: TypeAlias = Union[
    FiltersAndAndOrOrAndAndAndAndOrOrUnionMember0,
    FiltersAndAndOrOrAndAndAndAndOrOrOr,
    FiltersAndAndOrOrAndAndAndAndOrOrAnd,
]


class FiltersAndAndOrOrAndAndAndAndOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersAndAndOrOrAndAndAndAndOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions or nested expressions"""


class FiltersAndAndOrOrAndAndAndAndAndAndUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndOrOrAndAndAndAndAndAndOrOr(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndOrOrAndAndAndAndAndAndOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersAndAndOrOrAndAndAndAndAndAndOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions"""


class FiltersAndAndOrOrAndAndAndAndAndAndAndAnd(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndOrOrAndAndAndAndAndAndAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersAndAndOrOrAndAndAndAndAndAndAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions"""


FiltersAndAndOrOrAndAndAndAndAndAnd: TypeAlias = Union[
    FiltersAndAndOrOrAndAndAndAndAndAndUnionMember0,
    FiltersAndAndOrOrAndAndAndAndAndAndOr,
    FiltersAndAndOrOrAndAndAndAndAndAndAnd,
]


class FiltersAndAndOrOrAndAndAndAndAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersAndAndOrOrAndAndAndAndAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions or nested expressions"""


FiltersAndAndOrOrAndAndAndAnd: TypeAlias = Union[
    FiltersAndAndOrOrAndAndAndAndUnionMember0, FiltersAndAndOrOrAndAndAndAndOr, FiltersAndAndOrOrAndAndAndAndAnd
]


class FiltersAndAndOrOrAndAndAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersAndAndOrOrAndAndAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions or nested expressions"""


FiltersAndAndOrOrAndAnd: TypeAlias = Union[
    FiltersAndAndOrOrAndAndUnionMember0, FiltersAndAndOrOrAndAndOr, FiltersAndAndOrOrAndAndAnd
]


class FiltersAndAndOrOrAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersAndAndOrOrAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions or nested expressions"""


FiltersAndAndOrOr: TypeAlias = Union[FiltersAndAndOrOrUnionMember0, FiltersAndAndOrOrOr, FiltersAndAndOrOrAnd]


class FiltersAndAndOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersAndAndOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions or nested expressions"""


class FiltersAndAndAndAndUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndAndAndOrOrUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndAndAndOrOrOrOrUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndAndAndOrOrOrOrOrOrUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndAndAndOrOrOrOrOrOrOrOr(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndAndAndOrOrOrOrOrOrOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersAndAndAndAndOrOrOrOrOrOrOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions"""


class FiltersAndAndAndAndOrOrOrOrOrOrAndAnd(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndAndAndOrOrOrOrOrOrAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersAndAndAndAndOrOrOrOrOrOrAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions"""


FiltersAndAndAndAndOrOrOrOrOrOr: TypeAlias = Union[
    FiltersAndAndAndAndOrOrOrOrOrOrUnionMember0, FiltersAndAndAndAndOrOrOrOrOrOrOr, FiltersAndAndAndAndOrOrOrOrOrOrAnd
]


class FiltersAndAndAndAndOrOrOrOrOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersAndAndAndAndOrOrOrOrOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions or nested expressions"""


class FiltersAndAndAndAndOrOrOrOrAndAndUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndAndAndOrOrOrOrAndAndOrOr(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndAndAndOrOrOrOrAndAndOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersAndAndAndAndOrOrOrOrAndAndOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions"""


class FiltersAndAndAndAndOrOrOrOrAndAndAndAnd(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndAndAndOrOrOrOrAndAndAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersAndAndAndAndOrOrOrOrAndAndAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions"""


FiltersAndAndAndAndOrOrOrOrAndAnd: TypeAlias = Union[
    FiltersAndAndAndAndOrOrOrOrAndAndUnionMember0,
    FiltersAndAndAndAndOrOrOrOrAndAndOr,
    FiltersAndAndAndAndOrOrOrOrAndAndAnd,
]


class FiltersAndAndAndAndOrOrOrOrAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersAndAndAndAndOrOrOrOrAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions or nested expressions"""


FiltersAndAndAndAndOrOrOrOr: TypeAlias = Union[
    FiltersAndAndAndAndOrOrOrOrUnionMember0, FiltersAndAndAndAndOrOrOrOrOr, FiltersAndAndAndAndOrOrOrOrAnd
]


class FiltersAndAndAndAndOrOrOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersAndAndAndAndOrOrOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions or nested expressions"""


class FiltersAndAndAndAndOrOrAndAndUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndAndAndOrOrAndAndOrOrUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndAndAndOrOrAndAndOrOrOrOr(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndAndAndOrOrAndAndOrOrOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersAndAndAndAndOrOrAndAndOrOrOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions"""


class FiltersAndAndAndAndOrOrAndAndOrOrAndAnd(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndAndAndOrOrAndAndOrOrAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersAndAndAndAndOrOrAndAndOrOrAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions"""


FiltersAndAndAndAndOrOrAndAndOrOr: TypeAlias = Union[
    FiltersAndAndAndAndOrOrAndAndOrOrUnionMember0,
    FiltersAndAndAndAndOrOrAndAndOrOrOr,
    FiltersAndAndAndAndOrOrAndAndOrOrAnd,
]


class FiltersAndAndAndAndOrOrAndAndOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersAndAndAndAndOrOrAndAndOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions or nested expressions"""


class FiltersAndAndAndAndOrOrAndAndAndAndUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndAndAndOrOrAndAndAndAndOrOr(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndAndAndOrOrAndAndAndAndOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersAndAndAndAndOrOrAndAndAndAndOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions"""


class FiltersAndAndAndAndOrOrAndAndAndAndAndAnd(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndAndAndOrOrAndAndAndAndAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersAndAndAndAndOrOrAndAndAndAndAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions"""


FiltersAndAndAndAndOrOrAndAndAndAnd: TypeAlias = Union[
    FiltersAndAndAndAndOrOrAndAndAndAndUnionMember0,
    FiltersAndAndAndAndOrOrAndAndAndAndOr,
    FiltersAndAndAndAndOrOrAndAndAndAndAnd,
]


class FiltersAndAndAndAndOrOrAndAndAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersAndAndAndAndOrOrAndAndAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions or nested expressions"""


FiltersAndAndAndAndOrOrAndAnd: TypeAlias = Union[
    FiltersAndAndAndAndOrOrAndAndUnionMember0, FiltersAndAndAndAndOrOrAndAndOr, FiltersAndAndAndAndOrOrAndAndAnd
]


class FiltersAndAndAndAndOrOrAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersAndAndAndAndOrOrAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions or nested expressions"""


FiltersAndAndAndAndOrOr: TypeAlias = Union[
    FiltersAndAndAndAndOrOrUnionMember0, FiltersAndAndAndAndOrOrOr, FiltersAndAndAndAndOrOrAnd
]


class FiltersAndAndAndAndOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersAndAndAndAndOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions or nested expressions"""


class FiltersAndAndAndAndAndAndUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndAndAndAndAndOrOrUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndAndAndAndAndOrOrOrOrUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndAndAndAndAndOrOrOrOrOrOr(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndAndAndAndAndOrOrOrOrOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersAndAndAndAndAndAndOrOrOrOrOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions"""


class FiltersAndAndAndAndAndAndOrOrOrOrAndAnd(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndAndAndAndAndOrOrOrOrAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersAndAndAndAndAndAndOrOrOrOrAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions"""


FiltersAndAndAndAndAndAndOrOrOrOr: TypeAlias = Union[
    FiltersAndAndAndAndAndAndOrOrOrOrUnionMember0,
    FiltersAndAndAndAndAndAndOrOrOrOrOr,
    FiltersAndAndAndAndAndAndOrOrOrOrAnd,
]


class FiltersAndAndAndAndAndAndOrOrOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersAndAndAndAndAndAndOrOrOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions or nested expressions"""


class FiltersAndAndAndAndAndAndOrOrAndAndUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndAndAndAndAndOrOrAndAndOrOr(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndAndAndAndAndOrOrAndAndOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersAndAndAndAndAndAndOrOrAndAndOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions"""


class FiltersAndAndAndAndAndAndOrOrAndAndAndAnd(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndAndAndAndAndOrOrAndAndAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersAndAndAndAndAndAndOrOrAndAndAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions"""


FiltersAndAndAndAndAndAndOrOrAndAnd: TypeAlias = Union[
    FiltersAndAndAndAndAndAndOrOrAndAndUnionMember0,
    FiltersAndAndAndAndAndAndOrOrAndAndOr,
    FiltersAndAndAndAndAndAndOrOrAndAndAnd,
]


class FiltersAndAndAndAndAndAndOrOrAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersAndAndAndAndAndAndOrOrAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions or nested expressions"""


FiltersAndAndAndAndAndAndOrOr: TypeAlias = Union[
    FiltersAndAndAndAndAndAndOrOrUnionMember0, FiltersAndAndAndAndAndAndOrOrOr, FiltersAndAndAndAndAndAndOrOrAnd
]


class FiltersAndAndAndAndAndAndOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersAndAndAndAndAndAndOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions or nested expressions"""


class FiltersAndAndAndAndAndAndAndAndUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndAndAndAndAndAndAndOrOrUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndAndAndAndAndAndAndOrOrOrOr(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndAndAndAndAndAndAndOrOrOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersAndAndAndAndAndAndAndAndOrOrOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions"""


class FiltersAndAndAndAndAndAndAndAndOrOrAndAnd(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndAndAndAndAndAndAndOrOrAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersAndAndAndAndAndAndAndAndOrOrAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions"""


FiltersAndAndAndAndAndAndAndAndOrOr: TypeAlias = Union[
    FiltersAndAndAndAndAndAndAndAndOrOrUnionMember0,
    FiltersAndAndAndAndAndAndAndAndOrOrOr,
    FiltersAndAndAndAndAndAndAndAndOrOrAnd,
]


class FiltersAndAndAndAndAndAndAndAndOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersAndAndAndAndAndAndAndAndOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions or nested expressions"""


class FiltersAndAndAndAndAndAndAndAndAndAndUnionMember0(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndAndAndAndAndAndAndAndAndOrOr(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndAndAndAndAndAndAndAndAndOr(TypedDict, total=False):
    or_: Required[Annotated[Iterable[FiltersAndAndAndAndAndAndAndAndAndAndOrOr], PropertyInfo(alias="OR")]]
    """OR: Array of conditions"""


class FiltersAndAndAndAndAndAndAndAndAndAndAndAnd(TypedDict, total=False):
    """
    A single filter condition based on metadata, numeric values, array contents, or string matching
    """

    key: Required[str]

    value: Required[str]

    filter_type: Annotated[
        Literal["metadata", "numeric", "array_contains", "string_contains"], PropertyInfo(alias="filterType")
    ]

    ignore_case: Annotated[Union[bool, Literal["true", "false"]], PropertyInfo(alias="ignoreCase")]

    negate: Union[bool, Literal["true", "false"]]

    numeric_operator: Annotated[Literal[">", "<", ">=", "<=", "="], PropertyInfo(alias="numericOperator")]


class FiltersAndAndAndAndAndAndAndAndAndAndAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersAndAndAndAndAndAndAndAndAndAndAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions"""


FiltersAndAndAndAndAndAndAndAndAndAnd: TypeAlias = Union[
    FiltersAndAndAndAndAndAndAndAndAndAndUnionMember0,
    FiltersAndAndAndAndAndAndAndAndAndAndOr,
    FiltersAndAndAndAndAndAndAndAndAndAndAnd,
]


class FiltersAndAndAndAndAndAndAndAndAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersAndAndAndAndAndAndAndAndAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions or nested expressions"""


FiltersAndAndAndAndAndAndAndAnd: TypeAlias = Union[
    FiltersAndAndAndAndAndAndAndAndUnionMember0, FiltersAndAndAndAndAndAndAndAndOr, FiltersAndAndAndAndAndAndAndAndAnd
]


class FiltersAndAndAndAndAndAndAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersAndAndAndAndAndAndAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions or nested expressions"""


FiltersAndAndAndAndAndAnd: TypeAlias = Union[
    FiltersAndAndAndAndAndAndUnionMember0, FiltersAndAndAndAndAndAndOr, FiltersAndAndAndAndAndAndAnd
]


class FiltersAndAndAndAndAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersAndAndAndAndAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions or nested expressions"""


FiltersAndAndAndAnd: TypeAlias = Union[FiltersAndAndAndAndUnionMember0, FiltersAndAndAndAndOr, FiltersAndAndAndAndAnd]


class FiltersAndAndAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersAndAndAndAnd], PropertyInfo(alias="AND")]]
    """AND: Array of conditions or nested expressions"""


FiltersAndAnd: TypeAlias = Union[FiltersAndAndUnionMember0, FiltersAndAndOr, FiltersAndAndAnd]


class FiltersAnd(TypedDict, total=False):
    and_: Required[Annotated[Iterable[FiltersAndAnd], PropertyInfo(alias="AND")]]
    """Array of AND filter expressions"""


Filters: TypeAlias = Union[FiltersOr, FiltersAnd]
