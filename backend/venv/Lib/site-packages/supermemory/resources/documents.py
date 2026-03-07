# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Mapping, Iterable, cast
from typing_extensions import Literal

import httpx

from ..types import (
    document_add_params,
    document_list_params,
    document_update_params,
    document_batch_add_params,
    document_delete_bulk_params,
    document_upload_file_params,
)
from .._types import Body, Omit, Query, Headers, NoneType, NotGiven, FileTypes, SequenceNotStr, omit, not_given
from .._utils import extract_files, maybe_transform, deepcopy_minimal, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.document_add_response import DocumentAddResponse
from ..types.document_get_response import DocumentGetResponse
from ..types.document_list_response import DocumentListResponse
from ..types.document_update_response import DocumentUpdateResponse
from ..types.document_batch_add_response import DocumentBatchAddResponse
from ..types.document_delete_bulk_response import DocumentDeleteBulkResponse
from ..types.document_upload_file_response import DocumentUploadFileResponse
from ..types.document_list_processing_response import DocumentListProcessingResponse

__all__ = ["DocumentsResource", "AsyncDocumentsResource"]


class DocumentsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> DocumentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/supermemoryai/python-sdk#accessing-raw-response-data-eg-headers
        """
        return DocumentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DocumentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/supermemoryai/python-sdk#with_streaming_response
        """
        return DocumentsResourceWithStreamingResponse(self)

    def update(
        self,
        id: str,
        *,
        container_tag: str | Omit = omit,
        container_tags: SequenceNotStr[str] | Omit = omit,
        content: str | Omit = omit,
        custom_id: str | Omit = omit,
        metadata: Dict[str, Union[str, float, bool, SequenceNotStr[str]]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentUpdateResponse:
        """
        Update a document with any content type (text, url, file, etc.) and metadata

        Args:
          container_tag: Optional tag this document should be containerized by. This can be an ID for
              your user, a project ID, or any other identifier you wish to use to group
              documents.

          container_tags: (DEPRECATED: Use containerTag instead) Optional tags this document should be
              containerized by. This can be an ID for your user, a project ID, or any other
              identifier you wish to use to group documents.

          content: The content to extract and process into a document. This can be a URL to a
              website, a PDF, an image, or a video.

              Plaintext: Any plaintext format

              URL: A URL to a website, PDF, image, or video

              We automatically detect the content type from the url's response format.

          custom_id: Optional custom ID of the document. This could be an ID from your database that
              will uniquely identify this document.

          metadata: Optional metadata for the document. This is used to store additional information
              about the document. You can use this to store any additional information you
              need about the document. Metadata can be filtered through. Keys must be strings
              and are case sensitive. Values can be strings, numbers, or booleans. You cannot
              nest objects.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._patch(
            f"/v3/documents/{id}",
            body=maybe_transform(
                {
                    "container_tag": container_tag,
                    "container_tags": container_tags,
                    "content": content,
                    "custom_id": custom_id,
                    "metadata": metadata,
                },
                document_update_params.DocumentUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentUpdateResponse,
        )

    def list(
        self,
        *,
        container_tags: SequenceNotStr[str] | Omit = omit,
        filters: document_list_params.Filters | Omit = omit,
        include_content: bool | Omit = omit,
        limit: Union[str, float] | Omit = omit,
        order: Literal["asc", "desc"] | Omit = omit,
        page: Union[str, float] | Omit = omit,
        sort: Literal["createdAt", "updatedAt"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentListResponse:
        """
        Retrieves a paginated list of documents with their metadata and workflow status

        Args:
          container_tags: Optional tags this document should be containerized by. This can be an ID for
              your user, a project ID, or any other identifier you wish to use to group
              documents.

          filters: Optional filters to apply to the search. Can be a JSON string or Query object.

          include_content: Whether to include the content field in the response. Warning: This can make
              responses significantly larger.

          limit: Number of items per page

          order: Sort order

          page: Page number to fetch

          sort: Field to sort by

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v3/documents/list",
            body=maybe_transform(
                {
                    "container_tags": container_tags,
                    "filters": filters,
                    "include_content": include_content,
                    "limit": limit,
                    "order": order,
                    "page": page,
                    "sort": sort,
                },
                document_list_params.DocumentListParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentListResponse,
        )

    def delete(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Delete a document by ID or customId

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/v3/documents/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def add(
        self,
        *,
        content: str,
        container_tag: str | Omit = omit,
        container_tags: SequenceNotStr[str] | Omit = omit,
        custom_id: str | Omit = omit,
        entity_context: str | Omit = omit,
        metadata: Dict[str, Union[str, float, bool, SequenceNotStr[str]]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentAddResponse:
        """
        Add a document with any content type (text, url, file, etc.) and metadata

        Args:
          content: The content to extract and process into a document. This can be a URL to a
              website, a PDF, an image, or a video.

          container_tag: Optional tag this document should be containerized by. Max 100 characters,
              alphanumeric with hyphens and underscores only.

          custom_id: Optional custom ID of the document. Max 100 characters, alphanumeric with
              hyphens and underscores only.

          entity_context: Optional entity context for this container tag. Max 1500 characters. Used during
              document processing to guide memory extraction.

          metadata: Optional metadata for the document.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v3/documents",
            body=maybe_transform(
                {
                    "content": content,
                    "container_tag": container_tag,
                    "container_tags": container_tags,
                    "custom_id": custom_id,
                    "entity_context": entity_context,
                    "metadata": metadata,
                },
                document_add_params.DocumentAddParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentAddResponse,
        )

    def batch_add(
        self,
        *,
        documents: Union[Iterable[document_batch_add_params.DocumentsUnionMember0], SequenceNotStr[str]],
        container_tag: str | Omit = omit,
        container_tags: SequenceNotStr[str] | Omit = omit,
        content: None | Omit = omit,
        metadata: Dict[str, Union[str, float, bool, SequenceNotStr[str]]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentBatchAddResponse:
        """Add multiple documents in a single request.

        Each document can have any content
        type (text, url, file, etc.) and metadata

        Args:
          container_tag: Optional tag this document should be containerized by. This can be an ID for
              your user, a project ID, or any other identifier you wish to use to group
              documents.

          container_tags: (DEPRECATED: Use containerTag instead) Optional tags this document should be
              containerized by. This can be an ID for your user, a project ID, or any other
              identifier you wish to use to group documents.

          metadata: Optional metadata for the document. This is used to store additional information
              about the document. You can use this to store any additional information you
              need about the document. Metadata can be filtered through. Keys must be strings
              and are case sensitive. Values can be strings, numbers, or booleans. You cannot
              nest objects.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v3/documents/batch",
            body=maybe_transform(
                {
                    "documents": documents,
                    "container_tag": container_tag,
                    "container_tags": container_tags,
                    "content": content,
                    "metadata": metadata,
                },
                document_batch_add_params.DocumentBatchAddParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentBatchAddResponse,
        )

    def delete_bulk(
        self,
        *,
        container_tags: SequenceNotStr[str] | Omit = omit,
        ids: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentDeleteBulkResponse:
        """
        Bulk delete documents by IDs or container tags

        Args:
          container_tags: Array of container tags - all documents in these containers will be deleted

          ids: Array of document IDs to delete (max 100 at once)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._delete(
            "/v3/documents/bulk",
            body=maybe_transform(
                {
                    "container_tags": container_tags,
                    "ids": ids,
                },
                document_delete_bulk_params.DocumentDeleteBulkParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentDeleteBulkResponse,
        )

    def get(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentGetResponse:
        """
        Get a document by ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/v3/documents/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentGetResponse,
        )

    def list_processing(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentListProcessingResponse:
        """Get documents that are currently being processed"""
        return self._get(
            "/v3/documents/processing",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentListProcessingResponse,
        )

    def upload_file(
        self,
        *,
        file: FileTypes,
        container_tags: str | Omit = omit,
        file_type: str | Omit = omit,
        metadata: str | Omit = omit,
        mime_type: str | Omit = omit,
        use_advanced_processing: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentUploadFileResponse:
        """
        Upload a file to be processed

        Args:
          file: File to upload and process

          container_tags: Optional container tags. Can be either a JSON string of an array (e.g.,
              '["user_123", "project_123"]') or a single string (e.g., 'user_123'). Single
              strings will be automatically converted to an array.

          file_type:
              Optional file type override to force specific processing behavior. Valid values:
              text, pdf, tweet, google_doc, google_slide, google_sheet, image, video,
              notion_doc, webpage, onedrive

          metadata: Optional metadata for the document as a JSON string. This is used to store
              additional information about the document. Keys must be strings and values can
              be strings, numbers, or booleans.

          mime_type: Required when fileType is 'image' or 'video'. Specifies the exact MIME type to
              use (e.g., 'image/png', 'image/jpeg', 'video/mp4', 'video/webm')

          use_advanced_processing: DEPRECATED: This field is no longer used. Advanced PDF processing is now
              automatic with our hybrid Mistral OCR + Gemini pipeline. This parameter will be
              accepted but ignored for backwards compatibility.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal(
            {
                "file": file,
                "container_tags": container_tags,
                "file_type": file_type,
                "metadata": metadata,
                "mime_type": mime_type,
                "use_advanced_processing": use_advanced_processing,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["file"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return self._post(
            "/v3/documents/file",
            body=maybe_transform(body, document_upload_file_params.DocumentUploadFileParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentUploadFileResponse,
        )


class AsyncDocumentsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncDocumentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/supermemoryai/python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncDocumentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDocumentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/supermemoryai/python-sdk#with_streaming_response
        """
        return AsyncDocumentsResourceWithStreamingResponse(self)

    async def update(
        self,
        id: str,
        *,
        container_tag: str | Omit = omit,
        container_tags: SequenceNotStr[str] | Omit = omit,
        content: str | Omit = omit,
        custom_id: str | Omit = omit,
        metadata: Dict[str, Union[str, float, bool, SequenceNotStr[str]]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentUpdateResponse:
        """
        Update a document with any content type (text, url, file, etc.) and metadata

        Args:
          container_tag: Optional tag this document should be containerized by. This can be an ID for
              your user, a project ID, or any other identifier you wish to use to group
              documents.

          container_tags: (DEPRECATED: Use containerTag instead) Optional tags this document should be
              containerized by. This can be an ID for your user, a project ID, or any other
              identifier you wish to use to group documents.

          content: The content to extract and process into a document. This can be a URL to a
              website, a PDF, an image, or a video.

              Plaintext: Any plaintext format

              URL: A URL to a website, PDF, image, or video

              We automatically detect the content type from the url's response format.

          custom_id: Optional custom ID of the document. This could be an ID from your database that
              will uniquely identify this document.

          metadata: Optional metadata for the document. This is used to store additional information
              about the document. You can use this to store any additional information you
              need about the document. Metadata can be filtered through. Keys must be strings
              and are case sensitive. Values can be strings, numbers, or booleans. You cannot
              nest objects.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._patch(
            f"/v3/documents/{id}",
            body=await async_maybe_transform(
                {
                    "container_tag": container_tag,
                    "container_tags": container_tags,
                    "content": content,
                    "custom_id": custom_id,
                    "metadata": metadata,
                },
                document_update_params.DocumentUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentUpdateResponse,
        )

    async def list(
        self,
        *,
        container_tags: SequenceNotStr[str] | Omit = omit,
        filters: document_list_params.Filters | Omit = omit,
        include_content: bool | Omit = omit,
        limit: Union[str, float] | Omit = omit,
        order: Literal["asc", "desc"] | Omit = omit,
        page: Union[str, float] | Omit = omit,
        sort: Literal["createdAt", "updatedAt"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentListResponse:
        """
        Retrieves a paginated list of documents with their metadata and workflow status

        Args:
          container_tags: Optional tags this document should be containerized by. This can be an ID for
              your user, a project ID, or any other identifier you wish to use to group
              documents.

          filters: Optional filters to apply to the search. Can be a JSON string or Query object.

          include_content: Whether to include the content field in the response. Warning: This can make
              responses significantly larger.

          limit: Number of items per page

          order: Sort order

          page: Page number to fetch

          sort: Field to sort by

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v3/documents/list",
            body=await async_maybe_transform(
                {
                    "container_tags": container_tags,
                    "filters": filters,
                    "include_content": include_content,
                    "limit": limit,
                    "order": order,
                    "page": page,
                    "sort": sort,
                },
                document_list_params.DocumentListParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentListResponse,
        )

    async def delete(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Delete a document by ID or customId

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/v3/documents/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def add(
        self,
        *,
        content: str,
        container_tag: str | Omit = omit,
        container_tags: SequenceNotStr[str] | Omit = omit,
        custom_id: str | Omit = omit,
        entity_context: str | Omit = omit,
        metadata: Dict[str, Union[str, float, bool, SequenceNotStr[str]]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentAddResponse:
        """
        Add a document with any content type (text, url, file, etc.) and metadata

        Args:
          content: The content to extract and process into a document. This can be a URL to a
              website, a PDF, an image, or a video.

          container_tag: Optional tag this document should be containerized by. Max 100 characters,
              alphanumeric with hyphens and underscores only.

          custom_id: Optional custom ID of the document. Max 100 characters, alphanumeric with
              hyphens and underscores only.

          entity_context: Optional entity context for this container tag. Max 1500 characters. Used during
              document processing to guide memory extraction.

          metadata: Optional metadata for the document.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v3/documents",
            body=await async_maybe_transform(
                {
                    "content": content,
                    "container_tag": container_tag,
                    "container_tags": container_tags,
                    "custom_id": custom_id,
                    "entity_context": entity_context,
                    "metadata": metadata,
                },
                document_add_params.DocumentAddParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentAddResponse,
        )

    async def batch_add(
        self,
        *,
        documents: Union[Iterable[document_batch_add_params.DocumentsUnionMember0], SequenceNotStr[str]],
        container_tag: str | Omit = omit,
        container_tags: SequenceNotStr[str] | Omit = omit,
        content: None | Omit = omit,
        metadata: Dict[str, Union[str, float, bool, SequenceNotStr[str]]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentBatchAddResponse:
        """Add multiple documents in a single request.

        Each document can have any content
        type (text, url, file, etc.) and metadata

        Args:
          container_tag: Optional tag this document should be containerized by. This can be an ID for
              your user, a project ID, or any other identifier you wish to use to group
              documents.

          container_tags: (DEPRECATED: Use containerTag instead) Optional tags this document should be
              containerized by. This can be an ID for your user, a project ID, or any other
              identifier you wish to use to group documents.

          metadata: Optional metadata for the document. This is used to store additional information
              about the document. You can use this to store any additional information you
              need about the document. Metadata can be filtered through. Keys must be strings
              and are case sensitive. Values can be strings, numbers, or booleans. You cannot
              nest objects.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v3/documents/batch",
            body=await async_maybe_transform(
                {
                    "documents": documents,
                    "container_tag": container_tag,
                    "container_tags": container_tags,
                    "content": content,
                    "metadata": metadata,
                },
                document_batch_add_params.DocumentBatchAddParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentBatchAddResponse,
        )

    async def delete_bulk(
        self,
        *,
        container_tags: SequenceNotStr[str] | Omit = omit,
        ids: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentDeleteBulkResponse:
        """
        Bulk delete documents by IDs or container tags

        Args:
          container_tags: Array of container tags - all documents in these containers will be deleted

          ids: Array of document IDs to delete (max 100 at once)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._delete(
            "/v3/documents/bulk",
            body=await async_maybe_transform(
                {
                    "container_tags": container_tags,
                    "ids": ids,
                },
                document_delete_bulk_params.DocumentDeleteBulkParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentDeleteBulkResponse,
        )

    async def get(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentGetResponse:
        """
        Get a document by ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/v3/documents/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentGetResponse,
        )

    async def list_processing(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentListProcessingResponse:
        """Get documents that are currently being processed"""
        return await self._get(
            "/v3/documents/processing",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentListProcessingResponse,
        )

    async def upload_file(
        self,
        *,
        file: FileTypes,
        container_tags: str | Omit = omit,
        file_type: str | Omit = omit,
        metadata: str | Omit = omit,
        mime_type: str | Omit = omit,
        use_advanced_processing: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentUploadFileResponse:
        """
        Upload a file to be processed

        Args:
          file: File to upload and process

          container_tags: Optional container tags. Can be either a JSON string of an array (e.g.,
              '["user_123", "project_123"]') or a single string (e.g., 'user_123'). Single
              strings will be automatically converted to an array.

          file_type:
              Optional file type override to force specific processing behavior. Valid values:
              text, pdf, tweet, google_doc, google_slide, google_sheet, image, video,
              notion_doc, webpage, onedrive

          metadata: Optional metadata for the document as a JSON string. This is used to store
              additional information about the document. Keys must be strings and values can
              be strings, numbers, or booleans.

          mime_type: Required when fileType is 'image' or 'video'. Specifies the exact MIME type to
              use (e.g., 'image/png', 'image/jpeg', 'video/mp4', 'video/webm')

          use_advanced_processing: DEPRECATED: This field is no longer used. Advanced PDF processing is now
              automatic with our hybrid Mistral OCR + Gemini pipeline. This parameter will be
              accepted but ignored for backwards compatibility.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal(
            {
                "file": file,
                "container_tags": container_tags,
                "file_type": file_type,
                "metadata": metadata,
                "mime_type": mime_type,
                "use_advanced_processing": use_advanced_processing,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["file"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return await self._post(
            "/v3/documents/file",
            body=await async_maybe_transform(body, document_upload_file_params.DocumentUploadFileParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentUploadFileResponse,
        )


class DocumentsResourceWithRawResponse:
    def __init__(self, documents: DocumentsResource) -> None:
        self._documents = documents

        self.update = to_raw_response_wrapper(
            documents.update,
        )
        self.list = to_raw_response_wrapper(
            documents.list,
        )
        self.delete = to_raw_response_wrapper(
            documents.delete,
        )
        self.add = to_raw_response_wrapper(
            documents.add,
        )
        self.batch_add = to_raw_response_wrapper(
            documents.batch_add,
        )
        self.delete_bulk = to_raw_response_wrapper(
            documents.delete_bulk,
        )
        self.get = to_raw_response_wrapper(
            documents.get,
        )
        self.list_processing = to_raw_response_wrapper(
            documents.list_processing,
        )
        self.upload_file = to_raw_response_wrapper(
            documents.upload_file,
        )


class AsyncDocumentsResourceWithRawResponse:
    def __init__(self, documents: AsyncDocumentsResource) -> None:
        self._documents = documents

        self.update = async_to_raw_response_wrapper(
            documents.update,
        )
        self.list = async_to_raw_response_wrapper(
            documents.list,
        )
        self.delete = async_to_raw_response_wrapper(
            documents.delete,
        )
        self.add = async_to_raw_response_wrapper(
            documents.add,
        )
        self.batch_add = async_to_raw_response_wrapper(
            documents.batch_add,
        )
        self.delete_bulk = async_to_raw_response_wrapper(
            documents.delete_bulk,
        )
        self.get = async_to_raw_response_wrapper(
            documents.get,
        )
        self.list_processing = async_to_raw_response_wrapper(
            documents.list_processing,
        )
        self.upload_file = async_to_raw_response_wrapper(
            documents.upload_file,
        )


class DocumentsResourceWithStreamingResponse:
    def __init__(self, documents: DocumentsResource) -> None:
        self._documents = documents

        self.update = to_streamed_response_wrapper(
            documents.update,
        )
        self.list = to_streamed_response_wrapper(
            documents.list,
        )
        self.delete = to_streamed_response_wrapper(
            documents.delete,
        )
        self.add = to_streamed_response_wrapper(
            documents.add,
        )
        self.batch_add = to_streamed_response_wrapper(
            documents.batch_add,
        )
        self.delete_bulk = to_streamed_response_wrapper(
            documents.delete_bulk,
        )
        self.get = to_streamed_response_wrapper(
            documents.get,
        )
        self.list_processing = to_streamed_response_wrapper(
            documents.list_processing,
        )
        self.upload_file = to_streamed_response_wrapper(
            documents.upload_file,
        )


class AsyncDocumentsResourceWithStreamingResponse:
    def __init__(self, documents: AsyncDocumentsResource) -> None:
        self._documents = documents

        self.update = async_to_streamed_response_wrapper(
            documents.update,
        )
        self.list = async_to_streamed_response_wrapper(
            documents.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            documents.delete,
        )
        self.add = async_to_streamed_response_wrapper(
            documents.add,
        )
        self.batch_add = async_to_streamed_response_wrapper(
            documents.batch_add,
        )
        self.delete_bulk = async_to_streamed_response_wrapper(
            documents.delete_bulk,
        )
        self.get = async_to_streamed_response_wrapper(
            documents.get,
        )
        self.list_processing = async_to_streamed_response_wrapper(
            documents.list_processing,
        )
        self.upload_file = async_to_streamed_response_wrapper(
            documents.upload_file,
        )
