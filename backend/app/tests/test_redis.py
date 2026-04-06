import redis

from app.core.config import settings

def test_connection():
  try:

    r = redis.from_url(settings.REDIS_URL)

    if r.ping():
      print("Redit is connected via config")
  
  except Exception as e: 
    print(f"Connection failed: {e}")
    print("Tip:Check if docker is running")


if __name__ == "__main__":
  test_connection()
