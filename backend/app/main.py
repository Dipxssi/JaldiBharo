from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from contextlib import asynccontextmanager
from typing import List
from app.services import generate_listing_from_image
from app.models import Listing
from app.database import get_session, create_db_and_tables
from app.utils import upload_to_cloudinary, create_collage
MAX_FILE_SIZE = 10 * 1024 * 1024

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    print(" Database tables created and ready!")
    yield
    print("Shutting down........")

app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", 
        "http://localhost:5173", 
        "https://jaldi-bharo.vercel.app",
        "https://jaldi-bharo.vercel.app/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload", response_model=Listing)
async def upload_images(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_session)
):
    image_bytes_list = []

    for file in files:
        if file.size is not None and file.size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File {file.filename} is too large! Limit is 10MB.",
            )
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File {file.filename} is too large! Limit is 10MB.",
            )
        if file.content_type is None or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail=f"File {file.filename} is not an image.",
            )

        image_bytes_list.append(content)
    
    
    collage_bytes = create_collage(image_bytes_list)

   
    image_url = upload_to_cloudinary(collage_bytes)

    
    ai_data = await generate_listing_from_image(collage_bytes)
    if not ai_data:
        raise HTTPException(status_code=500, detail="AI failed to generate data")
    
    tags_str = ", ".join(ai_data.tags) if ai_data.tags else ""

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

@app.get("/listings", response_model=List[Listing])
def get_listings(db: Session = Depends(get_session)):
    statement = select(Listing)
    results = db.exec(statement)
    return results.all()