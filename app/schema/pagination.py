from typing import Generic, List, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationResponseSchema(BaseModel, Generic[T]):
    items: List[T] = Field(..., description="List of items in the current page")
    total_items: int = Field(..., description="Total number of items across all pages")
    total_pages: int = Field(..., description="Total number of pages available")
    current_page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    has_next: bool = Field(..., description="Indicates if there is a next page")
    has_previous: bool = Field(..., description="Indicates if there is a previous page")
