from django.db import models


class FakePayment(models.Model):
    """결제 대행 서비스 쪽에 남는 결제 기록. 우리 사이트의 주문(Order)과는 다른 표다."""

    payment_key = models.CharField(max_length=64, unique=True)
    order_no = models.CharField(max_length=20)
    order_name = models.CharField(max_length=200)
    amount = models.PositiveIntegerField()
    status = models.CharField(max_length=20, default="paid")
    approved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "가상 결제"
        verbose_name_plural = "가상 결제"
