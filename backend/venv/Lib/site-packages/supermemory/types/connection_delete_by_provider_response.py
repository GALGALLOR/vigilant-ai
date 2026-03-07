# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["ConnectionDeleteByProviderResponse"]


class ConnectionDeleteByProviderResponse(BaseModel):
    id: str

    provider: str
