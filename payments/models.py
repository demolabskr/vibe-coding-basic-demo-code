from django.conf import settings
from django.db import models

from shop.models import Content


class Order(models.Model):
    """구매 기록 하나. 누가(구매자) 무엇을(콘텐츠) 얼마에 샀는지 적는다."""

    class Status(models.TextChoices):
        PENDING = "pending", "결제 대기"
        PAID = "paid", "결제 완료"
        CANCELED = "canceled", "취소"

    order_no = models.CharField("주문 번호", max_length=20, unique=True, blank=True)
    # 회원이나 콘텐츠를 지워도 구매 기록은 남아야 하므로 지우기를 막는다(PROTECT)
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders", verbose_name="구매자")
    content = models.ForeignKey(Content, on_delete=models.PROTECT, related_name="orders", verbose_name="콘텐츠")
    amount = models.PositiveIntegerField("금액(원)")
    status = models.CharField("상태", max_length=20, choices=Status.choices, default=Status.PENDING)
    payment_key = models.CharField("결제 키", max_length=100, unique=True, null=True, blank=True)
    created_at = models.DateTimeField("주문 시각", auto_now_add=True)
    paid_at = models.DateTimeField("결제 시각", null=True, blank=True)
    receipt_sent_at = models.DateTimeField("구매 확인 메일 보낸 시각", null=True, blank=True)

    class Meta:
        verbose_name = "주문"
        verbose_name_plural = "주문"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.order_no} {self.content}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.order_no:  # 처음 저장할 때 번호를 붙인다. 예: A1001
            self.order_no = f"A{1000 + self.pk}"
            super().save(update_fields=["order_no"])

    @property
    def is_paid(self):
        return self.status == self.Status.PAID
