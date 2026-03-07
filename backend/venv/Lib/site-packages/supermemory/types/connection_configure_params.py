# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Required, TypedDict

__all__ = ["ConnectionConfigureParams"]


class ConnectionConfigureParams(TypedDict, total=False):
    resources: Required[Iterable[Dict[str, object]]]
