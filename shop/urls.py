from django.urls import path

from . import views

app_name = "shop"

urlpatterns = [
    path("contents/", views.content_list, name="content_list"),
    path("contents/<slug:slug>/", views.content_detail, name="content_detail"),
    path("library/", views.library, name="library"),
    path("library/<int:order_id>/watch/", views.watch, name="watch"),
    path("download/<int:order_id>/", views.download, name="download"),
    path("download/file/<str:token>/", views.download_file, name="download_file"),
]
