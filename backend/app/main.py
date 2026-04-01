from fastapi import FastAPI , UploadFile , File , HTTPException, Depends
from .services import generate_listing_from_image
from .models import Listing
from sqlmodel import Session , select
from .database import get_session , create_db_and_tables
from .models import Listing
from .utils import upload_to_cloudinary, create_collage
from contextlib import asynccontextmanager

MAX_FILE_SIZE = 10 * 1024 * 1024


@asynccontextmanager
async def lifespan(app:FastAPI):
  create_db_and_tables()
  print("database tables created!")

  yield

  print("Shutting down........")

app = FastAPI(lifespan=lifespan)


@app.post("/upload" , response_model=Listing)
async def upload_images(files: list[UploadFile] = File(...),
                        db: Session = Depends(get_session)):
  
  image_bytes_list = []

  for file in files:
    if file.size > MAX_FILE_SIZE:
      raise HTTPException(
                   status_code=413, 
                detail=f"File {file.filename} is too large! Limit is 10MB."
      )
    if not file.content_type.startswith("image/"):
      raise HTTPException(
                status_code=400, 
                detail=f"File {file.filename} is not an image."
            )

    content = await file.read()
    image_bytes_list.append(content)
  
  collage_bytes = create_collage(image_bytes_list)

  image_url = upload_to_cloudinary(collage_bytes)

  ai_data = await generate_listing_from_image(collage_bytes)
 
  tags_str = ", ".join(ai_data.tags)

  new_listing = Listing(
    title=ai_data.title,
    description=ai_data.description,
    category=ai_data.category,
    condition=ai_data.condition,
    suggested_price=ai_data.suggested_price,
    tags=tags_str,         
    image_url=image_url    
  )

  db.add(new_listing)
  db.commit()
  db.refresh(new_listing)
  return new_listing


  
@app.get("/listings" , response_model= list[Listing])
def get_listings(db: Session = Depends(get_session)):
  statement = select(Listing)
  results = db.exec(statement)
  return results.all()