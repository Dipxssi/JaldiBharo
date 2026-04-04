import cloudinary
import cloudinary.uploader
import io
from PIL import Image
import os
from dotenv import load_dotenv
from urllib.parse import unquote, urlparse

load_dotenv()


def _configure_cloudinary() -> None:
    # Render has no .env; use dashboard env vars. CLOUDINARY_URL (from Cloudinary) overrides split vars.
    url = os.getenv("CLOUDINARY_URL")
    if url and url.strip():
        parsed = urlparse(url.strip())
        if parsed.scheme != "cloudinary":
            raise ValueError("CLOUDINARY_URL must start with cloudinary://")
        cloudinary.config(
            cloud_name=parsed.hostname,
            api_key=unquote(parsed.username) if parsed.username else None,
            api_secret=unquote(parsed.password) if parsed.password else None,
        )
        return
    cloudinary.config(
        cloud_name=(os.getenv("CLOUDINARY_CLOUD_NAME") or "").strip() or None,
        api_key=(os.getenv("CLOUDINARY_API_KEY") or "").strip() or None,
        api_secret=(os.getenv("CLOUDINARY_API_SECRET") or "").strip() or None,
    )


_configure_cloudinary()


def upload_to_cloudinary(file_bytes: bytes) -> str:
    result = cloudinary.uploader.upload(io.BytesIO(file_bytes))
    return result["secure_url"]

def create_collage(image_bytes_list: list[bytes]) -> bytes:
  images = [Image.open(io.BytesIO(b)) for b in image_bytes_list]

  min_height = min(img.height for img in images)

  resized_images = []

  for img in images:
    aspect_ratio = img.width / img.height
    new_width = int(min_height * aspect_ratio)
    resized_images.append(img.resize((new_width , min_height)))

  total_width = sum(img.width for img in resized_images)
  collage = Image.new("RGB" , (total_width, min_height))

  x_offset = 0
  for img in resized_images:
    collage.paste(img, (x_offset, 0))
    x_offset += img.width

  img_byte_arr = io.BytesIO()
  collage.save(img_byte_arr , format='JPEG')
  return img_byte_arr.getvalue()



