"""가상 결제 서비스의 API. 실제 서비스라면 인터넷 너머의 주소로 부른다.

    GET https://api.pay.example/v1/payments/<payment_key>
    응답: {"status": "paid", "amount": 12000, "order_no": "A1001"}
"""
from .models import FakePayment


class ApiError(Exception):
    pass


def check_secret_key(secret_key):
    # 테스트용 비밀 키만 받는다. 실제 서비스는 발급한 키인지 확인한다
    if not secret_key or not secret_key.startswith("test_sk_"):
        raise ApiError("invalid api key")


def check_client_key(client_key):
    if not client_key or not client_key.startswith("test_ck_"):
        raise ApiError("invalid client key")


def get_payment(secret_key, payment_key):
    check_secret_key(secret_key)
    try:
        p = FakePayment.objects.get(payment_key=payment_key)
    except FakePayment.DoesNotExist:
        raise ApiError("payment not found")
    return {"payment_key": p.payment_key, "order_no": p.order_no, "amount": p.amount, "status": p.status}
