# scripts/test_auth_utils.py

import os
from dotenv import load_dotenv

# Important: This script assumes it's run from the project root.
# If you run it from the scripts/ directory, the imports might fail.
# To run from root: python scripts/test_auth_utils.py
from interview_system.auth.password_utils import hash_password, verify_password
from interview_system.auth.jwt_utils import create_access_token, create_refresh_token

def main():
    """
    Runs a test of the password hashing and JWT creation utilities.
    """
    # Load the JWT_SECRET_KEY from your .env file
    load_dotenv()
    if not os.getenv("JWT_SECRET_KEY"):
        print("Error: JWT_SECRET_KEY not found in .env file.")
        return

    print("--- 🔑 Testing Authentication Utilities ---")

    # --- 1. Test Password Hashing ---
    print("\n--- Testing password_utils.py ---")
    password = "my_super_secret_password123"
    hashed = hash_password(password)

    print(f"Original Password: {password}")
    print(f"Hashed Password:   {hashed}")

    # Test successful verification
    is_match = verify_password(password, hashed)
    print(f"Verification (Correct Password): {'✅ Success' if is_match else '❌ Failure'}")

    # Test failed verification
    is_match_fail = verify_password("my_super_secret_password123", hashed)
    print(f"Verification (Wrong Password):   {'❌ Failure' if not is_match_fail else '✅ Success'}")

    # --- 2. Test JWT Creawrong_passwordtion ---
    print("\n--- Testing jwt_utils.py ---")
    user_data = {"user_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef"}
    
    access_token = create_access_token(data=user_data)
    refresh_token = create_refresh_token(data=user_data)

    print(f"\nUser Data: {user_data}")
    print(f"\nGenerated Access Token (expires in 15 mins):\n{access_token}")
    print(f"\nGenerated Refresh Token (expires in 7 days):\n{refresh_token}")

    print("\n--- ✅ All tests completed. ---")

if __name__ == "__main__":
    main()