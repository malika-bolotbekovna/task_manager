from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('profile/edit/', views.profile_edit, name='profile-edit'),
]
