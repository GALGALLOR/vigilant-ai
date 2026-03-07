# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["ConnectionConfigureResponse"]


class ConnectionConfigureResponse(BaseModel):
    message: str

    success: bool

    webhooks_registered: Optional[float] = FieldInfo(alias="webhooksRegistered", default=None)
