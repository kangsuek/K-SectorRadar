# K-SectorRadar Backend

K-SectorRadar 백엔드 애플리케이션

## 기술 스택

- **Framework**: FastAPI 0.104.x+
- **Database**: PostgreSQL/MySQL (프로덕션), SQLite (개발)
- **ORM**: SQLAlchemy 2.0+
- **Cache**: Redis 7.x+
- **Scheduler**: APScheduler 3.10.x+

## 설치 및 실행

### 1. 가상 환경 생성

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
# 개발 환경의 경우
pip install -r requirements-dev.txt
```

### 3. 환경 변수 설정

```bash
cp .env.example .env
# .env 파일을 편집하여 데이터베이스 및 Redis 설정 수정
```

### 4. 데이터베이스 초기화

```bash
python -m app.database
```

### 5. 서버 실행

```bash
uvicorn app.main:app --reload
```

서버는 http://localhost:8000 에서 실행됩니다.

API 문서는 http://localhost:8000/docs 에서 확인할 수 있습니다.

## 프로젝트 구조

```
backend/
├── app/
│   ├── api/          # API 라우터
│   ├── models/       # 데이터 모델
│   ├── services/     # 비즈니스 로직
│   ├── collectors/   # 데이터 수집기
│   ├── schemas/      # Pydantic 스키마
│   ├── utils/        # 유틸리티 함수
│   ├── config.py     # 설정
│   ├── database.py   # 데이터베이스 연결
│   └── main.py       # 애플리케이션 진입점
├── config/           # 설정 파일
├── tests/            # 테스트
└── scripts/          # 유틸리티 스크립트
```

## 테스트

```bash
pytest
pytest --cov=app --cov-report=html
```

