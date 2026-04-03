import requests
import sys
from urllib.parse import urljoin

BASE_URL = "http://localhost:8000"

pages = [
    ("/", "Home Page"),
    ("/admin/", "Admin Panel"),
    ("/login/", "Login"),
    ("/signup/", "Signup"),
    ("/notifications/", "Notifications"),
    ("/events/", "Events"),
    ("/engineering/", "Engineering Notes"),
    ("/medical/", "Medical Notes"),
    ("/complaints/", "Submit Complaint"),
    ("/student-files/", "Student Files"),
    ("/profile/", "User Profile"),
    ("/my-complaints/", "My Complaints"),
]

print("=" * 70)
print("🧪 TESTING ALL PAGES")
print("=" * 70)

working_pages = []
error_pages = []

for endpoint, name in pages:
    url = urljoin(BASE_URL, endpoint)
    try:
        response = requests.get(url, timeout=5, allow_redirects=True)
        status = response.status_code
        
        if status == 500:
            print(f"❌ {name:25} - {url:40} [500 ERROR]")
            error_pages.append((name, url, status))
        elif status == 404:
            print(f"⚠️  {name:25} - {url:40} [404 NOT FOUND]")
        elif status == 200:
            print(f"✅ {name:25} - {url:40} [200 OK]")
            working_pages.append((name, url, status))
        elif status == 302:
            # Redirect, usually to login - still working
            print(f"✅ {name:25} - {url:40} [302 REDIRECT]")
            working_pages.append((name, url, status))
        else:
            print(f"⚠️  {name:25} - {url:40} [{status}]")
            
    except Exception as e:
        print(f"❌ {name:25} - {url:40} [ERROR: {str(e)[:30]}]")
        error_pages.append((name, url, str(e)))

print("\n" + "=" * 70)
print(f"📊 SUMMARY")
print("=" * 70)
print(f"✅ Working Pages: {len(working_pages)}")
print(f"❌ Error Pages: {len(error_pages)}")
print(f"⚠️  Other Status: {len(pages) - len(working_pages) - len(error_pages)}")

if error_pages:
    print("\n🔴 PAGES WITH ERRORS:")
    for name, url, status in error_pages:
        print(f"  • {name} - {status}")

print(f"\n✅ PAGES WORKING CORRECTLY:")
for name, url, status in working_pages:
    print(f"  • {name}")

print("\n" + "=" * 70)
