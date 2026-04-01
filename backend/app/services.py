import os
import google.generativeai as genai
from dotenv import load_dotenv
from .schema import ListingResponse

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_listing_from_image(image_data: list[bytes]):

  model = genai.GenerativeModel('gemini-1.5-flash')

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
  response = model.generate_content(
    [prompt , *image_data],
    generation_config={
      "response_mime_type": "application/json",
      "response_schema": ListingResponse
    }
  )

  return ListingResponse.model_validate_json(response.text)