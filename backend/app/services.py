import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from .schema import ListingResponse

load_dotenv()


GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

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
            types.Part.from_bytes(data=image_bytes, mime_type='image/png')
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