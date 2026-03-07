# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Iterable, Optional
from typing_extensions import Literal

import httpx

from ..types import (
    connection_list_params,
    connection_create_params,
    connection_import_params,
    connection_configure_params,
    connection_resources_params,
    connection_get_by_tag_params,
    connection_list_documents_params,
    connection_delete_by_provider_params,
)
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
from ..types.connection_list_response import ConnectionListResponse
from ..types.connection_create_response import ConnectionCreateResponse
from ..types.connection_configure_response import ConnectionConfigureResponse
from ..types.connection_get_by_id_response import ConnectionGetByIDResponse
from ..types.connection_resources_response import ConnectionResourcesResponse
from ..types.connection_get_by_tag_response import ConnectionGetByTagResponse
from ..types.connection_delete_by_id_response import ConnectionDeleteByIDResponse
from ..types.connection_list_documents_response import ConnectionListDocumentsResponse
from ..types.connection_delete_by_provider_response import ConnectionDeleteByProviderResponse

__all__ = ["ConnectionsResource", "AsyncConnectionsResource"]


class ConnectionsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ConnectionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/supermemoryai/python-sdk#accessing-raw-response-data-eg-headers
        """
        return ConnectionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ConnectionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/supermemoryai/python-sdk#with_streaming_response
        """
        return ConnectionsResourceWithStreamingResponse(self)

    def create(
        self,
        provider: Literal["notion", "google-drive", "onedrive", "gmail", "github", "web-crawler", "s3"],
        *,
        container_tags: SequenceNotStr[str] | Omit = omit,
        document_limit: int | Omit = omit,
        metadata: Optional[Dict[str, Union[str, float, bool]]] | Omit = omit,
        redirect_url: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ConnectionCreateResponse:
        """
        Initialize connection and get authorization URL

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not provider:
            raise ValueError(f"Expected a non-empty value for `provider` but received {provider!r}")
        return self._post(
            f"/v3/connections/{provider}",
            body=maybe_transform(
                {
                    "container_tags": container_tags,
                    "document_limit": document_limit,
                    "metadata": metadata,
                    "redirect_url": redirect_url,
                },
                connection_create_params.ConnectionCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConnectionCreateResponse,
        )

    def list(
        self,
        *,
        container_tags: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ConnectionListResponse:
        """
        List all connections

        Args:
          container_tags: Optional comma-separated list of container tags to filter documents by

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v3/connections/list",
            body=maybe_transform({"container_tags": container_tags}, connection_list_params.ConnectionListParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConnectionListResponse,
        )

    def configure(
        self,
        connection_id: str,
        *,
        resources: Iterable[Dict[str, object]],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ConnectionConfigureResponse:
        """
        Configure resources for a connection (supported providers: GitHub for now)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not connection_id:
            raise ValueError(f"Expected a non-empty value for `connection_id` but received {connection_id!r}")
        return self._post(
            f"/v3/connections/{connection_id}/configure",
            body=maybe_transform({"resources": resources}, connection_configure_params.ConnectionConfigureParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConnectionConfigureResponse,
        )

    def delete_by_id(
        self,
        connection_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ConnectionDeleteByIDResponse:
        """
        Delete a specific connection by ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not connection_id:
            raise ValueError(f"Expected a non-empty value for `connection_id` but received {connection_id!r}")
        return self._delete(
            f"/v3/connections/{connection_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConnectionDeleteByIDResponse,
        )

    def delete_by_provider(
        self,
        provider: Literal["notion", "google-drive", "onedrive", "gmail", "github", "web-crawler", "s3"],
        *,
        container_tags: SequenceNotStr[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ConnectionDeleteByProviderResponse:
        """
        Delete connection for a specific provider and container tags

        Args:
          container_tags: Optional comma-separated list of container tags to filter connections by

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not provider:
            raise ValueError(f"Expected a non-empty value for `provider` but received {provider!r}")
        return self._delete(
            f"/v3/connections/{provider}",
            body=maybe_transform(
                {"container_tags": container_tags},
                connection_delete_by_provider_params.ConnectionDeleteByProviderParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConnectionDeleteByProviderResponse,
        )

    def get_by_id(
        self,
        connection_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ConnectionGetByIDResponse:
        """
        Get connection details with id

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not connection_id:
            raise ValueError(f"Expected a non-empty value for `connection_id` but received {connection_id!r}")
        return self._get(
            f"/v3/connections/{connection_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConnectionGetByIDResponse,
        )

    def get_by_tag(
        self,
        provider: Literal["notion", "google-drive", "onedrive", "gmail", "github", "web-crawler", "s3"],
        *,
        container_tags: SequenceNotStr[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ConnectionGetByTagResponse:
        """
        Get connection details with provider and container tags

        Args:
          container_tags: Comma-separated list of container tags to filter connection by

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not provider:
            raise ValueError(f"Expected a non-empty value for `provider` but received {provider!r}")
        return self._post(
            f"/v3/connections/{provider}/connection",
            body=maybe_transform(
                {"container_tags": container_tags}, connection_get_by_tag_params.ConnectionGetByTagParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConnectionGetByTagResponse,
        )

    def import_(
        self,
        provider: Literal["notion", "google-drive", "onedrive", "gmail", "github", "web-crawler", "s3"],
        *,
        container_tags: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> str:
        """
        Initiate a manual sync of connections

        Args:
          container_tags: Optional comma-separated list of container tags to filter connections by

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not provider:
            raise ValueError(f"Expected a non-empty value for `provider` but received {provider!r}")
        extra_headers = {"Accept": "text/plain", **(extra_headers or {})}
        return self._post(
            f"/v3/connections/{provider}/import",
            body=maybe_transform({"container_tags": container_tags}, connection_import_params.ConnectionImportParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=str,
        )

    def list_documents(
        self,
        provider: Literal["notion", "google-drive", "onedrive", "gmail", "github", "web-crawler", "s3"],
        *,
        container_tags: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ConnectionListDocumentsResponse:
        """
        List documents indexed for a provider and container tags

        Args:
          container_tags: Optional comma-separated list of container tags to filter documents by

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not provider:
            raise ValueError(f"Expected a non-empty value for `provider` but received {provider!r}")
        return self._post(
            f"/v3/connections/{provider}/documents",
            body=maybe_transform(
                {"container_tags": container_tags}, connection_list_documents_params.ConnectionListDocumentsParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConnectionListDocumentsResponse,
        )

    def resources(
        self,
        connection_id: str,
        *,
        page: float | Omit = omit,
        per_page: float | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ConnectionResourcesResponse:
        """
        Fetch resources for a connection (supported providers: GitHub for now)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not connection_id:
            raise ValueError(f"Expected a non-empty value for `connection_id` but received {connection_id!r}")
        return self._get(
            f"/v3/connections/{connection_id}/resources",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "page": page,
                        "per_page": per_page,
                    },
                    connection_resources_params.ConnectionResourcesParams,
                ),
            ),
            cast_to=ConnectionResourcesResponse,
        )


class AsyncConnectionsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncConnectionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/supermemoryai/python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncConnectionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncConnectionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/supermemoryai/python-sdk#with_streaming_response
        """
        return AsyncConnectionsResourceWithStreamingResponse(self)

    async def create(
        self,
        provider: Literal["notion", "google-drive", "onedrive", "gmail", "github", "web-crawler", "s3"],
        *,
        container_tags: SequenceNotStr[str] | Omit = omit,
        document_limit: int | Omit = omit,
        metadata: Optional[Dict[str, Union[str, float, bool]]] | Omit = omit,
        redirect_url: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ConnectionCreateResponse:
        """
        Initialize connection and get authorization URL

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not provider:
            raise ValueError(f"Expected a non-empty value for `provider` but received {provider!r}")
        return await self._post(
            f"/v3/connections/{provider}",
            body=await async_maybe_transform(
                {
                    "container_tags": container_tags,
                    "document_limit": document_limit,
                    "metadata": metadata,
                    "redirect_url": redirect_url,
                },
                connection_create_params.ConnectionCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConnectionCreateResponse,
        )

    async def list(
        self,
        *,
        container_tags: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ConnectionListResponse:
        """
        List all connections

        Args:
          container_tags: Optional comma-separated list of container tags to filter documents by

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v3/connections/list",
            body=await async_maybe_transform(
                {"container_tags": container_tags}, connection_list_params.ConnectionListParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConnectionListResponse,
        )

    async def configure(
        self,
        connection_id: str,
        *,
        resources: Iterable[Dict[str, object]],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ConnectionConfigureResponse:
        """
        Configure resources for a connection (supported providers: GitHub for now)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not connection_id:
            raise ValueError(f"Expected a non-empty value for `connection_id` but received {connection_id!r}")
        return await self._post(
            f"/v3/connections/{connection_id}/configure",
            body=await async_maybe_transform(
                {"resources": resources}, connection_configure_params.ConnectionConfigureParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConnectionConfigureResponse,
        )

    async def delete_by_id(
        self,
        connection_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ConnectionDeleteByIDResponse:
        """
        Delete a specific connection by ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not connection_id:
            raise ValueError(f"Expected a non-empty value for `connection_id` but received {connection_id!r}")
        return await self._delete(
            f"/v3/connections/{connection_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConnectionDeleteByIDResponse,
        )

    async def delete_by_provider(
        self,
        provider: Literal["notion", "google-drive", "onedrive", "gmail", "github", "web-crawler", "s3"],
        *,
        container_tags: SequenceNotStr[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ConnectionDeleteByProviderResponse:
        """
        Delete connection for a specific provider and container tags

        Args:
          container_tags: Optional comma-separated list of container tags to filter connections by

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not provider:
            raise ValueError(f"Expected a non-empty value for `provider` but received {provider!r}")
        return await self._delete(
            f"/v3/connections/{provider}",
            body=await async_maybe_transform(
                {"container_tags": container_tags},
                connection_delete_by_provider_params.ConnectionDeleteByProviderParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConnectionDeleteByProviderResponse,
        )

    async def get_by_id(
        self,
        connection_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ConnectionGetByIDResponse:
        """
        Get connection details with id

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not connection_id:
            raise ValueError(f"Expected a non-empty value for `connection_id` but received {connection_id!r}")
        return await self._get(
            f"/v3/connections/{connection_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConnectionGetByIDResponse,
        )

    async def get_by_tag(
        self,
        provider: Literal["notion", "google-drive", "onedrive", "gmail", "github", "web-crawler", "s3"],
        *,
        container_tags: SequenceNotStr[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ConnectionGetByTagResponse:
        """
        Get connection details with provider and container tags

        Args:
          container_tags: Comma-separated list of container tags to filter connection by

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not provider:
            raise ValueError(f"Expected a non-empty value for `provider` but received {provider!r}")
        return await self._post(
            f"/v3/connections/{provider}/connection",
            body=await async_maybe_transform(
                {"container_tags": container_tags}, connection_get_by_tag_params.ConnectionGetByTagParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConnectionGetByTagResponse,
        )

    async def import_(
        self,
        provider: Literal["notion", "google-drive", "onedrive", "gmail", "github", "web-crawler", "s3"],
        *,
        container_tags: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> str:
        """
        Initiate a manual sync of connections

        Args:
          container_tags: Optional comma-separated list of container tags to filter connections by

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not provider:
            raise ValueError(f"Expected a non-empty value for `provider` but received {provider!r}")
        extra_headers = {"Accept": "text/plain", **(extra_headers or {})}
        return await self._post(
            f"/v3/connections/{provider}/import",
            body=await async_maybe_transform(
                {"container_tags": container_tags}, connection_import_params.ConnectionImportParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=str,
        )

    async def list_documents(
        self,
        provider: Literal["notion", "google-drive", "onedrive", "gmail", "github", "web-crawler", "s3"],
        *,
        container_tags: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ConnectionListDocumentsResponse:
        """
        List documents indexed for a provider and container tags

        Args:
          container_tags: Optional comma-separated list of container tags to filter documents by

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not provider:
            raise ValueError(f"Expected a non-empty value for `provider` but received {provider!r}")
        return await self._post(
            f"/v3/connections/{provider}/documents",
            body=await async_maybe_transform(
                {"container_tags": container_tags}, connection_list_documents_params.ConnectionListDocumentsParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConnectionListDocumentsResponse,
        )

    async def resources(
        self,
        connection_id: str,
        *,
        page: float | Omit = omit,
        per_page: float | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ConnectionResourcesResponse:
        """
        Fetch resources for a connection (supported providers: GitHub for now)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not connection_id:
            raise ValueError(f"Expected a non-empty value for `connection_id` but received {connection_id!r}")
        return await self._get(
            f"/v3/connections/{connection_id}/resources",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "page": page,
                        "per_page": per_page,
                    },
                    connection_resources_params.ConnectionResourcesParams,
                ),
            ),
            cast_to=ConnectionResourcesResponse,
        )


class ConnectionsResourceWithRawResponse:
    def __init__(self, connections: ConnectionsResource) -> None:
        self._connections = connections

        self.create = to_raw_response_wrapper(
            connections.create,
        )
        self.list = to_raw_response_wrapper(
            connections.list,
        )
        self.configure = to_raw_response_wrapper(
            connections.configure,
        )
        self.delete_by_id = to_raw_response_wrapper(
            connections.delete_by_id,
        )
        self.delete_by_provider = to_raw_response_wrapper(
            connections.delete_by_provider,
        )
        self.get_by_id = to_raw_response_wrapper(
            connections.get_by_id,
        )
        self.get_by_tag = to_raw_response_wrapper(
            connections.get_by_tag,
        )
        self.import_ = to_raw_response_wrapper(
            connections.import_,
        )
        self.list_documents = to_raw_response_wrapper(
            connections.list_documents,
        )
        self.resources = to_raw_response_wrapper(
            connections.resources,
        )


class AsyncConnectionsResourceWithRawResponse:
    def __init__(self, connections: AsyncConnectionsResource) -> None:
        self._connections = connections

        self.create = async_to_raw_response_wrapper(
            connections.create,
        )
        self.list = async_to_raw_response_wrapper(
            connections.list,
        )
        self.configure = async_to_raw_response_wrapper(
            connections.configure,
        )
        self.delete_by_id = async_to_raw_response_wrapper(
            connections.delete_by_id,
        )
        self.delete_by_provider = async_to_raw_response_wrapper(
            connections.delete_by_provider,
        )
        self.get_by_id = async_to_raw_response_wrapper(
            connections.get_by_id,
        )
        self.get_by_tag = async_to_raw_response_wrapper(
            connections.get_by_tag,
        )
        self.import_ = async_to_raw_response_wrapper(
            connections.import_,
        )
        self.list_documents = async_to_raw_response_wrapper(
            connections.list_documents,
        )
        self.resources = async_to_raw_response_wrapper(
            connections.resources,
        )


class ConnectionsResourceWithStreamingResponse:
    def __init__(self, connections: ConnectionsResource) -> None:
        self._connections = connections

        self.create = to_streamed_response_wrapper(
            connections.create,
        )
        self.list = to_streamed_response_wrapper(
            connections.list,
        )
        self.configure = to_streamed_response_wrapper(
            connections.configure,
        )
        self.delete_by_id = to_streamed_response_wrapper(
            connections.delete_by_id,
        )
        self.delete_by_provider = to_streamed_response_wrapper(
            connections.delete_by_provider,
        )
        self.get_by_id = to_streamed_response_wrapper(
            connections.get_by_id,
        )
        self.get_by_tag = to_streamed_response_wrapper(
            connections.get_by_tag,
        )
        self.import_ = to_streamed_response_wrapper(
            connections.import_,
        )
        self.list_documents = to_streamed_response_wrapper(
            connections.list_documents,
        )
        self.resources = to_streamed_response_wrapper(
            connections.resources,
        )


class AsyncConnectionsResourceWithStreamingResponse:
    def __init__(self, connections: AsyncConnectionsResource) -> None:
        self._connections = connections

        self.create = async_to_streamed_response_wrapper(
            connections.create,
        )
        self.list = async_to_streamed_response_wrapper(
            connections.list,
        )
        self.configure = async_to_streamed_response_wrapper(
            connections.configure,
        )
        self.delete_by_id = async_to_streamed_response_wrapper(
            connections.delete_by_id,
        )
        self.delete_by_provider = async_to_streamed_response_wrapper(
            connections.delete_by_provider,
        )
        self.get_by_id = async_to_streamed_response_wrapper(
            connections.get_by_id,
        )
        self.get_by_tag = async_to_streamed_response_wrapper(
            connections.get_by_tag,
        )
        self.import_ = async_to_streamed_response_wrapper(
            connections.import_,
        )
        self.list_documents = async_to_streamed_response_wrapper(
            connections.list_documents,
        )
        self.resources = async_to_streamed_response_wrapper(
            connections.resources,
        )
