# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Iterable, Optional

import httpx

from ..types import setting_update_params
from .._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
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
from ..types.setting_get_response import SettingGetResponse
from ..types.setting_update_response import SettingUpdateResponse

__all__ = ["SettingsResource", "AsyncSettingsResource"]


class SettingsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> SettingsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/supermemoryai/python-sdk#accessing-raw-response-data-eg-headers
        """
        return SettingsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SettingsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/supermemoryai/python-sdk#with_streaming_response
        """
        return SettingsResourceWithStreamingResponse(self)

    def update(
        self,
        *,
        chunk_size: Optional[int] | Omit = omit,
        exclude_items: Union[str, float, bool, Dict[str, object], Iterable[object], None] | Omit = omit,
        filter_prompt: Optional[str] | Omit = omit,
        github_client_id: Optional[str] | Omit = omit,
        github_client_secret: Optional[str] | Omit = omit,
        github_custom_key_enabled: Optional[bool] | Omit = omit,
        google_drive_client_id: Optional[str] | Omit = omit,
        google_drive_client_secret: Optional[str] | Omit = omit,
        google_drive_custom_key_enabled: Optional[bool] | Omit = omit,
        include_items: Union[str, float, bool, Dict[str, object], Iterable[object], None] | Omit = omit,
        notion_client_id: Optional[str] | Omit = omit,
        notion_client_secret: Optional[str] | Omit = omit,
        notion_custom_key_enabled: Optional[bool] | Omit = omit,
        onedrive_client_id: Optional[str] | Omit = omit,
        onedrive_client_secret: Optional[str] | Omit = omit,
        onedrive_custom_key_enabled: Optional[bool] | Omit = omit,
        should_llm_filter: Optional[bool] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SettingUpdateResponse:
        """
        Update settings for an organization

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._patch(
            "/v3/settings",
            body=maybe_transform(
                {
                    "chunk_size": chunk_size,
                    "exclude_items": exclude_items,
                    "filter_prompt": filter_prompt,
                    "github_client_id": github_client_id,
                    "github_client_secret": github_client_secret,
                    "github_custom_key_enabled": github_custom_key_enabled,
                    "google_drive_client_id": google_drive_client_id,
                    "google_drive_client_secret": google_drive_client_secret,
                    "google_drive_custom_key_enabled": google_drive_custom_key_enabled,
                    "include_items": include_items,
                    "notion_client_id": notion_client_id,
                    "notion_client_secret": notion_client_secret,
                    "notion_custom_key_enabled": notion_custom_key_enabled,
                    "onedrive_client_id": onedrive_client_id,
                    "onedrive_client_secret": onedrive_client_secret,
                    "onedrive_custom_key_enabled": onedrive_custom_key_enabled,
                    "should_llm_filter": should_llm_filter,
                },
                setting_update_params.SettingUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SettingUpdateResponse,
        )

    def get(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SettingGetResponse:
        """Get settings for an organization"""
        return self._get(
            "/v3/settings",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SettingGetResponse,
        )


class AsyncSettingsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncSettingsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/supermemoryai/python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncSettingsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSettingsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/supermemoryai/python-sdk#with_streaming_response
        """
        return AsyncSettingsResourceWithStreamingResponse(self)

    async def update(
        self,
        *,
        chunk_size: Optional[int] | Omit = omit,
        exclude_items: Union[str, float, bool, Dict[str, object], Iterable[object], None] | Omit = omit,
        filter_prompt: Optional[str] | Omit = omit,
        github_client_id: Optional[str] | Omit = omit,
        github_client_secret: Optional[str] | Omit = omit,
        github_custom_key_enabled: Optional[bool] | Omit = omit,
        google_drive_client_id: Optional[str] | Omit = omit,
        google_drive_client_secret: Optional[str] | Omit = omit,
        google_drive_custom_key_enabled: Optional[bool] | Omit = omit,
        include_items: Union[str, float, bool, Dict[str, object], Iterable[object], None] | Omit = omit,
        notion_client_id: Optional[str] | Omit = omit,
        notion_client_secret: Optional[str] | Omit = omit,
        notion_custom_key_enabled: Optional[bool] | Omit = omit,
        onedrive_client_id: Optional[str] | Omit = omit,
        onedrive_client_secret: Optional[str] | Omit = omit,
        onedrive_custom_key_enabled: Optional[bool] | Omit = omit,
        should_llm_filter: Optional[bool] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SettingUpdateResponse:
        """
        Update settings for an organization

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._patch(
            "/v3/settings",
            body=await async_maybe_transform(
                {
                    "chunk_size": chunk_size,
                    "exclude_items": exclude_items,
                    "filter_prompt": filter_prompt,
                    "github_client_id": github_client_id,
                    "github_client_secret": github_client_secret,
                    "github_custom_key_enabled": github_custom_key_enabled,
                    "google_drive_client_id": google_drive_client_id,
                    "google_drive_client_secret": google_drive_client_secret,
                    "google_drive_custom_key_enabled": google_drive_custom_key_enabled,
                    "include_items": include_items,
                    "notion_client_id": notion_client_id,
                    "notion_client_secret": notion_client_secret,
                    "notion_custom_key_enabled": notion_custom_key_enabled,
                    "onedrive_client_id": onedrive_client_id,
                    "onedrive_client_secret": onedrive_client_secret,
                    "onedrive_custom_key_enabled": onedrive_custom_key_enabled,
                    "should_llm_filter": should_llm_filter,
                },
                setting_update_params.SettingUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SettingUpdateResponse,
        )

    async def get(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SettingGetResponse:
        """Get settings for an organization"""
        return await self._get(
            "/v3/settings",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SettingGetResponse,
        )


class SettingsResourceWithRawResponse:
    def __init__(self, settings: SettingsResource) -> None:
        self._settings = settings

        self.update = to_raw_response_wrapper(
            settings.update,
        )
        self.get = to_raw_response_wrapper(
            settings.get,
        )


class AsyncSettingsResourceWithRawResponse:
    def __init__(self, settings: AsyncSettingsResource) -> None:
        self._settings = settings

        self.update = async_to_raw_response_wrapper(
            settings.update,
        )
        self.get = async_to_raw_response_wrapper(
            settings.get,
        )


class SettingsResourceWithStreamingResponse:
    def __init__(self, settings: SettingsResource) -> None:
        self._settings = settings

        self.update = to_streamed_response_wrapper(
            settings.update,
        )
        self.get = to_streamed_response_wrapper(
            settings.get,
        )


class AsyncSettingsResourceWithStreamingResponse:
    def __init__(self, settings: AsyncSettingsResource) -> None:
        self._settings = settings

        self.update = async_to_streamed_response_wrapper(
            settings.update,
        )
        self.get = async_to_streamed_response_wrapper(
            settings.get,
        )
