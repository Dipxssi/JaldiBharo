import uuid
from uuid import UUID
from sqlmodel import SQLModel, Field
from typing import List, Optional

class Listing(SQLModel , table=True):
  
  id: Optional[UUID] = Field(default_factory=uuid.uuid4 , primary_key=True)
  image_url : str = Field(description="URL tot the image stored in Cloudinary")

  title: str
  description: str
  category: str
  condition: str
  suggested_price: int
  tags: str
