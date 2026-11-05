from django.conf import settings


def site(request):
    """모든 화면에서 사이트 이름을 쓸 수 있게 한다."""
    return {"SITE_NAME": settings.SITE_NAME}
