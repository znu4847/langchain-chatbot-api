from django.urls import path
from . import views

# comment
urlpatterns = [
    path("", views.ROOT.as_view()),
    path("auth", views.Auth.as_view()),
    path("me", views.Me.as_view()),
    path("password", views.Password.as_view()),
    path("login", views.Login.as_view()),
    path("logout", views.Logout.as_view()),
    path("<int:pk>", views.PK.as_view()),
    path("llm-key/<int:pk>", views.LLMKey.as_view()),
    path("stats/<int:pk>", views.Stats.as_view()),
]
