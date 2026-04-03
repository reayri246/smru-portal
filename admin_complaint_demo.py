#!/usr/bin/env python
"""
Admin Complaint Management Demo Script
This script demonstrates how administrators can access and manage student complaints.
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from smru.models import Complaint
from django.contrib.auth.models import User

def demo_complaint_management():
    """Demonstrate complaint management functionality"""

    print("🎓 SMRU College Portal - Admin Complaint Management Demo")
    print("=" * 60)

    # Show total complaints
    total_complaints = Complaint.objects.count()
    print(f"\n📊 Total Complaints in System: {total_complaints}")

    if total_complaints > 0:
        # Show complaint statistics
        status_counts = {}
        for complaint in Complaint.objects.all():
            status = complaint.get_status_display()
            status_counts[status] = status_counts.get(status, 0) + 1

        print("\n📈 Complaint Status Summary:")
        for status, count in status_counts.items():
            print(f"   • {status}: {count}")

        # Show recent complaints
        print("\n📝 Recent Complaints:")
        recent_complaints = Complaint.objects.order_by('-submitted_at')[:5]
        for complaint in recent_complaints:
            print(f"   ID {complaint.id}: {complaint.name} ({complaint.roll})")
            print(f"      Category: {complaint.get_category_display()}")
            print(f"      Status: {complaint.get_status_display()}")
            print(f"      Submitted: {complaint.submitted_at.strftime('%Y-%m-%d %H:%M')}")
            print(f"      Preview: {complaint.complaint_text[:100]}{'...' if len(complaint.complaint_text) > 100 else ''}")
            print()

    print("🔧 Admin Access Instructions:")
    print("1. Open your browser and go to: http://localhost:8000/admin/")
    print("2. Login with admin credentials")
    print("3. Click on 'Complaints' in the left sidebar")
    print("4. View, filter, and respond to student complaints")
    print("5. Use bulk actions to update multiple complaints at once")

    print("\n✨ Admin Features:")
    print("• View all complaints with status indicators")
    print("• Filter by status, category, and date")
    print("• Search by student name, roll, email, or complaint text")
    print("• Read full complaint details and attached files")
    print("• Write responses and update complaint status")
    print("• Bulk actions: Mark as Resolved, Closed, or In Progress")

    print("\n🔐 Permission Management:")
    print("• Go to 'Student Profiles' in admin")
    print("• Edit user profiles to grant 'Can view all complaints' permission")
    print("• Authorized users see 'All Complaints' in their navigation menu")

if __name__ == "__main__":
    demo_complaint_management()