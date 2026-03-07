# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Iterable, Optional
from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["SettingUpdateParams"]


class SettingUpdateParams(TypedDict, total=False):
    chunk_size: Annotated[Optional[int], PropertyInfo(alias="chunkSize")]

    exclude_items: Annotated[
        Union[str, float, bool, Dict[str, object], Iterable[object], None], PropertyInfo(alias="excludeItems")
    ]

    filter_prompt: Annotated[Optional[str], PropertyInfo(alias="filterPrompt")]

    github_client_id: Annotated[Optional[str], PropertyInfo(alias="githubClientId")]

    github_client_secret: Annotated[Optional[str], PropertyInfo(alias="githubClientSecret")]

    github_custom_key_enabled: Annotated[Optional[bool], PropertyInfo(alias="githubCustomKeyEnabled")]

    google_drive_client_id: Annotated[Optional[str], PropertyInfo(alias="googleDriveClientId")]

    google_drive_client_secret: Annotated[Optional[str], PropertyInfo(alias="googleDriveClientSecret")]

    google_drive_custom_key_enabled: Annotated[Optional[bool], PropertyInfo(alias="googleDriveCustomKeyEnabled")]

    include_items: Annotated[
        Union[str, float, bool, Dict[str, object], Iterable[object], None], PropertyInfo(alias="includeItems")
    ]

    notion_client_id: Annotated[Optional[str], PropertyInfo(alias="notionClientId")]

    notion_client_secret: Annotated[Optional[str], PropertyInfo(alias="notionClientSecret")]

    notion_custom_key_enabled: Annotated[Optional[bool], PropertyInfo(alias="notionCustomKeyEnabled")]

    onedrive_client_id: Annotated[Optional[str], PropertyInfo(alias="onedriveClientId")]

    onedrive_client_secret: Annotated[Optional[str], PropertyInfo(alias="onedriveClientSecret")]

    onedrive_custom_key_enabled: Annotated[Optional[bool], PropertyInfo(alias="onedriveCustomKeyEnabled")]

    should_llm_filter: Annotated[Optional[bool], PropertyInfo(alias="shouldLLMFilter")]
