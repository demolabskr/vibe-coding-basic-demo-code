from django.urls import include, path

from . import views

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    # 로그인, 로그아웃, 비밀번호 바꾸기와 재설정은 Django에 들어 있는 기능을 쓴다
    path("", include("django.contrib.auth.urls")),
]
