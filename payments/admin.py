from django.contrib import admin

from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["order_no", "buyer", "content", "amount", "status", "paid_at"]
    list_filter = ["status", "content__kind"]
    search_fields = ["order_no", "buyer__username", "buyer__email", "content__title"]
    readonly_fields = ["order_no", "payment_key", "created_at", "paid_at", "receipt_sent_at"]
    date_hierarchy = "created_at"
