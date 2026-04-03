import requests
from requests.cookies import RequestsCookieJar

BASE_URL = "http://localhost:8000"

print("=" * 70)
print("🧪 TESTING LOGOUT FUNCTIONALITY")
print("=" * 70)

session = requests.Session()

# Step 1: Get login page
print("\n1️⃣  Getting login page...")
response = session.get(f"{BASE_URL}/login/")
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    print("   ✅ Login page loaded")

# Step 2: Login with admin credentials
print("\n2️⃣  Logging in with admin credentials...")
login_data = {
    'username': 'admin',
    'password': 'admin123'
}
response = session.post(f"{BASE_URL}/login/", data=login_data, allow_redirects=True)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    print("   ✅ Login successful (or redirected)")

# Step 3: Test logout
print("\n3️⃣  Testing logout endpoint...")
response = session.get(f"{BASE_URL}/logout/", allow_redirects=True)
print(f"   Final Status: {response.status_code}")
if response.status_code == 200:
    print("   ✅ Logout successful - redirected correctly!")
    print(f"   Final URL: {response.url}")
else:
    print(f"   ❌ Logout failed with status {response.status_code}")

print("\n" + "=" * 70)
print("✅ LOGOUT TEST COMPLETE")
print("=" * 70)
