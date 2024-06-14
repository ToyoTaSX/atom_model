from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    path('get_photo_class/', views.get_photo_class),
]
