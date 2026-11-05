from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    path("orders/", views.create_order, name="create_order"),
    path("orders/<str:order_no>/", views.checkout, name="checkout"),
    path("payments/success/", views.success, name="success"),
    path("payments/done/<str:order_no>/", views.success_page, name="success_page"),
    path("payments/fail/", views.fail, name="fail"),
    path("payments/webhook/", views.webhook, name="webhook"),
]
