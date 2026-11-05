"""구매하지 않은 사람은 판매 파일을 받지 못한다는 것을 확인하는 테스트."""
from unittest import mock

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.test import TestCase, override_settings

from payments.models import Order
from shop.models import Content


@override_settings(FAKEPG_SEND_WEBHOOK=False)
class DownloadTests(TestCase):
    def setUp(self):
        self.buyer = User.objects.create_user("buyer", password="예시값1234")
        self.member = User.objects.create_user("member", password="예시값1234")
        self.book = Content(kind="ebook", title="예시 전자책", slug="sample-ebook",
                            summary="예시", description="예시", price=9000, is_published=True)
        self.book.cover.save("test-cover.png", ContentFile(b"png"), save=False)
        self.book.file.save("test-ebook.pdf", ContentFile(b"%PDF-1.4 sample"), save=False)
        self.book.save()
        self.order = Order.objects.create(buyer=self.buyer, content=self.book, amount=9000,
                                          status=Order.Status.PAID)

    def tearDown(self):
        self.book.cover.delete(save=False)
        self.book.file.delete(save=False)

    def test_visitor_is_sent_to_login(self):
        response = self.client.get(f"/download/{self.order.id}/")
        self.assertRedirects(response, f"/accounts/login/?next=/download/{self.order.id}/", fetch_redirect_response=False)

    def test_non_buyer_cannot_download(self):
        self.client.login(username="member", password="예시값1234")
        response = self.client.get(f"/download/{self.order.id}/")
        self.assertEqual(response.status_code, 404)  # 남의 주문은 없는 것처럼 보인다

    def test_unpaid_order_cannot_download(self):
        pending = Order.objects.create(buyer=self.member, content=self.book, amount=9000)
        self.client.login(username="member", password="예시값1234")
        response = self.client.get(f"/download/{pending.id}/")
        self.assertEqual(response.status_code, 403)

    def test_buyer_gets_file(self):
        self.client.login(username="buyer", password="예시값1234")
        response = self.client.get(f"/download/{self.order.id}/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("attachment", response["Content-Disposition"])
        self.assertEqual(b"".join(response.streaming_content), b"%PDF-1.4 sample")

    def test_expired_link_is_refused(self):
        self.client.login(username="buyer", password="예시값1234")
        link = self.client.get(f"/download/{self.order.id}/")["Location"]
        with mock.patch("shop.views.DOWNLOAD_LINK_SECONDS", -1):
            response = self.client.get(link)
        self.assertEqual(response.status_code, 403)

    def test_tampered_link_is_refused(self):
        self.client.login(username="buyer", password="예시값1234")
        link = self.client.get(f"/download/{self.order.id}/")["Location"]
        response = self.client.get(link.replace(":", "x", 1))
        self.assertEqual(response.status_code, 403)

    def test_private_file_has_no_public_url(self):
        response = self.client.get("/media/files/test-ebook.pdf")
        self.assertEqual(response.status_code, 404)


class ListTests(TestCase):
    def test_hidden_content_is_not_listed(self):
        Content.objects.create(kind="template", title="숨긴 서식", slug="hidden", summary="-",
                               description="-", price=1000, is_published=False)
        self.assertNotContains(self.client.get("/contents/"), "숨긴 서식")
        self.assertEqual(self.client.get("/contents/hidden/").status_code, 404)


class ApiTests(TestCase):
    def test_api_lists_published_contents_without_file_url(self):
        c = Content.objects.create(kind="ebook", title="공개 전자책", slug="open", summary="-",
                                   description="-", price=9000, is_published=True)
        c.cover.name = "covers/open.png"
        c.save()
        data = self.client.get("/api/contents/").json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["title"], "공개 전자책")
        self.assertNotIn("file", data["results"][0])
