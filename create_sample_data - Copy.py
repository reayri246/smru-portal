import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from smru.models import College, Branch, Year, Subject, Notification, Event
from django.utils import timezone
from datetime import timedelta

# Create Colleges
try:
    college1 = College.objects.get_or_create(
        name="SMRU Medical Science",
        defaults={"description": "Premier Medical Science College with excellent faculty", "type": "medical"}
    )[0]

    college2 = College.objects.get_or_create(
        name="SMRU Engineering",
        defaults={"description": "Top-tier Engineering College with modern facilities", "type": "engineering"}
    )[0]

    # Create Branches
    branch1 = Branch.objects.get_or_create(
        college=college2,
        name="Computer Science",
        defaults={"code": "CSE"}
    )[0]

    branch2 = Branch.objects.get_or_create(
        college=college2,
        name="Mechanical Engineering",
        defaults={"code": "ME"}
    )[0]

    branch3 = Branch.objects.get_or_create(
        college=college1,
        name="MBBS",
        defaults={"code": "MBBS"}
    )[0]

    branch4 = Branch.objects.get_or_create(
        college=college1,
        name="BDS",
        defaults={"code": "BDS"}
    )[0]

    # Create Notifications
    notification = Notification.objects.get_or_create(
        title="Welcome to SMRU Portal",
        defaults={
            "description": "Welcome to the new SMRU College Portal! This is your gateway to academic resources, notifications, and college management.",
            "priority": "high",
            "is_active": True
        }
    )[0]

    notification2 = Notification.objects.get_or_create(
        title="Semester Registration Open",
        defaults={
            "description": "Online semester registration is now open. Register before the deadline.",
            "priority": "high",
            "is_active": True
        }
    )[0]

    # Create Events
    event1 = Event.objects.get_or_create(
        name="Annual Science Fair",
        defaults={
            "description": "Annual Science Fair showcasing student innovations and research projects from across the college.",
            "date": (timezone.now() + timedelta(days=15)).date(),
            "time": "10:00 AM",
            "location": "Main Auditorium",
            "status": "upcoming",
            "capacity": 500,
            "registered_count": 45
        }
    )[0]

    event2 = Event.objects.get_or_create(
        name="Sports Championship",
        defaults={
            "description": "Inter-college sports championship featuring various sports competitions including football, cricket, and volleyball.",
            "date": (timezone.now() + timedelta(days=30)).date(),
            "time": "2:00 PM",
            "location": "Sports Ground",
            "status": "upcoming",
            "capacity": 1000,
            "registered_count": 120
        }
    )[0]

    event3 = Event.objects.get_or_create(
        name="Technical Symposium",
        defaults={
            "description": "A day-long symposium featuring talks from industry experts and technical workshops.",
            "date": (timezone.now() + timedelta(days=45)).date(),
            "time": "9:00 AM",
            "location": "Tech Hall",
            "status": "upcoming",
            "capacity": 300,
            "registered_count": 87
        }
    )[0]

    print("✅ Sample Data Created Successfully!")
    print("\n📊 Data Summary:")
    print(f"  • Colleges: {College.objects.count()}")
    print(f"  • Notifications: {Notification.objects.count()}")
    print(f"  • Events: {Event.objects.count()}")
    print("\n🏫 Colleges:")
    for college in College.objects.all():
        print(f"  • {college.name}")
    print("\n📢 Notifications:")
    for notif in Notification.objects.all():
        print(f"  • {notif.title} ({notif.get_priority_display()})")
    print("\n🎉 Events:")
    for event in Event.objects.all():
        print(f"  • {event.name} - {event.date}")

except Exception as e:
    print(f"❌ Error: {e}")
