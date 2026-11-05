"""판매 파일을 두는 저장소.

판매 파일은 공개 주소가 없는 private/ 폴더에 둔다.
누구나 볼 수 있는 표지(media/)와 따로 두어, 파일 주소가 새어도 받을 수 없게 한다.
"""
from django.conf import settings
from django.core.files.storage import FileSystemStorage


def private_storage():
    # 함수로 두면 마이그레이션 파일에 내 컴퓨터의 폴더 경로가 적히지 않는다
    return FileSystemStorage(location=settings.PRIVATE_ROOT, base_url=None)
