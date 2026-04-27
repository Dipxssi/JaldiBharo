#defines the databases tables as Python classes 

import uuid
from uuid import UUID
from sqlmodel import SQLModel, Field
from typing import List, Optional
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column
 
 #defines the Listing table in the databases 
class Listing(SQLModel , table=True):
  
  id: Optional[UUID] = Field(default_factory=uuid.uuid4 , primary_key=True)

  image_url : str = Field(description="URL  image stored in Cloudinary")

  title: str
  description: str
  category: str
  condition: str
  suggested_price: int
  tags: str
  embedding: Optional[List[float]] = Field(default=None , sa_column=Column(Vector(768)))
