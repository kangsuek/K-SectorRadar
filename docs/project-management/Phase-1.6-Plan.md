# Phase 1.6 문서화 작업 세부 계획

> 작성일: 2025-11-15
> 상태: 진행 중

---

## 📋 개요

Phase 1에서 구현된 내용을 바탕으로 프로젝트 문서화 작업을 수행합니다.

### 목표

- Phase 1에서 구현된 API 엔드포인트 문서화
- 데이터베이스 스키마 완전 문서화
- 개발 환경 설정 가이드 작성

---

## 📚 작업 대상 문서

### 1. API_SPECIFICATION.md

**경로**: `docs/eng/API_SPECIFICATION.md`

**목적**: Phase 1에서 구현된 실제 API 엔드포인트를 개발자와 사용자가 쉽게 참조할 수 있도록 문서화

**포함 내용**:

#### 1.1 개요
- API 기본 정보 (Base URL, 버전, 응답 형식)
- 인증 방식 (현재 미적용)
- 일반 응답 구조 (APIResponse 스키마)

#### 1.2 구현된 엔드포인트 (Phase 1 완료분)

**Health Check**
- `GET /api/health` - Health Check
  - 데이터베이스 연결 상태
  - Redis 연결 상태
  - 전체 시스템 상태

**종목 관리**
- `GET /api/stocks` - 종목 목록 조회
  - 쿼리 파라미터 (type, theme, limit, offset)
  - 캐싱 적용 (TTL: 1시간)
  - 응답 예시 및 스키마

- `GET /api/stocks/{ticker}` - 종목 상세 조회
  - 캐싱 적용 (TTL: 1시간)
  - 응답 예시 및 스키마

**가격 데이터**
- `GET /api/prices/{ticker}` - 가격 데이터 조회
  - 쿼리 파라미터 (start_date, end_date, limit, offset)
  - 날짜 범위 필터링 (YYYY-MM-DD 형식)
  - 캐싱 적용 (TTL: 30분)
  - 응답 예시 및 스키마

#### 1.3 기본 구조만 구현된 엔드포인트 (Phase 2 예정)
- `GET /api/stocks/{ticker}/trading` - 매매 동향 (TODO)
- `GET /api/stocks/{ticker}/news` - 뉴스 데이터 (TODO)
- `GET /api/stocks/{ticker}/chart` - 차트 데이터 (TODO)

#### 1.4 에러 응답
- 에러 응답 구조 (ErrorResponse 스키마)
- 에러 코드 목록
  - NOT_FOUND (404)
  - BAD_REQUEST (400)
  - VALIDATION_ERROR (422)
  - INTERNAL_ERROR (500)
- 각 에러 응답 예시

#### 1.5 공통 스키마
- APIResponse
- ErrorResponse
- StockResponse / StockListResponse
- PriceResponse / PriceListResponse

---

### 2. DATABASE_SCHEMA.md

**경로**: `docs/eng/DATABASE_SCHEMA.md`

**목적**: 실제 구현된 데이터베이스 스키마를 문서화하여 데이터베이스 구조를 명확히 이해

**포함 내용**:

#### 2.1 데이터베이스 개요
- DBMS: MySQL 8.0+ (개발 환경: SQLite 지원)
- 인코딩: UTF-8
- 타임존: UTC
- ORM: SQLAlchemy 2.0+

#### 2.2 테이블 스키마

**stocks 테이블**
- 필드 목록 및 타입
- Primary Key: ticker
- 인덱스: idx_type, idx_theme
- 제약조건: CHECK (type IN ('STOCK', 'ETF'))
- SQLAlchemy 모델 정의
- 실제 CREATE TABLE SQL

**prices 테이블**
- 필드 목록 및 타입
- Primary Key: id (auto increment)
- Foreign Key: ticker → stocks(ticker) ON DELETE CASCADE
- 인덱스: idx_ticker_date, idx_ticker_timestamp
- SQLAlchemy 모델 정의
- 실제 CREATE TABLE SQL

**trading_trends 테이블**
- 필드 목록 및 타입
- Primary Key: id (auto increment)
- Foreign Key: ticker → stocks(ticker) ON DELETE CASCADE
- 인덱스: idx_ticker_date, idx_ticker_timestamp
- SQLAlchemy 모델 정의
- 실제 CREATE TABLE SQL

