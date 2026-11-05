"""주소와 처리 코드를 잇는 목록(라우팅)."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView, TemplateView

# 관리자 화면의 머리말
admin.site.site_header = "민지의 자료 가게 관리"
admin.site.site_title = "민지의 자료 가게 관리"
admin.site.index_title = "운영자 화면"

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="shop:content_list"), name="home"),
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("privacy/", TemplateView.as_view(template_name="privacy.html"), name="privacy"),
    path("", include("shop.urls")),
    path("", include("payments.urls")),
    # 가상 결제 서비스. 실제로는 결제 대행 회사의 서버에 있다
    path("fake-pg/", include("fakepg.urls")),
]

# 개발 중에만 표지 이미지를 개발 서버가 내준다. 운영에서는 웹 서버나 객체 스토리지가 맡는다
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
