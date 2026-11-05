"""예시 데이터를 넣는다: 운영자와 회원 계정, 예시 콘텐츠, buyer의 구매 기록 두 건.

    uv run python manage.py seed_demo

계정 비밀번호는 모두 예시값(demo-pass-1234)이다. 개발용 데이터베이스에서만 쓴다.
"""
import json
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.management.base import BaseCommand

from django.utils import timezone

from fakepg.models import FakePayment
from payments.models import Order
from shop.models import Content

SAMPLE = Path(settings.BASE_DIR) / "sample_data"
DEMO_PASSWORD = "demo-pass-1234"


class Command(BaseCommand):
    help = "예시 계정과 콘텐츠를 넣는다(이미 있으면 건너뛴다)."

    def handle(self, *args, **options):
        if not settings.DEBUG:
            self.stderr.write("DEBUG가 꺼져 있다. 예시 데이터는 개발 환경에서만 넣는다.")
            return
        User = get_user_model()
        if not User.objects.filter(username="minji").exists():
            User.objects.create_superuser("minji", "minji@example.com", DEMO_PASSWORD)
        for name in ["buyer", "member"]:
            if not User.objects.filter(username=name).exists():
                User.objects.create_user(name, f"{name}@example.com", DEMO_PASSWORD)

        items = json.loads((SAMPLE / "contents.json").read_text(encoding="utf-8"))
        for item in items:
            if Content.objects.filter(slug=item["slug"]).exists():
                continue
            content = Content(
                kind=item["kind"], title=item["title"], slug=item["slug"],
                summary=item["summary"], description=item["description"],
                price=item["price"], sale_price=item.get("sale_price"), is_published=item["is_published"],
            )
            with open(SAMPLE / "covers" / f"{item['slug']}.png", "rb") as cover:
                content.cover.save(f"{item['slug']}.png", File(cover), save=False)
            with open(SAMPLE / "files" / item["file"], "rb") as f:
                content.file.save(item["file"], File(f), save=False)
            content.save()
        buyer = User.objects.get(username="buyer")
        if not buyer.orders.exists():
            for slug in ["budget", "excel-functions"]:
                content = Content.objects.get(slug=slug)
                order = Order.objects.create(buyer=buyer, content=content, amount=content.price)
                payment = FakePayment.objects.create(payment_key=f"pay_demo{order.id:04d}", order_no=order.order_no,
                                                     order_name=content.title, amount=order.amount)
                order.status, order.payment_key, order.paid_at = Order.Status.PAID, payment.payment_key, timezone.now()
                order.save()
        self.stdout.write(self.style.SUCCESS(f"예시 데이터 준비 완료: 콘텐츠 {Content.objects.count()}개"))
