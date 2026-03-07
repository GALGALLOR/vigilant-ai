# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ..types import search_execute_params, search_memories_params, search_documents_params
from .._types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.search_execute_response import SearchExecuteResponse
from ..types.search_memories_response import SearchMemoriesResponse
from ..types.search_documents_response import SearchDocumentsResponse

__all__ = ["SearchResource", "AsyncSearchResource"]


class SearchResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> SearchResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/supermemoryai/python-sdk#accessing-raw-response-data-eg-headers
        """
        return SearchResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SearchResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/supermemoryai/python-sdk#with_streaming_response
        """
        return SearchResourceWithStreamingResponse(self)

    def documents(
        self,
        *,
        q: str,
        categories_filter: SequenceNotStr[str] | Omit = omit,
        chunk_threshold: float | Omit = omit,
        container_tags: SequenceNotStr[str] | Omit = omit,
        doc_id: str | Omit = omit,
        document_threshold: float | Omit = omit,
        filters: search_documents_params.Filters | Omit = omit,
        include_full_docs: bool | Omit = omit,
        include_summary: bool | Omit = omit,
        limit: int | Omit = omit,
        only_matching_chunks: bool | Omit = omit,
        rerank: bool | Omit = omit,
        rewrite_query: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SearchDocumentsResponse:
        """
        Search memories with advanced filtering

        Args:
          q: Search query string

          categories_filter: DEPRECATED: Optional category filters

          chunk_threshold: Threshold / sensitivity for chunk selection. 0 is least sensitive (returns most
              chunks, more results), 1 is most sensitive (returns lesser chunks, accurate
              results)

          container_tags: Optional tags this search should be containerized by. This can be an ID for your
              user, a project ID, or any other identifier you wish to use to filter documents.

          doc_id: Optional document ID to search within. You can use this to find chunks in a very
              large document.

          document_threshold: DEPRECATED: This field is no longer used in v3 search. The search now uses
              chunkThreshold only. This parameter will be ignored.

          filters: Optional filters to apply to the search. Can be a JSON string or Query object.

          include_full_docs: If true, include full document in the response. This is helpful if you want a
              chatbot to know the full context of the document.

          include_summary: If true, include document summary in the response. This is helpful if you want a
              chatbot to know the full context of the document.

          limit: Maximum number of results to return

          only_matching_chunks: If true, only return matching chunks without context. Normally, we send the
              previous and next chunk to provide more context for LLMs. If you only want the
              matching chunk, set this to true.

          rerank: If true, rerank the results based on the query. This is helpful if you want to
              ensure the most relevant results are returned.

          rewrite_query: If true, rewrites the query to make it easier to find documents. This increases
              the latency by about 400ms

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v3/search",
            body=maybe_transform(
                {
                    "q": q,
                    "categories_filter": categories_filter,
                    "chunk_threshold": chunk_threshold,
                    "container_tags": container_tags,
                    "doc_id": doc_id,
                    "document_threshold": document_threshold,
                    "filters": filters,
                    "include_full_docs": include_full_docs,
                    "include_summary": include_summary,
                    "limit": limit,
                    "only_matching_chunks": only_matching_chunks,
                    "rerank": rerank,
                    "rewrite_query": rewrite_query,
                },
                search_documents_params.SearchDocumentsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SearchDocumentsResponse,
        )

    def execute(
        self,
        *,
        q: str,
        categories_filter: SequenceNotStr[str] | Omit = omit,
        chunk_threshold: float | Omit = omit,
        container_tags: SequenceNotStr[str] | Omit = omit,
        doc_id: str | Omit = omit,
        document_threshold: float | Omit = omit,
        filters: search_execute_params.Filters | Omit = omit,
        include_full_docs: bool | Omit = omit,
        include_summary: bool | Omit = omit,
        limit: int | Omit = omit,
        only_matching_chunks: bool | Omit = omit,
        rerank: bool | Omit = omit,
        rewrite_query: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SearchExecuteResponse:
        """
        Search memories with advanced filtering

        Args:
          q: Search query string

          categories_filter: DEPRECATED: Optional category filters

          chunk_threshold: Threshold / sensitivity for chunk selection. 0 is least sensitive (returns most
              chunks, more results), 1 is most sensitive (returns lesser chunks, accurate
              results)

          container_tags: Optional tags this search should be containerized by. This can be an ID for your
              user, a project ID, or any other identifier you wish to use to filter documents.

          doc_id: Optional document ID to search within. You can use this to find chunks in a very
              large document.

          document_threshold: DEPRECATED: This field is no longer used in v3 search. The search now uses
              chunkThreshold only. This parameter will be ignored.

          filters: Optional filters to apply to the search. Can be a JSON string or Query object.

          include_full_docs: If true, include full document in the response. This is helpful if you want a
              chatbot to know the full context of the document.

          include_summary: If true, include document summary in the response. This is helpful if you want a
              chatbot to know the full context of the document.

          limit: Maximum number of results to return

          only_matching_chunks: If true, only return matching chunks without context. Normally, we send the
              previous and next chunk to provide more context for LLMs. If you only want the
              matching chunk, set this to true.

          rerank: If true, rerank the results based on the query. This is helpful if you want to
              ensure the most relevant results are returned.

          rewrite_query: If true, rewrites the query to make it easier to find documents. This increases
              the latency by about 400ms

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v3/search",
            body=maybe_transform(
                {
                    "q": q,
                    "categories_filter": categories_filter,
                    "chunk_threshold": chunk_threshold,
                    "container_tags": container_tags,
                    "doc_id": doc_id,
                    "document_threshold": document_threshold,
                    "filters": filters,
                    "include_full_docs": include_full_docs,
                    "include_summary": include_summary,
                    "limit": limit,
                    "only_matching_chunks": only_matching_chunks,
                    "rerank": rerank,
                    "rewrite_query": rewrite_query,
                },
                search_execute_params.SearchExecuteParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SearchExecuteResponse,
        )

    def memories(
        self,
        *,
        q: str,
        container_tag: str | Omit = omit,
        filters: search_memories_params.Filters | Omit = omit,
        include: search_memories_params.Include | Omit = omit,
        limit: int | Omit = omit,
        rerank: bool | Omit = omit,
        rewrite_query: bool | Omit = omit,
        search_mode: Literal["memories", "hybrid", "documents"] | Omit = omit,
        threshold: float | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SearchMemoriesResponse:
        """
        Search memory entries - Low latency for conversational

        Args:
          q: Search query string

          container_tag: Optional tag this search should be containerized by. This can be an ID for your
              user, a project ID, or any other identifier you wish to use to filter memories.

          filters: Optional filters to apply to the search. Can be a JSON string or Query object.

          limit: Maximum number of results to return

          rerank: If true, rerank the results based on the query. This is helpful if you want to
              ensure the most relevant results are returned.

          rewrite_query: If true, rewrites the query to make it easier to find documents. This increases
              the latency by about 400ms

          search_mode: Search mode. 'memories' searches only memory entries (default). 'hybrid'
              searches both memories and document chunks. 'documents' searches only document
              chunks.

          threshold: Threshold / sensitivity for memories selection. 0 is least sensitive (returns
              most memories, more results), 1 is most sensitive (returns lesser memories,
              accurate results)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v4/search",
            body=maybe_transform(
                {
                    "q": q,
                    "container_tag": container_tag,
                    "filters": filters,
                    "include": include,
                    "limit": limit,
                    "rerank": rerank,
                    "rewrite_query": rewrite_query,
                    "search_mode": search_mode,
                    "threshold": threshold,
                },
                search_memories_params.SearchMemoriesParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SearchMemoriesResponse,
        )


class AsyncSearchResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncSearchResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/supermemoryai/python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncSearchResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSearchResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/supermemoryai/python-sdk#with_streaming_response
        """
        return AsyncSearchResourceWithStreamingResponse(self)

    async def documents(
        self,
        *,
        q: str,
        categories_filter: SequenceNotStr[str] | Omit = omit,
        chunk_threshold: float | Omit = omit,
        container_tags: SequenceNotStr[str] | Omit = omit,
        doc_id: str | Omit = omit,
        document_threshold: float | Omit = omit,
        filters: search_documents_params.Filters | Omit = omit,
        include_full_docs: bool | Omit = omit,
        include_summary: bool | Omit = omit,
        limit: int | Omit = omit,
        only_matching_chunks: bool | Omit = omit,
        rerank: bool | Omit = omit,
        rewrite_query: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SearchDocumentsResponse:
        """
        Search memories with advanced filtering

        Args:
          q: Search query string

          categories_filter: DEPRECATED: Optional category filters

          chunk_threshold: Threshold / sensitivity for chunk selection. 0 is least sensitive (returns most
              chunks, more results), 1 is most sensitive (returns lesser chunks, accurate
              results)

          container_tags: Optional tags this search should be containerized by. This can be an ID for your
              user, a project ID, or any other identifier you wish to use to filter documents.

          doc_id: Optional document ID to search within. You can use this to find chunks in a very
              large document.

          document_threshold: DEPRECATED: This field is no longer used in v3 search. The search now uses
              chunkThreshold only. This parameter will be ignored.

          filters: Optional filters to apply to the search. Can be a JSON string or Query object.

          include_full_docs: If true, include full document in the response. This is helpful if you want a
              chatbot to know the full context of the document.

          include_summary: If true, include document summary in the response. This is helpful if you want a
              chatbot to know the full context of the document.

          limit: Maximum number of results to return

          only_matching_chunks: If true, only return matching chunks without context. Normally, we send the
              previous and next chunk to provide more context for LLMs. If you only want the
              matching chunk, set this to true.

          rerank: If true, rerank the results based on the query. This is helpful if you want to
              ensure the most relevant results are returned.

          rewrite_query: If true, rewrites the query to make it easier to find documents. This increases
              the latency by about 400ms

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v3/search",
            body=await async_maybe_transform(
                {
                    "q": q,
                    "categories_filter": categories_filter,
                    "chunk_threshold": chunk_threshold,
                    "container_tags": container_tags,
                    "doc_id": doc_id,
                    "document_threshold": document_threshold,
                    "filters": filters,
                    "include_full_docs": include_full_docs,
                    "include_summary": include_summary,
                    "limit": limit,
                    "only_matching_chunks": only_matching_chunks,
                    "rerank": rerank,
                    "rewrite_query": rewrite_query,
                },
                search_documents_params.SearchDocumentsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SearchDocumentsResponse,
        )

    async def execute(
        self,
        *,
        q: str,
        categories_filter: SequenceNotStr[str] | Omit = omit,
        chunk_threshold: float | Omit = omit,
        container_tags: SequenceNotStr[str] | Omit = omit,
        doc_id: str | Omit = omit,
        document_threshold: float | Omit = omit,
        filters: search_execute_params.Filters | Omit = omit,
        include_full_docs: bool | Omit = omit,
        include_summary: bool | Omit = omit,
        limit: int | Omit = omit,
        only_matching_chunks: bool | Omit = omit,
        rerank: bool | Omit = omit,
        rewrite_query: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SearchExecuteResponse:
        """
        Search memories with advanced filtering

        Args:
          q: Search query string

          categories_filter: DEPRECATED: Optional category filters

          chunk_threshold: Threshold / sensitivity for chunk selection. 0 is least sensitive (returns most
              chunks, more results), 1 is most sensitive (returns lesser chunks, accurate
              results)

          container_tags: Optional tags this search should be containerized by. This can be an ID for your
              user, a project ID, or any other identifier you wish to use to filter documents.

          doc_id: Optional document ID to search within. You can use this to find chunks in a very
              large document.

          document_threshold: DEPRECATED: This field is no longer used in v3 search. The search now uses
              chunkThreshold only. This parameter will be ignored.

          filters: Optional filters to apply to the search. Can be a JSON string or Query object.

          include_full_docs: If true, include full document in the response. This is helpful if you want a
              chatbot to know the full context of the document.

          include_summary: If true, include document summary in the response. This is helpful if you want a
              chatbot to know the full context of the document.

          limit: Maximum number of results to return

          only_matching_chunks: If true, only return matching chunks without context. Normally, we send the
              previous and next chunk to provide more context for LLMs. If you only want the
              matching chunk, set this to true.

          rerank: If true, rerank the results based on the query. This is helpful if you want to
              ensure the most relevant results are returned.

          rewrite_query: If true, rewrites the query to make it easier to find documents. This increases
              the latency by about 400ms

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v3/search",
            body=await async_maybe_transform(
                {
                    "q": q,
                    "categories_filter": categories_filter,
                    "chunk_threshold": chunk_threshold,
                    "container_tags": container_tags,
                    "doc_id": doc_id,
                    "document_threshold": document_threshold,
                    "filters": filters,
                    "include_full_docs": include_full_docs,
                    "include_summary": include_summary,
                    "limit": limit,
                    "only_matching_chunks": only_matching_chunks,
                    "rerank": rerank,
                    "rewrite_query": rewrite_query,
                },
                search_execute_params.SearchExecuteParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SearchExecuteResponse,
        )

    async def memories(
        self,
        *,
        q: str,
        container_tag: str | Omit = omit,
        filters: search_memories_params.Filters | Omit = omit,
        include: search_memories_params.Include | Omit = omit,
        limit: int | Omit = omit,
        rerank: bool | Omit = omit,
        rewrite_query: bool | Omit = omit,
        search_mode: Literal["memories", "hybrid", "documents"] | Omit = omit,
        threshold: float | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SearchMemoriesResponse:
        """
        Search memory entries - Low latency for conversational

        Args:
          q: Search query string

          container_tag: Optional tag this search should be containerized by. This can be an ID for your
              user, a project ID, or any other identifier you wish to use to filter memories.

          filters: Optional filters to apply to the search. Can be a JSON string or Query object.

          limit: Maximum number of results to return

          rerank: If true, rerank the results based on the query. This is helpful if you want to
              ensure the most relevant results are returned.

          rewrite_query: If true, rewrites the query to make it easier to find documents. This increases
              the latency by about 400ms

          search_mode: Search mode. 'memories' searches only memory entries (default). 'hybrid'
              searches both memories and document chunks. 'documents' searches only document
              chunks.

          threshold: Threshold / sensitivity for memories selection. 0 is least sensitive (returns
              most memories, more results), 1 is most sensitive (returns lesser memories,
              accurate results)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v4/search",
            body=await async_maybe_transform(
                {
                    "q": q,
                    "container_tag": container_tag,
                    "filters": filters,
                    "include": include,
                    "limit": limit,
                    "rerank": rerank,
                    "rewrite_query": rewrite_query,
                    "search_mode": search_mode,
                    "threshold": threshold,
                },
                search_memories_params.SearchMemoriesParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SearchMemoriesResponse,
        )


class SearchResourceWithRawResponse:
    def __init__(self, search: SearchResource) -> None:
        self._search = search

        self.documents = to_raw_response_wrapper(
            search.documents,
        )
        self.execute = to_raw_response_wrapper(
            search.execute,
        )
        self.memories = to_raw_response_wrapper(
            search.memories,
        )


class AsyncSearchResourceWithRawResponse:
    def __init__(self, search: AsyncSearchResource) -> None:
        self._search = search

        self.documents = async_to_raw_response_wrapper(
            search.documents,
        )
        self.execute = async_to_raw_response_wrapper(
            search.execute,
        )
        self.memories = async_to_raw_response_wrapper(
            search.memories,
        )


class SearchResourceWithStreamingResponse:
    def __init__(self, search: SearchResource) -> None:
        self._search = search

        self.documents = to_streamed_response_wrapper(
            search.documents,
        )
        self.execute = to_streamed_response_wrapper(
            search.execute,
        )
        self.memories = to_streamed_response_wrapper(
            search.memories,
        )


class AsyncSearchResourceWithStreamingResponse:
    def __init__(self, search: AsyncSearchResource) -> None:
        self._search = search

        self.documents = async_to_streamed_response_wrapper(
            search.documents,
        )
        self.execute = async_to_streamed_response_wrapper(
            search.execute,
        )
        self.memories = async_to_streamed_response_wrapper(
            search.memories,
        )
