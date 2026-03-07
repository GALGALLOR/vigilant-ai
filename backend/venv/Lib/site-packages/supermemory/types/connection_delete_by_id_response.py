# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["ConnectionDeleteByIDResponse"]


class ConnectionDeleteByIDResponse(BaseModel):
    id: str

    provider: str
