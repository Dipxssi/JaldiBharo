# connects to gemini ai and tavily search 

from tavily import TavilyClient
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from .schema import ListingResponse, PriceRefinementResponse

load_dotenv()


GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# sends img data to gemeini 
async def generate_listing_from_image(image_bytes: bytes) -> ListingResponse | None:
    prompt = """
        You are an expert marketplace seller. Analyze the uploaded image(s) carefully.
        Return a structured JSON listing including:
        - A catchy title
        - A detailed description (mention any visible flaws or wear and tear)
        - The most appropriate category
        - Condition (New, Like New, Good, Fair, Poor)
        - A suggested price in USD (as an integer)
        - 5 relevant search tags
    """

    
    response = await client.aio.models.generate_content(
        model=GEMINI_MODEL,
        contents=[
            prompt,
            types.Part.from_bytes(data=image_bytes, mime_type='image/*')
        ],
        config=types.GenerateContentConfig(
            response_mime_type='application/json',
            response_schema=ListingResponse,
        ),
    )

    parsed = response.parsed
    if parsed is None:
        return None
    return ListingResponse.model_validate(parsed)


# searches the web for similar item proices using tavily
async def search_market_prices(query: str):
    try:
        
        search_result = tavily_client.search(
            query=query,
            search_depth="basic", 
            max_results=5
        )

        return [
            {"url": r["url"], "content": r["content"]} 
            for r in search_result.get("results", [])
        ]
    except Exception as e:
        print(f"Tavily Search Error: {e}")
        return []


#shows gemini the search res and the img data 
async def refine_price_with_market_context(
    listing: ListingResponse,
    market_references: list[dict],
) -> PriceRefinementResponse | None:
    
    if not market_references:
        return PriceRefinementResponse(
            final_suggested_price=int(listing.suggested_price),
            confidence="Low",
            reasoning="No market references available; using image-based suggested price.",
        )

    refs_text = "\n".join(
        f"- {r.get('url', '')}\n  {str(r.get('content', '')).strip()[:800]}"
        for r in market_references
    )

    prompt = f"""
You are pricing a USED item for a marketplace listing.

You will be given:
1) The current listing details (from image analysis).
2) Web search snippets of comparable listings/prices.

Task:
- Choose a single FINAL suggested price in USD as an integer.
- Use the web snippets to ground the price. If snippets are noisy or irrelevant, say so and lower confidence.
- Keep the price reasonable for a USED item (not brand-new MSRP unless clearly appropriate).

Return ONLY JSON matching the schema.

Listing:
title: {listing.title}
category: {listing.category}
condition: {listing.condition}
image_suggested_price_usd: {listing.suggested_price}
tags: {", ".join(listing.tags or [])}

Web market references (snippets):
{refs_text}
""".strip()

    try:
        response = await client.aio.models.generate_content(
            model=GEMINI_MODEL,
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=PriceRefinementResponse,
            ),
        )
        parsed = response.parsed
        if parsed is None:
            return None
        return PriceRefinementResponse.model_validate(parsed)
    except Exception as e:
        print(f"Price refinement error: {e}")
        return None
    
# a func that runs all the above 3 func
async def get_complete_listing_analysis(image_bytes: bytes):
    listing = await generate_listing_from_image(image_bytes)

    if not listing:
        return None
    

    search_query = f"{listing.title} current market price used"
    market_context = await search_market_prices(search_query)

    price_decision = await refine_price_with_market_context(listing, market_context)
    if price_decision is not None:
        listing.suggested_price = int(price_decision.final_suggested_price)

    return {
        "listing": listing,
        "market_references": market_context,
        "price_decision": price_decision,
    }


async def get_embedding(text: str) -> list[float]:
    response = await client.aio.models.embed_content(
        model="text-embedding-004",
        contents=text,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT",
        ),
    )
    if not response.embeddings or not response.embeddings[0].values:
        raise RuntimeError("Embedding API returned no vector")
    return list(response.embeddings[0].values)

