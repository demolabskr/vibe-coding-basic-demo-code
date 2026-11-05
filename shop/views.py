from django.contrib.auth.decorators import login_required
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner
from django.http import FileResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from payments.models import Order

from .models import Content


def content_list(request):
    """공개된 콘텐츠를 카드로 보여 준다. ?kind=ebook 처럼 종류로 거른다."""
    contents = Content.objects.filter(is_published=True)
    kind = request.GET.get("kind", "")
    if kind in Content.Kind.values:
        contents = contents.filter(kind=kind)
    return render(request, "shop/content_list.html", {
        "contents": contents,
        "kinds": Content.Kind.choices,
        "current_kind": kind,
    })



def content_detail(request, slug):
    """콘텐츠 하나의 상세 페이지. 숨긴 콘텐츠는 없는 것처럼 404를 낸다."""
    content = get_object_or_404(Content, slug=slug, is_published=True)
    owned = request.user.is_authenticated and content.orders.filter(
        buyer=request.user, status="paid"
    ).exists()
    return render(request, "shop/content_detail.html", {"content": content, "owned": owned})


# ---- 내 자료실과 내려받기 ----

DOWNLOAD_LINK_SECONDS = 300  # 내려받기 주소는 5분 뒤 만료된다
signer = TimestampSigner(salt="shop.download")


@login_required
def library(request):
    """내 자료실: 로그인한 사람이 결제를 마친 주문만 보여 준다."""
    orders = Order.objects.filter(buyer=request.user, status=Order.Status.PAID).select_related("content")
    return render(request, "shop/library.html", {"orders": orders})


@login_required
def download(request, order_id):
    """구매자만 받는다. 확인을 통과하면 몇 분 동안만 쓸 수 있는 서명 주소로 보낸다."""
    order = get_object_or_404(Order, id=order_id, buyer=request.user)
    if not order.is_paid:
        return HttpResponseForbidden("결제가 끝난 주문만 받을 수 있습니다.")
    token = signer.sign(str(order.id))
    return redirect("shop:download_file", token=token)


@login_required
def download_file(request, token):
    """서명 주소로 판매 파일을 내준다. 서명이 틀리거나 기한이 지나면 거절한다."""
    try:
        order_id = signer.unsign(token, max_age=DOWNLOAD_LINK_SECONDS)
    except SignatureExpired:
        return HttpResponseForbidden("내려받기 주소의 기한이 지났습니다. 내 자료실에서 다시 눌러 주세요.")
    except BadSignature:
        return HttpResponseForbidden("올바르지 않은 내려받기 주소입니다.")
    order = get_object_or_404(Order, id=order_id, buyer=request.user, status=Order.Status.PAID)
    file = order.content.file
    inline = request.GET.get("inline") == "1"  # 영상은 내려받지 않고 화면에서 재생한다
    return FileResponse(file.open("rb"), as_attachment=not inline, filename=file.name.rsplit("/", 1)[-1])


@login_required
def watch(request, order_id):
    """강의 영상을 사이트 안에서 본다."""
    order = get_object_or_404(Order, id=order_id, buyer=request.user, status=Order.Status.PAID,
                              content__kind=Content.Kind.VIDEO)
    video_url = reverse("shop:download_file", args=[signer.sign(str(order.id))]) + "?inline=1"
    return render(request, "shop/watch.html", {"order": order, "video_url": video_url})
