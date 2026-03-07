# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["ConnectionCreateResponse"]


class ConnectionCreateResponse(BaseModel):
    id: str

    auth_link: str = FieldInfo(alias="authLink")

    expires_in: str = FieldInfo(alias="expiresIn")

    redirects_to: Optional[str] = FieldInfo(alias="redirectsTo", default=None)
