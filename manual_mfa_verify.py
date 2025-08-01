import json
import time

import pyotp
import requests

# Generate a TOTP code
mfa_secret = "ABCDEFGHIJKLMNOP"
totp = pyotp.TOTP(mfa_secret)
mfa_code = totp.now()
print(f"Generated TOTP code: {mfa_code}")

# Create a manual session ID
user_id = 4  # From our database check
session_id = f"{user_id}_{int(time.time())}"
print(f"Manual session ID: {session_id}")

# Call verify endpoint
verify_url = "http://localhost:9999/api/auth/verify-mfa"
verify_data = {"session_id": session_id, "code": mfa_code}

print(f"Sending to {verify_url}: {verify_data}")
response = requests.post(verify_url, json=verify_data)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")

# If successful, test protected endpoint
if response.status_code == 200:
    json_data = response.json()
    token = json_data.get("access_token")
    if token:
        print("\nTesting protected endpoint...")
        headers = {"Authorization": f"Bearer {token}"}
        me_response = requests.get(
            "http://localhost:9999/api/users/me", headers=headers
        )
        print(f"Status: {me_response.status_code}")
        print(f"Response: {me_response.text}")
    else:
        print("No access token in response")
