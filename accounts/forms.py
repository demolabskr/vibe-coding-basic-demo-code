from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignupForm(UserCreationForm):
    """Django 기본 가입 양식에 메일 주소 칸을 더한다. 비밀번호 해시는 Django가 맡는다."""

    email = forms.EmailField(label="메일 주소", help_text="구매 확인 메일과 비밀번호 재설정 안내를 받습니다.")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["username", "email"]
