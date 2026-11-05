"""결제 결과를 서버가 다시 확인하는지, 웹훅이 서명을 확인하는지 보는 테스트."""
import json

from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from fakepg.models import FakePayment
from fakepg.webhook import sign
from payments.models import Order
from shop.models import Content

SECRET = "whsec_테스트"


@override_settings(FAKEPG_SEND_WEBHOOK=False, PAYMENT_SECRET_KEY="test_sk_테스트",
                   PAYMENT_PUBLIC_KEY="test_ck_테스트", PAYMENT_WEBHOOK_SECRET=SECRET)
class PaymentTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("buyer", password="예시값1234")
        self.content = Content.objects.create(kind="template", title="가계부 서식", slug="budget",
                                              summary="-", description="-", price=12000, is_published=True)
        self.client.login(username="buyer", password="예시값1234")

    def pay(self, amount):
        """결제창에서 결제를 마친 것처럼 결제 대행 서비스 쪽 기록을 만든다."""
        order = Order.objects.create(buyer=self.user, content=self.content, amount=self.content.price)
        FakePayment.objects.create(payment_key=f"pay_{order.id}", order_no=order.order_no,
                                   order_name="-", amount=amount)
        return order

    def test_order_amount_comes_from_database(self):
        self.client.post("/orders/", {"content_id": self.content.id, "amount": 100})
        self.assertEqual(Order.objects.get().amount, 12000)

    def test_sale_price_is_charged(self):
        self.content.sale_price = 9000
        self.content.save()
        self.client.post("/orders/", {"content_id": self.content.id})
        self.assertEqual(Order.objects.get().amount, 9000)

    def test_success_marks_order_paid(self):
        order = self.pay(12000)
        self.client.get(f"/payments/success/?paymentKey=pay_{order.id}&orderId={order.order_no}&amount=12000")
        order.refresh_from_db()
        self.assertTrue(order.is_paid)

    def test_paid_amount_must_match_order(self):
        order = self.pay(1000)  # 결제창에 넘기는 금액을 바꿔 1,000원만 낸 경우
        response = self.client.get(f"/payments/success/?paymentKey=pay_{order.id}&orderId={order.order_no}&amount=12000")
        order.refresh_from_db()
        self.assertEqual(response.status_code, 400)
        self.assertFalse(order.is_paid)

    def test_amount_in_address_is_not_trusted(self):
        order = self.pay(12000)
        response = self.client.get(f"/payments/success/?paymentKey=pay_{order.id}&orderId={order.order_no}&amount=1000")
        self.assertEqual(response.status_code, 400)

    def webhook(self, body, signature):
        return self.client.post("/payments/webhook/", body, content_type="application/json",
                                headers={"X-Pay-Signature": signature})

    def test_webhook_without_valid_signature_is_refused(self):
        order = self.pay(12000)
        body = json.dumps({"type": "payment.paid", "order_no": order.order_no, "payment_key": f"pay_{order.id}"})
        self.assertEqual(self.webhook(body, "wrong").status_code, 400)
        order.refresh_from_db()
        self.assertFalse(order.is_paid)

    def test_same_webhook_twice_is_processed_once(self):
        order = self.pay(12000)
        body = json.dumps({"type": "payment.paid", "order_no": order.order_no, "payment_key": f"pay_{order.id}"}).encode()
        self.assertEqual(self.webhook(body, sign(body, SECRET)).status_code, 200)
        first_paid_at = Order.objects.get(pk=order.pk).paid_at
        self.assertEqual(self.webhook(body, sign(body, SECRET)).status_code, 200)
        self.assertEqual(Order.objects.get(pk=order.pk).paid_at, first_paid_at)

    @override_settings(PAYMENT_SECRET_KEY="sk_live_잘못된키")
    def test_wrong_secret_key_fails(self):
        order = self.pay(12000)
        response = self.client.get(f"/payments/success/?paymentKey=pay_{order.id}&orderId={order.order_no}&amount=12000")
        self.assertEqual(response.status_code, 400)


@override_settings(FAKEPG_SEND_WEBHOOK=False, PAYMENT_SECRET_KEY="test_sk_테스트", PAYMENT_WEBHOOK_SECRET=SECRET)
class ReceiptMailTests(TestCase):
    def test_receipt_is_sent_once(self):
        from django.core import mail
        user = User.objects.create_user("buyer", email="buyer@example.com", password="예시값1234")
        content = Content.objects.create(kind="ebook", title="예시 전자책", slug="e", summary="-",
                                         description="-", price=9000, is_published=True)
        order = Order.objects.create(buyer=user, content=content, amount=9000)
        FakePayment.objects.create(payment_key="pay_x", order_no=order.order_no, order_name="-", amount=9000)
        self.client.login(username="buyer", password="예시값1234")
        url = f"/payments/success/?paymentKey=pay_x&orderId={order.order_no}&amount=9000"
        with self.captureOnCommitCallbacks(execute=True):
            self.client.get(url)
        with self.captureOnCommitCallbacks(execute=True):  # 웹훅이 한 번 더 와도
            body = json.dumps({"type": "payment.paid", "order_no": order.order_no, "payment_key": "pay_x"}).encode()
            self.client.post("/payments/webhook/", body, content_type="application/json",
                             headers={"X-Pay-Signature": sign(body, SECRET)})
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("예시 전자책", mail.outbox[0].subject)
