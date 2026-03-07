# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from .._models import BaseModel

__all__ = ["ConnectionResourcesResponse"]


class ConnectionResourcesResponse(BaseModel):
    resources: List[Dict[str, object]]

    total_count: Optional[float] = None
