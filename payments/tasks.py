"""화면과 따로 도는 작업."""
import logging

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.tasks import task
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

logger = logging.getLogger("payments")


@task
def send_receipt(order_id):
    """구매 확인 메일을 보낸다. 같은 주문에 두 번 보내지 않는다."""
    from .models import Order

    with transaction.atomic():
        order = Order.objects.select_for_update().select_related("buyer", "content").get(pk=order_id)
        if order.receipt_sent_at or not order.is_paid or not order.buyer.email:
            return
        context = {"order": order, "library_url": settings.SITE_URL.rstrip("/") + reverse("shop:library"),
                   "site_name": settings.SITE_NAME}
        send_mail(
            subject=f"[{settings.SITE_NAME}] {order.content.title} 구매가 완료되었습니다",
            message=render_to_string("email/receipt.txt", context),
            html_message=render_to_string("email/receipt.html", context),
            from_email=None,  # DEFAULT_FROM_EMAIL을 쓴다
            recipient_list=[order.buyer.email],
        )
        order.receipt_sent_at = timezone.now()
        order.save(update_fields=["receipt_sent_at"])
    logger.info("구매 확인 메일 발송 주문=%s", order.order_no)
