# 민지의 자료 가게

전자책, 강의 영상, 서식 파일을 파는 작은 판매 사이트다. 책 「바이브 코딩 기초 지식」에서 예시로 든 "나만의 콘텐츠 판매 사이트"를 실제로 바이브 코딩으로 만든 저장소다. 지은이 민지와 가게, 판매 콘텐츠는 모두 가상이며 실제로 판매하지 않는다.

- 스택: Python, Django, SQLite(개발)와 PostgreSQL(운영)
- 결제: 실제 결제 대행 서비스 대신 같은 흐름을 흉내 내는 가상 결제 서비스(`fakepg`)를 쓴다. 실제 돈은 오가지 않는다.
- 라이선스: MIT

## 실행 방법

1. [uv](https://docs.astral.sh/uv/)를 설치한다.
2. 이 저장소를 받고 폴더로 들어간다.
3. `.env.example`을 `.env`로 복사하고 `DJANGO_SECRET_KEY`를 긴 무작위 문자열로 바꾼다.
4. 패키지를 설치하고 데이터베이스를 만든다.

   ```text
   uv sync
   uv run python manage.py migrate
   uv run python manage.py seed_demo
   ```

   `seed_demo`는 예시 계정과 콘텐츠를 넣는다. 운영자 `minji`, 회원 `buyer`와 `member`이고 비밀번호는 모두 예시값 `demo-pass-1234`다.

5. 개발 서버를 켜고 브라우저에서 http://127.0.0.1:8000/ 을 연다.

   ```text
   uv run python manage.py runserver
   ```
