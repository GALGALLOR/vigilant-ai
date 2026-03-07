# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union

import httpx

from ..types import memory_forget_params, memory_update_memory_params
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
from ..types.memory_forget_response import MemoryForgetResponse
from ..types.memory_update_memory_response import MemoryUpdateMemoryResponse

__all__ = ["MemoriesResource", "AsyncMemoriesResource"]


class MemoriesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> MemoriesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/supermemoryai/python-sdk#accessing-raw-response-data-eg-headers
        """
        return MemoriesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> MemoriesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/supermemoryai/python-sdk#with_streaming_response
        """
        return MemoriesResourceWithStreamingResponse(self)

    def forget(
        self,
        *,
        container_tag: str,
        id: str | Omit = omit,
        content: str | Omit = omit,
        reason: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MemoryForgetResponse:
        """Forget (soft delete) a memory entry.

        The memory is marked as forgotten but not
        permanently deleted.

        Args:
          container_tag: Container tag / space identifier. Required to scope the operation.

          id: ID of the memory entry to operate on

          content: Exact content match of the memory entry to operate on. Use this when you don't
              have the ID.

          reason: Optional reason for forgetting this memory

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._delete(
            "/v4/memories",
            body=maybe_transform(
                {
                    "container_tag": container_tag,
                    "id": id,
                    "content": content,
                    "reason": reason,
                },
                memory_forget_params.MemoryForgetParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MemoryForgetResponse,
        )

    def update_memory(
        self,
        *,
        container_tag: str,
        new_content: str,
        id: str | Omit = omit,
        content: str | Omit = omit,
        metadata: Dict[str, Union[str, float, bool, SequenceNotStr[str]]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MemoryUpdateMemoryResponse:
        """Update a memory by creating a new version.

        The original memory is preserved with
        isLatest=false.

        Args:
          container_tag: Container tag / space identifier. Required to scope the operation.

          new_content: The new content that will replace the existing memory

          id: ID of the memory entry to operate on

          content: Exact content match of the memory entry to operate on. Use this when you don't
              have the ID.

          metadata: Optional metadata. If not provided, inherits from the previous version.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._patch(
            "/v4/memories",
            body=maybe_transform(
                {
                    "container_tag": container_tag,
                    "new_content": new_content,
                    "id": id,
                    "content": content,
                    "metadata": metadata,
                },
                memory_update_memory_params.MemoryUpdateMemoryParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MemoryUpdateMemoryResponse,
        )


class AsyncMemoriesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncMemoriesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/supermemoryai/python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncMemoriesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncMemoriesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/supermemoryai/python-sdk#with_streaming_response
        """
        return AsyncMemoriesResourceWithStreamingResponse(self)

    async def forget(
        self,
        *,
        container_tag: str,
        id: str | Omit = omit,
        content: str | Omit = omit,
        reason: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MemoryForgetResponse:
        """Forget (soft delete) a memory entry.

        The memory is marked as forgotten but not
        permanently deleted.

        Args:
          container_tag: Container tag / space identifier. Required to scope the operation.

          id: ID of the memory entry to operate on

          content: Exact content match of the memory entry to operate on. Use this when you don't
              have the ID.

          reason: Optional reason for forgetting this memory

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._delete(
            "/v4/memories",
            body=await async_maybe_transform(
                {
                    "container_tag": container_tag,
                    "id": id,
                    "content": content,
                    "reason": reason,
                },
                memory_forget_params.MemoryForgetParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MemoryForgetResponse,
        )

    async def update_memory(
        self,
        *,
        container_tag: str,
        new_content: str,
        id: str | Omit = omit,
        content: str | Omit = omit,
        metadata: Dict[str, Union[str, float, bool, SequenceNotStr[str]]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MemoryUpdateMemoryResponse:
        """Update a memory by creating a new version.

        The original memory is preserved with
        isLatest=false.

        Args:
          container_tag: Container tag / space identifier. Required to scope the operation.

          new_content: The new content that will replace the existing memory

          id: ID of the memory entry to operate on

          content: Exact content match of the memory entry to operate on. Use this when you don't
              have the ID.

          metadata: Optional metadata. If not provided, inherits from the previous version.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._patch(
            "/v4/memories",
            body=await async_maybe_transform(
                {
                    "container_tag": container_tag,
                    "new_content": new_content,
                    "id": id,
                    "content": content,
                    "metadata": metadata,
                },
                memory_update_memory_params.MemoryUpdateMemoryParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MemoryUpdateMemoryResponse,
        )


class MemoriesResourceWithRawResponse:
    def __init__(self, memories: MemoriesResource) -> None:
        self._memories = memories

        self.forget = to_raw_response_wrapper(
            memories.forget,
        )
        self.update_memory = to_raw_response_wrapper(
            memories.update_memory,
        )


class AsyncMemoriesResourceWithRawResponse:
    def __init__(self, memories: AsyncMemoriesResource) -> None:
        self._memories = memories

        self.forget = async_to_raw_response_wrapper(
            memories.forget,
        )
        self.update_memory = async_to_raw_response_wrapper(
            memories.update_memory,
        )


class MemoriesResourceWithStreamingResponse:
    def __init__(self, memories: MemoriesResource) -> None:
        self._memories = memories

        self.forget = to_streamed_response_wrapper(
            memories.forget,
        )
        self.update_memory = to_streamed_response_wrapper(
            memories.update_memory,
        )


class AsyncMemoriesResourceWithStreamingResponse:
    def __init__(self, memories: AsyncMemoriesResource) -> None:
        self._memories = memories

        self.forget = async_to_streamed_response_wrapper(
            memories.forget,
        )
        self.update_memory = async_to_streamed_response_wrapper(
            memories.update_memory,
        )
