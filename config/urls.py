"""주소와 처리 코드를 잇는 목록(라우팅)."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("admin/", admin.site.urls),
]

# 개발 중에만 표지 이미지를 개발 서버가 내준다. 운영에서는 웹 서버나 객체 스토리지가 맡는다
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
