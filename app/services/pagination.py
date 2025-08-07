import math
from typing import Generic, List, TypeVar

from fastapi import Query as FastAPIQuery
from pydantic import BaseModel
from sqlalchemy.orm import Query

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Simple paginated response"""

    items: List[T]  # The actual data (brands, creative sets, etc.)
    total: int  # Total number of items in database
    page: int  # Current page number
    size: int  # Items per page
    total_pages: int  # Total number of pages
    has_next: bool  # Is there a next page?
    has_previous: bool  # Is there a previous page?


# Dependency to get pagination parameters from URL
def get_pagination(
    page: int = FastAPIQuery(1, ge=1, description="Page number (starts from 1)"),
    size: int = FastAPIQuery(20, ge=1, le=100, description="Items per page (max 100)"),
):
    return {"page": page, "size": size}


def paginate_query(query: Query, page: int, size: int) -> PaginatedResponse:
    """Apply pagination to any SQLAlchemy query"""

    # Count total items
    total = query.count()

    # Calculate pagination values
    total_pages = math.ceil(total / size) if total > 0 else 1
    offset = (page - 1) * size

    # Get items for current page
    items = query.offset(offset).limit(size).all()

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1,
    )
