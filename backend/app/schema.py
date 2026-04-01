from enum import Enum
from pydantic import BaseModel


class CategoryEnum(str , Enum):
  electronics = "electronics"
  books = "books"
  clothes = "clothes"
  bags = "bags"
  accessories = "accessories"
  shoes = "shoes"

class ListingResponse(BaseModel):
  title: str
  description: str
  category: CategoryEnum
  condition : str
  suggested_price: int
  tags: list[str]