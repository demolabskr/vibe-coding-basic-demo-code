import hmac
import json
import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from fakepg.webhook import sign
from shop.models import Content

from .models import Order
from .pg import PaymentError, PaymentTimeout
from .services import PaymentMismatch, confirm_payment

logger = logging.getLogger("payments")


@login_required
@require_POST
def create_order(request):
    """구매 버튼이 보내는 요청(POST /orders/). 금액은 화면이 아니라 데이터베이스의 가격으로 정한다."""
    content = get_object_or_404(Content, id=request.POST.get("content_id"), is_published=True)
    if Order.objects.filter(buyer=request.user, content=content, status=Order.Status.PAID).exists():
        messages.info(request, "이미 구매한 콘텐츠입니다.")
        return redirect(content.get_absolute_url())
    order = Order.objects.create(buyer=request.user, content=content, amount=content.price)
    return redirect("payments:checkout", order_no=order.order_no)


@login_required
def checkout(request, order_no):
    """주문 확인 화면. [결제하기]를 누르면 결제 대행 서비스의 결제창으로 넘어간다."""
    order = get_object_or_404(Order, order_no=order_no, buyer=request.user)
    if order.is_paid:
        return redirect("payments:success_page", order_no=order.order_no)
    site = settings.SITE_URL.rstrip("/")
    return render(request, "payments/checkout.html", {
        "order": order,
        "checkout_url": settings.PAYMENT_CHECKOUT_URL,
        "client_key": settings.PAYMENT_PUBLIC_KEY,
        "success_url": site + reverse("payments:success"),
        "fail_url": site + reverse("payments:fail"),
    })


@login_required
def success(request):
    """결제창에서 돌아오는 주소. 주소에 붙은 값은 단서일 뿐, 결과는 서버가 다시 확인한다."""
    order = get_object_or_404(Order, order_no=request.GET.get("orderId"), buyer=request.user)
    if request.GET.get("amount") != str(order.amount):
        logger.warning("결제 확인 실패 주문=%s 원인=주소의 금액 불일치", order.order_no)
        return render(request, "payments/fail.html", {"order": order, "reason": "결제 금액이 주문과 다릅니다."}, status=400)
    try:
        confirm_payment(order, request.GET.get("paymentKey", ""))
    except PaymentTimeout:
        messages.warning(request, "결제 상태를 확인하는 중입니다. 잠시 뒤 내 자료실에서 확인해 주세요.")
        return redirect("shop:content_list")
    except (PaymentError, PaymentMismatch):
        return render(request, "payments/fail.html", {"order": order, "reason": "결제를 확인하지 못했습니다."}, status=400)
    return redirect("payments:success_page", order_no=order.order_no)


@login_required
def success_page(request, order_no):
    order = get_object_or_404(Order, order_no=order_no, buyer=request.user, status=Order.Status.PAID)
    return render(request, "payments/success.html", {"order": order})


@login_required
def fail(request):
    order = Order.objects.filter(order_no=request.GET.get("orderId"), buyer=request.user).first()
    reason = "결제를 취소했습니다." if request.GET.get("code") == "USER_CANCEL" else "결제가 완료되지 않았습니다."
    return render(request, "payments/fail.html", {"order": order, "reason": reason})


@csrf_exempt  # 결제 대행 서비스가 보내는 요청이라 CSRF 토큰 대신 서명으로 확인한다
@require_POST
def webhook(request):
    """결제 대행 서비스가 결제 완료를 알려 주는 주소(웹훅)."""
    expected = sign(request.body, settings.PAYMENT_WEBHOOK_SECRET)
    if not hmac.compare_digest(request.headers.get("X-Pay-Signature", ""), expected):
        logger.warning("웹훅 거절 원인=서명 불일치")
        return HttpResponseBadRequest("invalid signature")
    event = json.loads(request.body)
    if event.get("type") != "payment.paid":
        return HttpResponse("ignored")
    order = Order.objects.filter(order_no=event.get("order_no")).first()
    if order is None:
        return HttpResponse("unknown order")
    try:
        # 알림 내용도 그대로 믿지 않고 결제 대행 서비스에 다시 묻는다
        confirm_payment(order, event.get("payment_key", ""))
    except (PaymentError, PaymentMismatch):
        return HttpResponseBadRequest("verify failed")
    return HttpResponse("ok")

