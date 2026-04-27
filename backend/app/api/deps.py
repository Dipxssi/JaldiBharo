## api security layer . handles authhentication and rate-limiting 

from fastapi import Depends , HTTPException , status
from fastapi.security import HTTPAuthorizationCredentials , HTTPBearer
from app.core.security import decode_access_token
import redis
import datetime
from app.core.config import settings

#connects to redis for keeping track of usage limits 
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

security_scheme = HTTPBearer()


# function for protected routes
async def get_current_user(token: HTTPAuthorizationCredentials = Depends(security_scheme)):

  payload = decode_access_token(token.credentials)

  if not payload:
    raise HTTPException(status_code=401 , detail="Invalid or expired ticket")
  
  user_id = payload.get("sub")
  user_tier = payload.get("tier", "guest")

  #Rate limit
  if user_tier =="guest":
    today = datetime.date.today().isoformat()

    redis_key = f"usage:{user_id}:{today}"

    count = int(redis_client.incr(redis_key)) # type: ignore

    if count ==1:
      redis_client.expire(redis_key , 86400)

    if count > 2:
      raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail = "daily limit reache! Upgrade to Pro for unlimited AI search"
      )
  return payload 

#extract token
#decode jwt
#validate user
#check user tier
#if guest:
#count request in redis
#allow max 2/day 
#return user payload 