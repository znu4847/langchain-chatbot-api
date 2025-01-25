from django.urls import path
from . import views

# comment
urlpatterns = [
    path("", views.ROOT.as_view()),
]
