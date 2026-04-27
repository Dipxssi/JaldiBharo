#defines all the routes and coordinates the app's actions 
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from sqlalchemy import inspect
from sqlmodel import Session, select
from contextlib import asynccontextmanager
from typing import List
from app.services import generate_listing_from_image, search_market_prices, refine_price_with_market_context , get_embedding
from app.models import Listing
from app.database import get_session, create_db_and_tables
from app.utils import upload_to_cloudinary, create_collage
from app.api.deps import get_current_user

MAX_FILE_SIZE = 10 * 1024 * 1024

#ensures the databases exists 
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

@app.get("/")
def home():
    return {"message": "welcome to jaldibharo! the public area is open "}

@app.get("/search")
async def protected_search(
    query: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    query_vector = await get_embedding(query)

    embedding_col = inspect(Listing).columns["embedding"]
    results = db.exec(
        select(Listing)
        .order_by(embedding_col.l2_distance(query_vector))
        .limit(5)
    ).all()
    return{
        "message": f"Hello{current_user['sub']}",
        "user":current_user['sub'],
        "tier": current_user.get("tier", "guest"),
        "results": results,
        "status":"Sucess!You accessed the protected area"
    }

#handles img uploads 
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

   
    image_url =await run_in_threadpool( upload_to_cloudinary,collage_bytes)

    
    ai_data = await generate_listing_from_image(collage_bytes)
    if not ai_data:
        raise HTTPException(status_code=500, detail="AI failed to generate data")
    
    text_to_embed = f"{ai_data.title} {ai_data.description}"

    embedding_vector = await get_embedding(text_to_embed)
    
    market_data = await search_market_prices(f"{ai_data.title} used market price")
    price_decision = await refine_price_with_market_context(ai_data, market_data)
    if price_decision is not None:
        ai_data.suggested_price = int(price_decision.final_suggested_price)
    
    tags_str = ", ".join(ai_data.tags) if ai_data.tags else ""

    new_listing = Listing(
        title=ai_data.title,
        description=ai_data.description,
        category=ai_data.category,
        condition=ai_data.condition,
        suggested_price=ai_data.suggested_price,
        tags=tags_str,         
        image_url=image_url,
        embedding= embedding_vector    
    )

    db.add(new_listing)
    db.commit()
    db.refresh(new_listing)
    return new_listing

#fetches all the saved items to show in the ui 
@app.get("/listings", response_model=List[Listing])
def get_listings(db: Session = Depends(get_session)):
    statement = select(Listing)
    results = db.exec(statement)
    return results.all()

# a lighter ver of upload that just returns ai data without savings to DB 
@app.post("/analyze-product")
async def analyze_product(file: UploadFile = File(...)):

    if  file.content_type is None or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail ="FIle must be an image")
    
    image_bytes = await file.read()

    listing = await generate_listing_from_image(image_bytes)

    if not listing:
        raise HTTPException(status_code=500, detail="Failed to analyze image")
    query = f"{listing.title} used market price"
    market_data = await search_market_prices(query)

    price_decision = await refine_price_with_market_context(listing, market_data)
    if price_decision is not None:
        listing.suggested_price = int(price_decision.final_suggested_price)
    
    return{
      "listing": listing,
      "market_analysis":{
          "suggested_retail":listing.suggested_price,
          "comparable_listings": market_data,
          "confidence_score": (price_decision.confidence if price_decision else ("High" if len(market_data) > 2 else "Low")),
          "reasoning": (price_decision.reasoning if price_decision else None),
      },
      "status":"success"
    }