**news 테이블**
- 필드 목록 및 타입
- Primary Key: id
- Foreign Key: ticker → stocks(ticker) ON DELETE CASCADE
- 인덱스: idx_ticker_published, idx_published_at
- 유니크 제약: uk_url
- SQLAlchemy 모델 정의
- 실제 CREATE TABLE SQL

#### 2.3 관계도 (ERD)
- 테이블 간 관계 (텍스트 기반 ERD)
- stocks 1:N prices, trading_trends, news

#### 2.4 인덱스 전략
- 각 인덱스의 목적
- 쿼리 성능 최적화 전략

#### 2.5 마이그레이션
- Alembic 사용
- 초기 마이그레이션 파일 위치
- 마이그레이션 실행 방법

---

### 3. DEVELOPMENT_GUIDE.md

**경로**: `docs/eng/DEVELOPMENT_GUIDE.md`

**목적**: 개발자가 로컬 환경에서 프로젝트를 설정하고 실행할 수 있도록 가이드

**포함 내용**:

#### 3.1 개발 환경 요구사항
- Python 3.10+
- Node.js 18+
- MySQL 8.0+ / SQLite (개발용)
- Redis 7.x+
- Docker & Docker Compose (선택)

#### 3.2 프로젝트 구조
- 디렉토리 구조 설명
- 주요 파일 및 역할

#### 3.3 백엔드 설정

**가상환경 설정**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**환경 변수 설정**
- `.env.example` 복사하여 `.env` 생성
- DATABASE_URL 설정
  - MySQL: `mysql+pymysql://user:password@localhost:3306/sectorradar`
  - SQLite: `sqlite:///./sectorradar.db`
- REDIS_URL 설정: `redis://localhost:6379/0`
- 기타 설정 (CORS_ORIGINS 등)

**데이터베이스 설정**

MySQL 사용 시:
```bash
# 데이터베이스 생성
mysql -u root -p
CREATE DATABASE sectorradar CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 마이그레이션 실행
python scripts/run_migrations.py

# 초기 데이터 시드
python scripts/seed_stocks.py
```

SQLite 사용 시 (개발 환경):
```bash
# 자동으로 데이터베이스 파일 생성됨
python -m app.database

# 초기 데이터 시드
python scripts/seed_stocks.py
```

**Redis 설정**

Docker로 Redis 실행:
```bash
docker run -d --name redis -p 6379:6379 redis:7-alpine
```

로컬 Redis 설치:
- macOS: `brew install redis && brew services start redis`
- Ubuntu: `sudo apt install redis-server`
- Windows: Redis for Windows 사용

Redis 연결 확인:
```bash
redis-cli ping
# 응답: PONG
```

**서버 실행**
```bash
uvicorn app.main:app --reload
# 접속: http://localhost:8000
# API 문서: http://localhost:8000/docs
```

#### 3.4 테스트 실행

**단위 테스트**
```bash
pytest tests/ -v
```

**커버리지 확인**
```bash
pytest --cov=app --cov-report=html tests/
# 리포트: htmlcov/index.html
```

**특정 테스트 실행**
```bash
pytest tests/test_api_stocks.py -v
```

#### 3.5 API 문서 접근
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- 각 엔드포인트 테스트 방법

#### 3.6 개발 워크플로우
- 코드 스타일 가이드 (Black, Flake8)
- 커밋 메시지 규칙
- 브랜치 전략

#### 3.7 트러블슈팅
- 자주 발생하는 문제 및 해결 방법
- 데이터베이스 연결 오류
- Redis 연결 오류
- 포트 충돌 문제

---

## 📊 작업 항목 체크리스트

### Phase 1.6: 문서화

#### 1. API 명세서 작성 (`docs/eng/API_SPECIFICATION.md`)
- [ ] 문서 구조 설계
- [ ] API 개요 작성
- [ ] Phase 1 구현 완료 엔드포인트 문서화
  - [ ] Health Check API
  - [ ] 종목 목록 조회 API
  - [ ] 종목 상세 조회 API
  - [ ] 가격 데이터 조회 API
- [ ] 기본 구조만 있는 엔드포인트 표시
- [ ] 에러 응답 문서화
- [ ] 공통 스키마 문서화
- [ ] 요청/응답 예시 작성

#### 2. 데이터베이스 스키마 문서 작성 (`docs/eng/DATABASE_SCHEMA.md`)
- [ ] 문서 구조 설계
- [ ] 데이터베이스 개요 작성
- [ ] stocks 테이블 문서화
- [ ] prices 테이블 문서화
- [ ] trading_trends 테이블 문서화
- [ ] news 테이블 문서화
- [ ] ERD (텍스트 기반) 작성
- [ ] 인덱스 전략 문서화
- [ ] 마이그레이션 가이드 작성

