from django.shortcuts import render

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
    """상세 페이지는 다음 요청에서 만든다. 지금은 목록 카드의 연결만 잇는다."""
    from django.http import HttpResponse
    return HttpResponse("상세 페이지 준비 중")
