from django.urls import path
from . import views

# comment
urlpatterns = [
    path("", views.ROOT.as_view()),
    path("<int:pk>", views.ROOTDetail.as_view()),
    path("token/<int:pk>", views.ROOTToken.as_view()),
]
