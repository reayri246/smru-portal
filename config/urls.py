"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
https://docs.djangoproject.com/en/3.2/topics/http/urls/
"""
# project_name/urls.py
from django.contrib import admin
from django.urls import path, include  # include needed for app urls
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from smru import views as smru_views

urlpatterns = [
    path('favicon.ico', RedirectView.as_view(url=settings.STATIC_URL + 'smru/favicon.svg', permanent=True)),
    path('admin/', admin.site.urls),
    path('', include('smru.urls')),  # Make sure your app name is 'smru'
]

# Error handlers
handler404 = smru_views.error_404
handler500 = smru_views.error_500

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)