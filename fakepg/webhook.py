"""결제가 끝나면 가맹점(우리 사이트)의 웹훅 주소로 알림을 보낸다."""
import hashlib
import hmac
import json
import logging
import threading
import time
import urllib.request

from django.conf import settings

logger = logging.getLogger("fakepg")


def sign(body: bytes, secret: str) -> str:
    return hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


def send_paid_event(payment):
    if not settings.FAKEPG_SEND_WEBHOOK:
        return
    body = json.dumps({"type": "payment.paid", "payment_key": payment.payment_key,
                       "order_no": payment.order_no}).encode()
    headers = {"Content-Type": "application/json",
               "X-Pay-Signature": sign(body, settings.PAYMENT_WEBHOOK_SECRET)}
    url = settings.SITE_URL.rstrip("/") + "/payments/webhook/"

    def deliver():
        time.sleep(1)  # 실제 서비스도 알림이 조금 늦게 온다
        try:
            urllib.request.urlopen(urllib.request.Request(url, data=body, headers=headers, method="POST"), timeout=5)
        except Exception as e:  # 받는 쪽이 꺼져 있어도 결제창은 멈추지 않는다
            logger.warning("웹훅 전달 실패 주소=%s 원인=%s", url, e)

    threading.Thread(target=deliver, daemon=True).start()
