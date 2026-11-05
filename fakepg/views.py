"""가상 결제창. 카드 정보 칸은 없고, 승인과 취소 버튼만 있다."""
import base64
import secrets
from urllib.parse import urlencode

from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from . import api
from .models import FakePayment
from .webhook import send_paid_event


@csrf_exempt  # 다른 사이트(가맹점)에서 넘어오는 양식이라 이 서비스의 CSRF 토큰이 없다
@require_POST
def checkout(request):
    data = request.POST
    try:
        api.check_client_key(data.get("client_key"))
        amount = int(data["amount"])
        order_no, success_url, fail_url = data["order_no"], data["success_url"], data["fail_url"]
    except (api.ApiError, KeyError, ValueError) as e:
        return HttpResponseBadRequest(f"결제창을 열 수 없습니다: {e}")

    if data.get("action") == "approve":
        payment = FakePayment.objects.create(
            payment_key="pay_" + secrets.token_hex(8), order_no=order_no,
            order_name=data.get("order_name", ""), amount=amount,
        )
        send_paid_event(payment)
        query = urlencode({"paymentKey": payment.payment_key, "orderId": order_no, "amount": amount})
        return redirect(f"{success_url}?{query}")
    if data.get("action") == "cancel":
        return redirect(f"{fail_url}?{urlencode({'code': 'USER_CANCEL', 'orderId': order_no})}")
    return render(request, "fakepg/checkout.html", {"data": data, "amount": f"{amount:,}"})


@require_GET
def payment_api(request, payment_key):
    """API 모양을 보여 주는 주소. 비밀 키를 Basic 인증으로 받는다."""
    auth = request.headers.get("Authorization", "")
    secret = base64.b64decode(auth.removeprefix("Basic ")).decode().rstrip(":") if auth.startswith("Basic ") else ""
    try:
        return JsonResponse(api.get_payment(secret, payment_key))
    except api.ApiError as e:
        return JsonResponse({"error": str(e)}, status=401 if "key" in str(e) else 404)
