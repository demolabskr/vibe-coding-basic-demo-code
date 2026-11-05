"""전날 판매 건수와 금액을 운영자에게 메일로 보낸다.

    uv run python manage.py sales_report

매일 아침 한 번 돌도록 서버의 예약 작업(cron 등)에 걸어 둔다.
"""
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.db.models import Count, Sum
from django.utils import timezone

from payments.models import Order


class Command(BaseCommand):
    help = "전날(한국 시간) 판매 건수와 금액을 운영자에게 메일로 보낸다."

    def handle(self, *args, **options):
        yesterday = timezone.localdate() - timedelta(days=1)
        sales = Order.objects.filter(status=Order.Status.PAID, paid_at__date=yesterday)
        total = sales.aggregate(count=Count("id"), amount=Sum("amount"))
        message = f"{yesterday} 판매 {total['count']}건, {total['amount'] or 0:,}원"
        send_mail(f"[{settings.SITE_NAME}] 어제 판매", message, None, [settings.OWNER_EMAIL])
        self.stdout.write(message)
