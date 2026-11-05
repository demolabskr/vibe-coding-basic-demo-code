from django.urls import path

from . import views

app_name = "shop"

urlpatterns = [
    path("contents/", views.content_list, name="content_list"),
    path("contents/<slug:slug>/", views.content_detail, name="content_detail"),
]
