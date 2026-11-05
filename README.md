# 민지의 자료 가게

전자책, 강의 영상, 서식 파일을 파는 작은 판매 사이트다. 책 「바이브 코딩 기초 지식」에서 예시로 든 "나만의 콘텐츠 판매 사이트"를 실제로 바이브 코딩으로 만든 저장소다. 지은이 민지와 가게, 판매 콘텐츠는 모두 가상이며 실제로 판매하지 않는다.

- 스택: Python, Django, SQLite(개발)와 PostgreSQL(운영). 화면은 Django 템플릿으로 서버에서 그린다.
- 결제: 실제 결제 대행 서비스 대신 같은 흐름을 흉내 내는 가상 결제 서비스(`fakepg`)를 쓴다. 실제 돈은 오가지 않는다.
- 라이선스: MIT(코드와 `sample_data/`의 예시 표지·파일 모두)

## 무엇이 들어 있나

| 기능 | 주소 |
|---|---|
| 콘텐츠 목록과 상세 | `/contents/`, `/contents/<slug>/` |
| 가입, 로그인, 비밀번호 재설정 | `/accounts/...` |
| 주문, 결제(가상 결제창), 결제 재확인, 웹훅 | `/orders/`, `/payments/...` |
| 내 자료실, 구매자만 받는 내려받기, 영상 보기 | `/library/`, `/download/<주문 id>/` |
| 구매 확인 메일 | 결제 완료 뒤 자동 |
| 운영자 관리 화면, 판매 기록 CSV | `/admin/` |
| 콘텐츠 목록 API | `/api/contents/` |
| 전날 판매 보고 메일 | `python manage.py sales_report` |

## 문서

| 문서 | 내용 |
|---|---|
| [docs/plan-memo.md](docs/plan-memo.md) | 만들기 전에 적은 한 문단 기획 메모 |
| [docs/PRD.md](docs/PRD.md) | 무엇을 왜 어디까지 만드는지 적은 요구 사항 문서 |
| [docs/wireframe.md](docs/wireframe.md) | 화면 흐름과 화면마다 들어갈 요소 |
| [docs/requests.md](docs/requests.md) | AI에게 보낸 열 개의 요청과 단계별 태그 |
| [docs/architecture.md](docs/architecture.md) | 폴더, 주소, 데이터, 결제와 내려받기 흐름, 환경 변수 |
| [docs/deploy-checklist.md](docs/deploy-checklist.md) | 배포 전후 점검표 |
| [AGENTS.md](AGENTS.md) | AI 코딩 에이전트가 매번 읽는 규칙 파일 |

## 단계별로 보기

요청 하나가 끝날 때마다 태그를 붙였다(`step-00`부터 `step-10`, 마지막은 `book-v1`). 태그로 옮기면 그 단계의 사이트를 그대로 볼 수 있다.

```text
git switch --detach step-03    목록 페이지까지 만든 상태
git switch main                마지막 상태로 돌아오기
```

GitHub에서는 Tags 목록에서 단계를 골라 그 시점의 코드를 볼 수 있다.

## 실행 방법

1. [uv](https://docs.astral.sh/uv/)를 설치한다.
2. 이 저장소를 받는다. Git이 없으면 GitHub의 Code 버튼에서 ZIP으로 받아 풀어도 된다.

   ```text
   git clone https://github.com/demolabskr/vibe-coding-basic-demo-code.git
   cd vibe-coding-basic-demo-code
   ```

3. `.env.example`을 `.env`로 복사하고 `DJANGO_SECRET_KEY`를 긴 무작위 문자열로 바꾼다.
4. 패키지를 설치하고 데이터베이스와 예시 데이터를 만든다.

   ```text
   uv sync
   uv run python manage.py migrate
   uv run python manage.py seed_demo
   ```

   `seed_demo`는 예시 계정과 콘텐츠를 넣는다. 운영자 `minji`, 회원 `buyer`와 `member`이고 비밀번호는 모두 예시값 `demo-pass-1234`다. `buyer`는 두 건을 산 상태로 시작한다.

5. 개발 서버를 켜고 브라우저에서 http://127.0.0.1:8000/ 을 연다. 관리자 화면은 http://127.0.0.1:8000/admin/ 이다.

   ```text
   uv run python manage.py runserver
   ```

6. 테스트를 돌린다.

   ```text
   uv run python manage.py test
   ```

구매 확인 메일은 개발 중에 실제로 나가지 않고 서버를 켠 터미널에 찍힌다.

## 실제로 운영하려면

이 저장소는 배우기 위한 예시다. 실제 판매에 쓰려면 적어도 다음을 직접 확인한다.

- 결제 대행 서비스와 계약하고 `payments/pg.py`를 그 서비스의 공식 문서에 맞춰 고친다.
- 개인정보 처리방침, 전자상거래 관련 고지, 환불 규정을 공식 안내와 전문가의 확인을 받아 작성한다.
- [배포 점검표](docs/deploy-checklist.md)를 따른다.
