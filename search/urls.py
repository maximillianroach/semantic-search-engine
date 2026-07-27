from django.urls import path
from . import views

urlpatterns = [
    path("page", views.page, name="page"),
    path("search", views.search, name="search"),
    path("styles", views.styles, name="styles"),
    path("genres", views.genres, name="genres"),
    path("artists", views.artists, name="artists")
]