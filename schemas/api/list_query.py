from typing import Annotated

from fastapi import Depends, Query


class ListQuery:
    def __init__(
        self,
        limit: int = Query(10, gt=0, description='Number of items to return'),
        offset: int = Query(0, ge=0, description='Number of items to skip'),
        order_by: str | None = Query(None, description='Sort field (use -field for descending, e.g. -created_at)'),
    ):
        self.limit = limit
        self.offset = offset
        self.order_by = order_by


ListQueryDep = Annotated[ListQuery, Depends()]
