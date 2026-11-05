"""콘텐츠 목록을 데이터(JSON)로 주는 API.

    GET /api/contents/          공개된 콘텐츠 목록
    GET /api/contents/<slug>/   콘텐츠 하나

화면 대신 데이터를 주는 주소다. 판매 파일 주소는 넣지 않는다.
"""
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET

from .models import Content


def to_dict(request, c):
    return {
        "slug": c.slug,
        "kind": c.kind,
        "title": c.title,
        "summary": c.summary,
        "price": c.price,
        "sale_price": c.sale_price,
        "cover": request.build_absolute_uri(c.cover.url),
        "url": request.build_absolute_uri(c.get_absolute_url()),
    }


@require_GET
def content_list(request):
    items = [to_dict(request, c) for c in Content.objects.filter(is_published=True)]
    return JsonResponse({"count": len(items), "results": items}, json_dumps_params={"ensure_ascii": False})


@require_GET
def content_detail(request, slug):
    c = get_object_or_404(Content, slug=slug, is_published=True)
    return JsonResponse(to_dict(request, c), json_dumps_params={"ensure_ascii": False})
