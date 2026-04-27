#defines the data strucrure for API req and res 

from enum import Enum
from pydantic import BaseModel

# allowed categories 
class CategoryEnum(str , Enum):
  electronics = "electronics"
  books = "books"
  clothes = "clothes"
  bags = "bags"
  accessories = "accessories"
  shoes = "shoes"

# ai returns when it sees an img 
class ListingResponse(BaseModel):
  title: str
  description: str
  category: CategoryEnum
  condition : str
  suggested_price: int
  tags: list[str]

#strucutre for web search res 
class MarketReference(BaseModel):
  url: str
  content: str

# structure for the final price descion after market research 

class PriceRefinementResponse(BaseModel):
  final_suggested_price: int
  confidence: str
  reasoning: str