#### 3. 개발 가이드 작성 (`docs/eng/DEVELOPMENT_GUIDE.md`)
- [ ] 문서 구조 설계
- [ ] 개발 환경 요구사항 작성
- [ ] 프로젝트 구조 설명
- [ ] 백엔드 설정 가이드 작성
  - [ ] 가상환경 설정
  - [ ] 환경 변수 설정
  - [ ] 데이터베이스 설정 (MySQL & SQLite)
  - [ ] Redis 설정
  - [ ] 서버 실행
- [ ] 테스트 실행 가이드 작성
- [ ] API 문서 접근 방법 작성
- [ ] 개발 워크플로우 작성
- [ ] 트러블슈팅 섹션 작성

#### 4. 문서 검토 및 완성
- [ ] 모든 문서 상호 참조 확인
- [ ] 코드 예제 검증
- [ ] 명령어 실행 가능 여부 확인
- [ ] 오타 및 문법 검토

---

## ⚙️ 작업 우선순위

1. **우선 순위 1**: DATABASE_SCHEMA.md (구현된 스키마가 명확하므로 가장 먼저 작성 가능)
2. **우선 순위 2**: API_SPECIFICATION.md (구현된 API를 기반으로 작성)
3. **우선 순위 3**: DEVELOPMENT_GUIDE.md (위 두 문서를 참조하여 작성)

---

## 📝 예상 작업 시간

- DATABASE_SCHEMA.md: 약 2-3시간
- API_SPECIFICATION.md: 약 3-4시간
- DEVELOPMENT_GUIDE.md: 약 4-5시간
- 검토 및 수정: 약 1-2시간

**총 예상 시간**: 10-14시간

---

## ✅ 완료 기준 (Definition of Done)

Phase 1.6 완료를 위한 기준:

### 1. API_SPECIFICATION.md
- ✅ Phase 1에서 구현된 모든 API 엔드포인트가 문서화됨
- ✅ 각 엔드포인트의 요청/응답 예시가 포함됨
- ✅ 에러 응답 및 스키마가 명확히 정의됨

### 2. DATABASE_SCHEMA.md
- ✅ 모든 테이블 스키마가 문서화됨
- ✅ 인덱스 및 제약조건이 명시됨
- ✅ 마이그레이션 가이드가 포함됨

### 3. DEVELOPMENT_GUIDE.md
- ✅ 데이터베이스 설정 가이드 (MySQL & SQLite)가 포함됨
- ✅ Redis 설정 가이드가 포함됨
- ✅ 모든 명령어가 실행 가능하고 검증됨

### 4. 문서 품질
- ✅ 오타 및 문법 오류 없음
- ✅ 코드 예제가 실제로 동작함
- ✅ 문서 간 상호 참조가 정확함

---

## 📌 참고 사항

### 현재 구현 상태 (Phase 1 완료)

**데이터베이스**
- ✅ SQLAlchemy 모델 정의 완료
- ✅ 마이그레이션 시스템 구축 (Alembic)
- ✅ MySQL/SQLite 지원

**Redis 캐싱**
- ✅ Redis 연결 설정
- ✅ 캐시 유틸리티 함수 구현
- ✅ 캐시 데코레이터 구현

**API 엔드포인트**
- ✅ Health Check (`GET /api/health`)
- ✅ 종목 목록 조회 (`GET /api/stocks`)
- ✅ 종목 상세 조회 (`GET /api/stocks/{ticker}`)
- ✅ 가격 데이터 조회 (`GET /api/prices/{ticker}`)

**테스트**
- ✅ 데이터베이스 연결 테스트
- ✅ Redis 캐싱 테스트
- ✅ API 엔드포인트 테스트
- ✅ 통합 테스트

---

## 🔗 관련 문서

- [TODO.md](./TODO.md) - 전체 프로젝트 작업 목록
- [DEFINITION_OF_DONE.md](../DEFINITION_OF_DONE.md) - 완료 기준
- [README.md](../../README.md) - 프로젝트 개요
- [03-Data-API-Design-Specification.md](../eng/03-Data-API-Design-Specification.md) - API 설계 명세

---

**작성자**: Claude
**최종 수정일**: 2025-11-15
