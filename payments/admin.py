import csv

from django.contrib import admin
from django.http import HttpResponse
from django.utils import timezone

from .models import Order


@admin.action(description="선택한 주문을 CSV로 내려받기")
def export_csv(modeladmin, request, queryset):
    """판매 기록을 CSV로 내려받는다. 엑셀에서 한글이 깨지지 않게 BOM을 붙인 UTF-8로 쓴다."""
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="orders-{timezone.localdate():%Y%m%d}.csv"'
    response.write("﻿")
    writer = csv.writer(response)
    writer.writerow(["주문 번호", "구매자", "콘텐츠", "금액", "상태", "결제 시각"])
    for o in queryset.select_related("buyer", "content"):
        paid = timezone.localtime(o.paid_at).isoformat(timespec="seconds") if o.paid_at else ""
        writer.writerow([o.order_no, o.buyer.username, o.content.title, o.amount, o.get_status_display(), paid])
    return response


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["order_no", "buyer", "content", "amount", "status", "paid_at"]
    list_filter = ["status", "content__kind"]
    search_fields = ["order_no", "buyer__username", "buyer__email", "content__title"]
    readonly_fields = ["order_no", "payment_key", "created_at", "paid_at", "receipt_sent_at"]
    date_hierarchy = "created_at"
    actions = [export_csv]
