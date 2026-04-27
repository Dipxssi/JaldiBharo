import time
from app.core.security import create_access_token , decode_access_token

def test_jwt_workflow():
  print("Starting JWT Test.......")

  user_identity = {"sub":"dipsha@2026", "tier": "pro"}

  token = create_access_token(data=user_identity)

  print("Token Generated Successfully!")

  print(f"The Encoded String {token}")

  decoded_data = decode_access_token(token)

  if decoded_data and decoded_data.get("sub") == "dipsha@2026":
    print(f"Token Verified User: {decoded_data.get('exp')}")
    print(f"User Tier: {decoded_data.get('tier')}")
    print(f"Expires At : {decoded_data.get('exp')}")
  else:
    print("Verification Failed")

  print("Test Completed")

if __name__ == "__main__":
  test_jwt_workflow()