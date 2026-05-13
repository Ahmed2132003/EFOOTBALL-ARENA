from django.urls import path
from .views import ProfileView, PublicProfileView, PasswordChangeView

app_name = "users_profile"

urlpatterns = [
    path("profile/",                  ProfileView.as_view(),        name="profile"),
    path("profile/<str:username>/",   PublicProfileView.as_view(),  name="public-profile"),
    path("change-password/",          PasswordChangeView.as_view(), name="change-password"),
]