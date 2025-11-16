# Swagger UI를 통한 API 수동 테스트 가이드

## 목차
1. [서버 실행](#1-서버-실행)
2. [Swagger UI 접속](#2-swagger-ui-접속)
3. [API 테스트 방법](#3-api-테스트-방법)
4. [주요 엔드포인트별 테스트 예시](#4-주요-엔드포인트별-테스트-예시)
5. [주의사항](#5-주의사항)

---

## 1. 서버 실행

### 1.1 백엔드 서버 시작

```bash
cd backend
source venv/bin/activate  # 가상 환경 활성화 (Windows: venv\Scripts\activate)
uvicorn app.main:app --reload
```

서버가 성공적으로 시작되면 다음과 같은 메시지가 표시됩니다:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
✅ Redis 연결 성공
INFO:     Application startup complete.
```

### 1.2 서버 상태 확인

브라우저에서 다음 URL을 열어 서버가 정상적으로 실행 중인지 확인합니다:
- **루트 엔드포인트**: http://localhost:8000
- **Health Check**: http://localhost:8000/api/health

---

## 2. Swagger UI 접속

### 2.1 Swagger UI URL

서버가 실행되면 다음 URL에서 Swagger UI에 접속할 수 있습니다:

**Swagger UI**: http://localhost:8000/docs

### 2.2 Swagger UI 화면 구성

Swagger UI 화면은 다음과 같이 구성되어 있습니다:

1. **상단**: API 제목 및 버전 정보
2. **왼쪽 사이드바**: API 엔드포인트 목록 (태그별로 그룹화)
3. **중앙**: 선택한 엔드포인트의 상세 정보 및 테스트 인터페이스
4. **오른쪽**: 응답 예시 및 스키마 정보

### 2.3 API 그룹 (Tags)

API는 다음과 같은 태그로 그룹화되어 있습니다:

- **stocks**: 종목 관리 API
- **prices**: 가격 데이터 API
- **trading**: 매매 동향 API (구현 대기)
- **news**: 뉴스 API (구현 대기)
- **chart**: 차트 데이터 API (구현 대기)
- **refresh**: 데이터 갱신 API (구현 대기)
- **data-collection**: 데이터 수집 API
- **scheduler**: 스케줄러 관리 API

---

## 3. API 테스트 방법

### 3.1 기본 사용법

1. **엔드포인트 선택**: 왼쪽 사이드바에서 테스트하고 싶은 API를 클릭합니다.
2. **엔드포인트 확장**: "Try it out" 버튼을 클릭합니다.
3. **파라미터 입력**: 필요한 파라미터를 입력합니다.
4. **요청 실행**: "Execute" 버튼을 클릭합니다.
5. **결과 확인**: 응답 코드, 응답 헤더, 응답 본문을 확인합니다.

### 3.2 파라미터 입력 방법

#### Path Parameters (경로 파라미터)
- URL 경로에 포함되는 파라미터
- 예: `/api/stocks/{ticker}` → `ticker` 필드에 값 입력

#### Query Parameters (쿼리 파라미터)
- URL 뒤에 `?key=value` 형식으로 추가되는 파라미터
- 예: `/api/stocks?type=STOCK&limit=10`

#### Request Body (요청 본문)
- POST, PUT 요청 시 JSON 형식으로 데이터 전송
- 스키마에 맞는 JSON 형식으로 입력
- 예시 버튼을 클릭하면 예시 JSON이 자동으로 입력됩니다

### 3.3 응답 확인

Swagger UI에서는 다음 정보를 확인할 수 있습니다:

1. **Response Code**: HTTP 상태 코드 (200, 201, 400, 404, 500 등)
2. **Response Headers**: 응답 헤더 정보
3. **Response Body**: JSON 형식의 응답 본문
4. **Curl 명령어**: 동일한 요청을 curl로 실행할 수 있는 명령어
5. **Request URL**: 실제 요청 URL

---

## 4. 주요 엔드포인트별 테스트 예시

### 4.1 Health Check API

**엔드포인트**: `GET /api/health`

**테스트 방법**:
1. "health" 섹션을 찾아 클릭
2. "Try it out" 클릭
3. "Execute" 클릭

**예상 응답**:
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "timestamp": "2025-11-14T10:30:00"
}
```

---

### 4.2 종목 목록 조회 API

**엔드포인트**: `GET /api/stocks`

**테스트 방법**:
1. "stocks" 태그의 `GET /api/stocks` 선택
2. "Try it out" 클릭
3. Query Parameters 입력 (선택사항):
   - `type`: STOCK 또는 ETF
   - `theme`: 테마 분류
   - `limit`: 페이지 크기 (기본값: 100)
   - `offset`: 오프셋 (기본값: 0)
4. "Execute" 클릭

**예시 요청**:
- 모든 종목 조회: 파라미터 없이 실행
- STOCK 타입만 조회: `type=STOCK` 입력
- 테마 필터링: `theme=Nuclear/Power Plant/Energy` 입력

**예상 응답**:
```json
{
  "success": true,
  "data": {
    "stocks": [
      {
        "ticker": "034020",
        "name": "Doosan Enerbility",
        "type": "STOCK",
        "theme": "Nuclear/Power Plant/Energy",
        "fee": null,
        "createdAt": "2025-01-01T00:00:00Z",
        "updatedAt": "2025-11-13T21:22:11Z"
      }
    ],
    "total": 50,
    "limit": 100,
    "offset": 0
  },
  "message": "",
  "timestamp": "2025-11-14T10:30:00Z"
}
```

---

### 4.3 종목 상세 조회 API

**엔드포인트**: `GET /api/stocks/{ticker}`

**테스트 방법**:
1. "stocks" 태그의 `GET /api/stocks/{ticker}` 선택
2. "Try it out" 클릭
3. Path Parameter `ticker`에 종목 코드 입력 (예: `034020`)
4. "Execute" 클릭

**예상 응답**:
```json
{
  "success": true,
  "data": {
    "ticker": "034020",
    "name": "Doosan Enerbility",
    "type": "STOCK",
    "theme": "Nuclear/Power Plant/Energy",
    "fee": null,
    "createdAt": "2025-01-01T00:00:00Z",
    "updatedAt": "2025-11-13T21:22:11Z"
  },
  "message": "",
  "timestamp": "2025-11-14T10:30:00Z"
}
```

---

### 4.4 종목 추가 API (관리자용)

**엔드포인트**: `POST /api/stocks`

**테스트 방법**:
1. "stocks" 태그의 `POST /api/stocks` 선택
2. "Try it out" 클릭
3. Request Body에 JSON 입력:
   ```json
   {
     "ticker": "TEST001",
     "name": "테스트 종목",
     "type": "STOCK",
     "theme": "테스트 테마",
     "fee": null
   }
   ```
4. "Execute" 클릭

**주의사항**:
- `ticker`는 고유값이어야 합니다 (중복 불가)
- `type`은 반드시 "STOCK" 또는 "ETF"여야 합니다
- ETF의 경우 `fee` 값을 입력할 수 있습니다

**예상 응답** (201 Created):
```json
{
  "success": true,
  "data": {
    "ticker": "TEST001",
    "name": "테스트 종목",
    "type": "STOCK",
    "theme": "테스트 테마",
    "fee": null,
    "createdAt": "2025-11-14T10:30:00Z",
    "updatedAt": "2025-11-14T10:30:00Z"
  },
  "message": "Stock 'TEST001' created successfully",
  "timestamp": "2025-11-14T10:30:00Z"
}
```

---

### 4.5 종목 정보 수정 API (관리자용)

**엔드포인트**: `PUT /api/stocks/{ticker}`

**테스트 방법**:
1. "stocks" 태그의 `PUT /api/stocks/{ticker}` 선택
2. "Try it out" 클릭
3. Path Parameter `ticker`에 종목 코드 입력
4. Request Body에 수정할 필드만 입력:
   ```json
   {
     "name": "수정된 종목명",
     "theme": "수정된 테마"
   }
   ```
5. "Execute" 클릭

**예상 응답**:
```json
{
  "success": true,
  "data": {
    "ticker": "TEST001",
    "name": "수정된 종목명",
    "type": "STOCK",
    "theme": "수정된 테마",
    "fee": null,
    "createdAt": "2025-11-14T10:30:00Z",
    "updatedAt": "2025-11-14T10:35:00Z"
  },
  "message": "Stock 'TEST001' updated successfully",
  "timestamp": "2025-11-14T10:35:00Z"
}
```

---

### 4.6 종목 삭제 API (관리자용)

**엔드포인트**: `DELETE /api/stocks/{ticker}`

**테스트 방법**:
1. "stocks" 태그의 `DELETE /api/stocks/{ticker}` 선택
2. "Try it out" 클릭
3. Path Parameter `ticker`에 삭제할 종목 코드 입력
4. "Execute" 클릭

**예상 응답**:
```json
{
  "success": true,
  "data": {
    "ticker": "TEST001"
  },
  "message": "Stock 'TEST001' deleted successfully",
  "timestamp": "2025-11-14T10:40:00Z"
}
```

---

### 4.7 가격 데이터 조회 API

**엔드포인트**: `GET /api/prices/{ticker}`

**테스트 방법**:
1. "prices" 태그의 `GET /api/prices/{ticker}` 선택
2. "Try it out" 클릭
3. Path Parameter `ticker`에 종목 코드 입력
4. Query Parameters 입력 (선택사항):
   - `start_date`: 시작 날짜 (YYYY-MM-DD 형식)
   - `end_date`: 종료 날짜 (YYYY-MM-DD 형식)
   - `limit`: 페이지 크기
   - `offset`: 오프셋
5. "Execute" 클릭

**예시 요청**:
- 모든 가격 데이터: 파라미터 없이 실행
- 날짜 범위 지정: `start_date=2025-01-01&end_date=2025-12-31`

---

### 4.8 가격 데이터 수집 API

**엔드포인트**: `POST /api/data/collect/prices/{ticker}`

**테스트 방법**:
1. "data-collection" 태그의 `POST /api/data/collect/prices/{ticker}` 선택
2. "Try it out" 클릭
3. Path Parameter `ticker`에 종목 코드 입력
4. Query Parameter `days` 입력 (기본값: 10, 최대: 365)
5. "Execute" 클릭

**주의사항**:
- 실제 네이버 파이낸스에서 데이터를 수집하므로 시간이 걸릴 수 있습니다
- 종목이 데이터베이스에 존재해야 합니다

---

### 4.9 스케줄러 상태 조회 API

**엔드포인트**: `GET /api/scheduler/status`

**테스트 방법**:
1. "scheduler" 태그의 `GET /api/scheduler/status` 선택
2. "Try it out" 클릭
3. "Execute" 클릭

**예상 응답**:
```json
{
  "success": true,
  "data": {
    "is_running": false,
    "interval_seconds": 30,
    "next_run_time": null,
    "last_run_time": null,
    "last_run_status": null,
    "last_run_error": null
  },
  "message": "Scheduler status retrieved successfully",
  "timestamp": "2025-11-14T10:30:00Z"
}
```

---

### 4.10 스케줄러 시작 API

**엔드포인트**: `POST /api/scheduler/start`

**테스트 방법**:
1. "scheduler" 태그의 `POST /api/scheduler/start` 선택
2. "Try it out" 클릭
3. Query Parameter `interval_seconds` 입력 (선택사항, 기본값: 30)
4. "Execute" 클릭

**예상 응답**:
```json
{
  "success": true,
  "data": {
    "is_running": true,
    "interval_seconds": 30,
    "message": "Scheduler started successfully"
  },
  "message": "Scheduler started successfully",
  "timestamp": "2025-11-14T10:30:00Z"
}
```

---

## 5. 주의사항

### 5.1 데이터베이스 준비

API를 테스트하기 전에 다음을 확인하세요:

1. **MySQL 설치 및 실행**: MySQL 서버가 실행 중인지 확인
2. **데이터베이스 생성**: `sectorradar` 데이터베이스가 생성되어 있는지 확인
3. **환경 변수 설정**: `.env` 파일에 올바른 `DATABASE_URL`이 설정되어 있는지 확인
4. **테이블 생성**: 데이터베이스가 초기화되어 있고 테이블이 생성되어 있는지 확인
5. **시드 데이터**: 종목 데이터가 로드되어 있는지 확인

**MySQL 설정 가이드**: `backend/SETUP_MYSQL.md` 파일을 참조하세요.

```bash
# MySQL 연결 테스트
mysql -u root -p -e "USE sectorradar; SHOW TABLES;"

# 데이터베이스 초기화 및 시드
python3 -c "from app.database import init_db; import asyncio; asyncio.run(init_db())"
python scripts/seed_stocks.py
```

### 5.2 Redis 연결 (선택사항)

캐싱 기능을 사용하려면 Redis가 실행 중이어야 합니다:

```bash
# Redis 실행 확인
redis-cli ping
# 응답: PONG

# Redis가 실행되지 않은 경우
redis-server
```

Redis가 없어도 API는 동작하지만 캐싱 기능이 제한됩니다.

### 5.3 에러 응답 확인

Swagger UI에서 에러 응답도 확인할 수 있습니다:

- **400 Bad Request**: 잘못된 요청 (예: 중복된 ticker, 잘못된 type)
- **404 Not Found**: 리소스를 찾을 수 없음 (예: 존재하지 않는 종목)
- **422 Validation Error**: 요청 검증 오류 (예: 필수 필드 누락)
- **500 Internal Server Error**: 서버 내부 오류

에러 응답 형식:
```json
{
  "success": false,
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "detail": "Detailed error message",
  "timestamp": "2025-11-14T10:30:00Z"
}
```

### 5.4 테스트 데이터 관리

테스트 후 생성한 데이터는 필요시 수동으로 삭제하거나, 테스트 데이터베이스를 사용하는 것을 권장합니다.

### 5.5 네트워크 요청

데이터 수집 API는 실제 네이버 파이낸스에 요청을 보내므로:
- 네트워크 연결이 필요합니다
- 요청에 시간이 걸릴 수 있습니다
- 과도한 요청은 IP 차단될 수 있으므로 주의하세요

---

## 6. 추가 리소스

### 6.1 ReDoc

FastAPI는 ReDoc 형식의 문서도 제공합니다:

**ReDoc URL**: http://localhost:8000/redoc

ReDoc은 읽기 전용 문서로, Swagger UI보다 더 깔끔한 문서 형식을 제공합니다.

### 6.2 OpenAPI JSON 스키마

OpenAPI 스키마를 직접 확인할 수 있습니다:

**OpenAPI JSON**: http://localhost:8000/openapi.json

이 스키마를 사용하여 Postman, Insomnia 등의 API 클라이언트에 임포트할 수 있습니다.

---

## 7. 문제 해결

### 7.1 서버가 시작되지 않는 경우

- 포트 8000이 이미 사용 중인지 확인
- 데이터베이스 연결 설정 확인
- 가상 환경이 활성화되어 있는지 확인

### 7.2 API 요청이 실패하는 경우

- MySQL 서버가 실행 중인지 확인
- `.env` 파일의 `DATABASE_URL`이 올바른지 확인 (MySQL 비밀번호 확인)
- 데이터베이스에 테이블이 생성되어 있는지 확인
- 종목 데이터가 시드되어 있는지 확인
- 에러 응답의 `detail` 필드를 확인하여 원인 파악

**MySQL 연결 오류 해결**: `backend/SETUP_MYSQL.md`의 "문제 해결" 섹션을 참조하세요.

### 7.3 캐시가 작동하지 않는 경우

- Redis가 실행 중인지 확인
- `.env` 파일의 `REDIS_URL` 설정 확인

---

이 가이드를 참고하여 Swagger UI를 통해 모든 API를 테스트할 수 있습니다.

