"""결제 대행 서비스와 이야기하는 창구.

우리 코드는 이 파일의 PaymentClient만 부른다. 실제 결제 대행 서비스로 바꿀 때는
이 파일만 그 서비스의 공식 문서에 맞춰 고친다.
"""
from django.conf import settings

from fakepg import api as fake_api


class PaymentError(Exception):
    """결제 대행 서비스가 거절하거나 오류를 낸 경우."""


class PaymentTimeout(PaymentError):
    """결제 대행 서비스가 제때 답하지 않은 경우."""


class PaymentClient:
    def __init__(self, secret_key):
        self.secret_key = secret_key

    def verify(self, payment_key):
        """결제 키로 결제 대행 서비스에 결제 결과를 직접 묻는다.

        실제 서비스라면 HTTPS로 GET /v1/payments/<payment_key> 를 부르고
        비밀 키로 인증한다. 여기서는 가상 결제 서비스의 함수를 부른다.
        """
        try:
            return fake_api.get_payment(self.secret_key, payment_key)
        except fake_api.ApiError as e:
            raise PaymentError(str(e)) from e


def get_client():
    return PaymentClient(settings.PAYMENT_SECRET_KEY)
