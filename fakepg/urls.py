from django.urls import path

from . import views

app_name = "fakepg"

urlpatterns = [
    path("checkout/", views.checkout, name="checkout"),
    path("v1/payments/<str:payment_key>", views.payment_api, name="payment_api"),
]
