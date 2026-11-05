"""결제 확인. 결제창에서 돌아올 때와 웹훅을 받을 때 모두 이 함수를 거친다."""
import logging

from django.db import transaction
from django.utils import timezone

from .models import Order
from .pg import PaymentError, get_client
from .tasks import send_receipt

logger = logging.getLogger("payments")


class PaymentMismatch(Exception):
    """결제 대행 서비스가 알려 준 결과가 주문과 맞지 않는다."""


def confirm_payment(order, payment_key):
    """결제 대행 서비스에 직접 물어 결과를 확인하고, 맞으면 주문을 결제 완료로 바꾼다.

    브라우저가 보낸 금액과 상태는 믿지 않는다. 같은 결제가 두 번 확인되어도
    (결제창 복귀와 웹훅이 둘 다 오는 경우) 주문은 한 번만 결제 완료가 된다.
    돌려주는 값: 이번 호출에서 결제 완료로 바뀌었으면 True, 이미 완료였으면 False.
    """
    try:
        result = get_client().verify(payment_key)
    except PaymentError as e:
        logger.error("결제 확인 실패 주문=%s 원인=%s", order.order_no, e)
        raise

    # 브라우저가 보낸 금액은 믿지 않는다. 결제 서비스에 직접 물어 받은 금액을 주문 금액과 비교한다
    if result["status"] != "paid" or result["order_no"] != order.order_no or result["amount"] != order.amount:
        logger.warning("결제 확인 실패 주문=%s 원인=결과 불일치 받은값=%s", order.order_no, result)
        raise PaymentMismatch("결제 결과가 주문과 맞지 않습니다.")

    with transaction.atomic():
        locked = Order.objects.select_for_update().get(pk=order.pk)
        if locked.is_paid:
            return False
        locked.status = Order.Status.PAID
        locked.payment_key = payment_key
        locked.paid_at = timezone.now()
        locked.save(update_fields=["status", "payment_key", "paid_at"])
        logger.info("결제 확인 성공 주문=%s 금액=%s", order.order_no, order.amount)
        # 결제 완료가 데이터베이스에 확정된 뒤에 구매 확인 메일 작업을 맡긴다
        transaction.on_commit(lambda: send_receipt.enqueue(order.pk))
    return True
