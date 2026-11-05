from django.shortcuts import get_object_or_404, render

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
