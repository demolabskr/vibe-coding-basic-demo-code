from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import SignupForm


def signup(request):
    """가입하면 바로 로그인하고, 오던 곳(next)이 있으면 그리로 돌려보낸다."""
    next_url = request.POST.get("next") or request.GET.get("next") or "/"
    if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        next_url = "/"
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"{user.username}님, 가입을 환영합니다.")
            return redirect(next_url)
    else:
        form = SignupForm()
    return render(request, "registration/signup.html", {"form": form, "next": next_url})
