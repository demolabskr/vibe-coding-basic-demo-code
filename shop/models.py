from django.db import models
from django.urls import reverse

from .storage import private_storage


class Content(models.Model):
    """판매하는 콘텐츠 하나(전자책, 강의 영상, 서식)."""

    class Kind(models.TextChoices):
        EBOOK = "ebook", "전자책"
        VIDEO = "video", "강의 영상"
        TEMPLATE = "template", "서식"

    kind = models.CharField("종류", max_length=20, choices=Kind.choices)
    title = models.CharField("제목", max_length=200)
    slug = models.SlugField("주소용 이름", unique=True, help_text="주소에 쓰는 영문 이름. 예: budget")
    summary = models.CharField("한 줄 소개", max_length=200)
    description = models.TextField("설명")
    price = models.PositiveIntegerField("가격(원)")
    cover = models.ImageField("표지", upload_to="covers/")
    file = models.FileField("판매 파일", upload_to="files/", storage=private_storage)
    is_published = models.BooleanField("공개", default=False)
    created_at = models.DateTimeField("등록 시각", auto_now_add=True)
    updated_at = models.DateTimeField("수정 시각", auto_now=True)

    class Meta:
        verbose_name = "콘텐츠"
        verbose_name_plural = "콘텐츠"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("shop:content_detail", args=[self.slug])
