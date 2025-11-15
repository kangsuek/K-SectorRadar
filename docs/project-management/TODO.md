# TODO

## ⚠️ 중요 원칙
1. **테스트 우선**: 테스트 통과 후 다음 단계. 커버리지 80%+ (Phase), 90%+ (최종)
2. **백엔드 API 우선**: API 먼저 구현 → Swagger UI 테스트 → 프론트엔드
3. **문서 즉시 업데이트**: 요구사항 변경 시 관련 문서 즉시 업데이트

### Phase 완료 조건
- 모든 체크리스트 완료
- 테스트 통과 (커버리지 목표 달성)
- API 문서화 완료 (백엔드)
- 관련 문서 업데이트 완료

---

## Phase 1: 프로젝트 초기화

### 1.1 프로젝트 구조 및 설정 (완료)
- [x] 프로젝트 디렉토리 구조 생성
- [x] .cursorrules 파일 생성
- [x] README.md 및 초기 설정 파일 생성
- [x] Backend 디렉토리 구조 및 초기 파일 생성
- [x] Frontend 디렉토리 구조 및 초기 파일 생성

### 1.2 데이터베이스 스키마 구현
- [x] SQLAlchemy 모델 정의
  - [x] `app/models/stock.py` - Stock 모델 완성 (인덱스 추가)
  - [x] `app/models/price.py` - Price 모델 완성
  - [x] `app/models/trading_trend.py` - TradingTrend 모델 완성
  - [x] `app/models/news.py` - News 모델 완성
  - [x] `app/models/__init__.py` - 모델 export 정리
- [x] 데이터베이스 연결 설정
  - [x] `app/database.py` - PostgreSQL/MySQL 연결 설정
  - [x] 환경 변수 설정 (README.md에 예시 추가)
  - [x] SQLite 개발 환경 지원
  - [x] 데이터베이스 연결 풀 설정
- [x] 마이그레이션 시스템 구축
  - [x] Alembic 초기화 및 설정
  - [x] 초기 마이그레이션 파일 생성 (사용자 실행 필요)
  - [x] 마이그레이션 실행 스크립트 작성 (`scripts/run_migrations.py`)
- [x] 데이터베이스 초기화 및 시드
  - [x] `app/database.py` - `init_db()` 함수 구현
  - [x] 초기 종목 데이터 시드 스크립트 작성 (`scripts/seed_stocks.py`)
  - [x] `config/stocks.json` 데이터를 DB에 로드하는 로직 구현

### 1.3 Redis 캐싱 레이어 구현
- [x] Redis 연결 설정
  - [x] `app/config.py` - Redis 설정 추가
  - [x] `app/utils/redis.py` - Redis 클라이언트 유틸리티 생성
  - [x] 환경 변수 설정 (.env.example 업데이트)
  - [x] Redis 연결 테스트
- [x] 캐시 유틸리티 함수 구현
  - [x] `app/utils/cache.py` - 캐시 헬퍼 함수 생성
    - [x] `get_cache(key)` - 캐시 조회
    - [x] `set_cache(key, value, ttl)` - 캐시 저장
    - [x] `delete_cache(key)` - 캐시 삭제
    - [x] `clear_cache_pattern(pattern)` - 패턴 기반 캐시 삭제
- [x] 캐시 데코레이터 구현
  - [x] `app/utils/cache.py` - `@cache_result` 데코레이터 구현
  - [x] TTL 설정 가능한 캐시 데코레이터
  - [x] 캐시 키 생성 전략
- [x] 캐시 무효화 전략 수립
  - [x] 데이터 수집 시 캐시 무효화 로직
  - [x] 종목 정보 변경 시 캐시 무효화 로직
  - [x] 캐시 무효화 헬퍼 함수 구현

### 1.4 기본 API 엔드포인트 구현 (완료)
- [x] Health Check 엔드포인트
  - [x] `GET /api/health` - 서버 상태 확인
  - [x] 데이터베이스 연결 상태 확인
  - [x] Redis 연결 상태 확인
- [x] 종목 관리 API
  - [x] `GET /api/stocks` - 전체 종목 목록 조회 (캐싱 적용)
  - [x] `GET /api/stocks/{ticker}` - 종목 상세 정보 조회 (캐싱 적용)
  - [ ] `POST /api/stocks` - 종목 추가 (관리자용, Phase 2 이후)
  - [ ] `PUT /api/stocks/{ticker}` - 종목 정보 수정 (관리자용, Phase 2 이후)
  - [ ] `DELETE /api/stocks/{ticker}` - 종목 삭제 (관리자용, Phase 2 이후)
- [x] 가격 데이터 API (기본 구조)
  - [x] `GET /api/prices/{ticker}` - 종목 가격 데이터 조회 (캐싱 적용)
  - [x] 날짜 범위 필터링 지원 (query parameters)
- [x] 에러 핸들링
  - [x] `app/exceptions.py` - 커스텀 예외 클래스 정의
  - [x] `app/main.py` - 전역 예외 핸들러 등록
  - [x] 일관된 에러 응답 형식 정의
- [x] API 문서화
  - [x] Swagger UI 자동 문서화 확인
  - [x] 주요 엔드포인트에 docstring 추가
  - [x] Pydantic 스키마 정의 (`app/schemas/` 디렉토리)
    - [x] `app/schemas/stock.py` - Stock 관련 스키마
    - [x] `app/schemas/price.py` - Price 관련 스키마
    - [x] `app/schemas/response.py` - 공통 응답 스키마

### 1.5 테스트 및 검증 ⚠️ 필수 (완료)
**✅ 모든 테스트 통과: 77개 통과, 2개 skip, 88% 커버리지 달성**

- [x] 데이터베이스 연결 테스트
  - [x] `tests/test_database.py` - DB 연결 테스트 작성
  - [x] 모델 생성/조회 테스트
  - [x] 테스트 커버리지 80% 이상 달성 ✅
- [x] Redis 캐싱 테스트
  - [x] `tests/test_cache.py` - 캐시 기능 테스트 작성
  - [x] 캐시 TTL 테스트
  - [x] 캐시 무효화 테스트
  - [x] 테스트 커버리지 80% 이상 달성 ✅
- [x] API 엔드포인트 테스트
  - [x] `tests/test_api_stocks.py` - 종목 API 테스트 작성
  - [x] `tests/test_api_health.py` - Health check 테스트 작성
  - [x] `tests/test_api_prices.py` - 가격 데이터 API 테스트 작성
  - [x] 캐싱 동작 검증 테스트
  - [x] 에러 핸들링 테스트
  - [x] 테스트 커버리지 80% 이상 달성 ✅
- [x] 통합 테스트
  - [x] 데이터베이스 + Redis + API 통합 테스트 (`tests/test_integration.py`)
  - [x] 테스트 데이터베이스 설정 (`tests/conftest.py`)
  - [x] MySQL/SQLite 호환 AutoIncrementBigInteger 타입 구현 (`app/db_types.py`)
  - [ ] Swagger UI를 통한 API 수동 테스트 완료 (수동 확인 필요)
- [x] Phase 1 완료 검증
  - [x] 모든 테스트 통과 확인 (77개 통과, 2개 skip) ✅
  - [x] 테스트 커버리지 리포트 확인 (88% 달성) ✅
  - [ ] API 문서화 완료 확인 (Swagger UI) - Phase 1.6에서 완료 예정
  - [ ] 관련 문서 업데이트 완료 확인 - Phase 1.6에서 완료 예정

**주요 수정사항:**
- 중복 인덱스 이름 수정 (SQLite 전역 고유 요구사항)
- Pydantic v2 마이그레이션 (Config → ConfigDict)
- API 응답 직렬화 개선 (by_alias=True, mode='json')
- SQLite 외래키 제약조건 활성화
- MySQL/SQLite 호환 AutoIncrementBigInteger 타입 구현

### 1.6 문서화
- [ ] API 명세서 업데이트
  - [ ] `docs/API_SPECIFICATION.md` - Phase 1 엔드포인트 문서화
- [ ] 데이터베이스 스키마 문서 업데이트
  - [ ] `docs/DATABASE_SCHEMA.md` - 최종 스키마 반영
- [ ] 개발 가이드 업데이트
  - [ ] `docs/DEVELOPMENT_GUIDE.md` - 데이터베이스 설정 가이드 추가
  - [ ] `docs/DEVELOPMENT_GUIDE.md` - Redis 설정 가이드 추가

## Phase 2: 데이터 수집 기능
**⚠️ Phase 1의 모든 테스트가 통과한 후에만 시작합니다.**

### 2.1 데이터 수집기 구현 (백엔드 API 우선)
- [ ] Naver Finance 데이터 수집기 구현
  - [ ] `app/collectors/finance_collector.py` - 가격 데이터 수집기 구현
  - [ ] `app/collectors/finance_collector.py` - 매매 동향 데이터 수집기 구현
  - [ ] `POST /api/data/collect/prices/{ticker}` - 가격 데이터 수집 API
  - [ ] `POST /api/data/collect/trading/{ticker}` - 매매 동향 수집 API
  - [ ] API 테스트 작성 및 통과
- [ ] Naver News 데이터 수집기 구현
  - [ ] `app/collectors/news_collector.py` - 뉴스 데이터 수집기 구현
  - [ ] `POST /api/data/collect/news/{ticker}` - 뉴스 데이터 수집 API
  - [ ] API 테스트 작성 및 통과
- [ ] 스케줄러 구현 (30초 간격 자동 갱신)
  - [ ] `app/scheduler/data_scheduler.py` - APScheduler 기반 스케줄러 구현
  - [ ] `GET /api/scheduler/status` - 스케줄러 상태 조회 API
  - [ ] `POST /api/scheduler/start` - 스케줄러 시작 API
  - [ ] `POST /api/scheduler/stop` - 스케줄러 중지 API
  - [ ] API 테스트 작성 및 통과
- [ ] 데이터 검증 로직 구현
  - [ ] `app/utils/validators.py` - 데이터 검증 유틸리티 구현
  - [ ] 가격 데이터 검증 로직
  - [ ] 매매 동향 데이터 검증 로직
  - [ ] 뉴스 데이터 검증 로직

### 2.2 테스트 및 검증 ⚠️ 필수
- [ ] 데이터 수집기 단위 테스트
  - [ ] `tests/test_finance_collector.py` - Finance 수집기 테스트
  - [ ] `tests/test_news_collector.py` - News 수집기 테스트
  - [ ] 테스트 커버리지 80% 이상 달성
- [ ] 스케줄러 테스트
  - [ ] `tests/test_scheduler.py` - 스케줄러 테스트 작성
  - [ ] 테스트 커버리지 80% 이상 달성
- [ ] API 엔드포인트 테스트
  - [ ] `tests/test_api_data_collection.py` - 데이터 수집 API 테스트
  - [ ] `tests/test_api_scheduler.py` - 스케줄러 API 테스트
  - [ ] 테스트 커버리지 80% 이상 달성
- [ ] 통합 테스트
  - [ ] 데이터 수집 → 저장 → 조회 전체 플로우 테스트
  - [ ] 스케줄러 자동 수집 테스트
- [ ] Phase 2 완료 검증
  - [ ] 모든 테스트 통과 확인
  - [ ] 테스트 커버리지 리포트 확인 (80% 이상)
  - [ ] API 문서화 완료 확인 (Swagger UI)
  - [ ] 관련 문서 업데이트 완료 확인

## Phase 3: Frontend 기본 기능
**⚠️ Phase 2의 모든 테스트가 통과한 후에만 시작합니다.**
**⚠️ 백엔드 API가 완성되어 있어야 프론트엔드 개발이 가능합니다.**

### 3.1 백엔드 API 완성 확인
- [ ] Phase 2에서 구현한 모든 API가 정상 동작하는지 확인
- [ ] Swagger UI를 통한 API 테스트 완료
- [ ] API 응답 형식 및 에러 핸들링 확인

### 3.2 Frontend 기본 기능 구현
- [ ] 대시보드 페이지 구현
  - [ ] `frontend/src/pages/Dashboard.tsx` - 대시보드 페이지 구현
  - [ ] 백엔드 API 연동 (`GET /api/stocks`)
  - [ ] 종목 카드 컴포넌트 구현
  - [ ] 자동 갱신 기능 구현
  - [ ] 테스트 작성 및 통과
- [ ] 종목 상세 페이지 구현
  - [ ] `frontend/src/pages/StockDetail.tsx` - 상세 페이지 구현
  - [ ] 백엔드 API 연동 (`GET /api/stocks/{ticker}`, `GET /api/prices/{ticker}`)
  - [ ] 가격 정보 표시
  - [ ] 테스트 작성 및 통과
- [ ] 비교 페이지 구현
  - [ ] `frontend/src/pages/Comparison.tsx` - 비교 페이지 구현
  - [ ] 백엔드 API 연동 (`GET /api/stocks/compare`)
  - [ ] 종목 선택 기능
  - [ ] 테스트 작성 및 통과
- [ ] 설정 페이지 구현
  - [ ] `frontend/src/pages/Settings.tsx` - 설정 페이지 구현
  - [ ] 백엔드 API 연동 (종목 관리 API)
  - [ ] 테스트 작성 및 통과
- [ ] 다크 모드 완전 지원
  - [ ] 모든 페이지 및 컴포넌트에 다크 모드 적용
  - [ ] 다크 모드 상태 관리 (Context API 또는 Zustand)
  - [ ] 테스트 작성 및 통과

### 3.3 테스트 및 검증 ⚠️ 필수
- [ ] 컴포넌트 단위 테스트
  - [ ] 각 페이지 컴포넌트 테스트 작성
  - [ ] 테스트 커버리지 80% 이상 달성
- [ ] API 연동 테스트
  - [ ] MSW(Mock Service Worker)를 사용한 API 모킹
  - [ ] API 호출 테스트
- [ ] 통합 테스트
  - [ ] 페이지 간 네비게이션 테스트
  - [ ] 사용자 시나리오 테스트
- [ ] Phase 3 완료 검증
  - [ ] 모든 테스트 통과 확인
  - [ ] 테스트 커버리지 리포트 확인 (80% 이상)
  - [ ] 다크 모드 동작 확인
  - [ ] 관련 문서 업데이트 완료 확인

## Phase 4: 차트 및 시각화
**⚠️ Phase 3의 모든 테스트가 통과한 후에만 시작합니다.**

### 4.1 백엔드 API (차트 데이터 제공)
- [ ] 차트 데이터 API 구현
  - [ ] `GET /api/charts/prices/{ticker}` - 가격 차트 데이터 API
  - [ ] `GET /api/charts/volume/{ticker}` - 거래량 차트 데이터 API
  - [ ] `GET /api/charts/mini/{ticker}` - 미니 차트 데이터 API (최근 6일)
  - [ ] API 테스트 작성 및 통과

### 4.2 Frontend 차트 구현
- [ ] 가격 차트 구현
  - [ ] `frontend/src/components/charts/PriceChart.tsx` - 가격 차트 컴포넌트
  - [ ] 백엔드 API 연동
  - [ ] 캔들스틱 차트 구현
  - [ ] 이동평균선 표시
  - [ ] 테스트 작성 및 통과
- [ ] 거래량 차트 구현
  - [ ] `frontend/src/components/charts/VolumeChart.tsx` - 거래량 차트 컴포넌트
  - [ ] 백엔드 API 연동
  - [ ] 테스트 작성 및 통과
- [ ] 미니 차트 구현 (대시보드 카드용)
  - [ ] `frontend/src/components/charts/MiniChart.tsx` - 미니 차트 컴포넌트
  - [ ] 백엔드 API 연동
  - [ ] 대시보드 카드에 통합
  - [ ] 테스트 작성 및 통과

### 4.3 테스트 및 검증 ⚠️ 필수
- [ ] 차트 컴포넌트 테스트
  - [ ] 각 차트 컴포넌트 테스트 작성
  - [ ] 테스트 커버리지 80% 이상 달성
- [ ] 차트 API 테스트
  - [ ] `tests/test_api_charts.py` - 차트 API 테스트 작성
  - [ ] 테스트 커버리지 80% 이상 달성
- [ ] 통합 테스트
  - [ ] 차트 렌더링 성능 테스트 (1초 이내)
  - [ ] 차트 데이터 정확성 테스트
- [ ] Phase 4 완료 검증
  - [ ] 모든 테스트 통과 확인
  - [ ] 테스트 커버리지 리포트 확인 (80% 이상)
  - [ ] 차트 성능 목표 달성 확인
  - [ ] 관련 문서 업데이트 완료 확인

## Phase 5: 테스트 및 최적화
**⚠️ Phase 4의 모든 테스트가 통과한 후에만 시작합니다.**

### 5.1 테스트 커버리지 향상
- [ ] 백엔드 테스트 보완
  - [ ] 누락된 엣지 케이스 테스트 추가
  - [ ] 통합 테스트 보완
  - [ ] E2E 테스트 작성 (선택사항)
  - [ ] 테스트 커버리지 90% 이상 달성
- [ ] 프론트엔드 테스트 보완
  - [ ] 컴포넌트 테스트 보완
  - [ ] 통합 테스트 보완
  - [ ] E2E 테스트 작성 (Playwright 또는 Cypress)
  - [ ] 테스트 커버리지 90% 이상 달성

### 5.2 성능 최적화
- [ ] 백엔드 성능 최적화
  - [ ] 데이터베이스 쿼리 최적화
  - [ ] Redis 캐싱 전략 최적화
  - [ ] API 응답 시간 측정 및 개선
- [ ] 프론트엔드 성능 최적화
  - [ ] 코드 스플리팅
  - [ ] 이미지 최적화
  - [ ] 번들 크기 최적화
  - [ ] 페이지 로딩 시간 3초 이내 달성

### 5.3 문서화 완료
- [ ] API 명세서 최종 업데이트
  - [ ] `docs/API_SPECIFICATION.md` - 모든 엔드포인트 문서화
- [ ] 개발 가이드 최종 업데이트
  - [ ] `docs/DEVELOPMENT_GUIDE.md` - 완전한 개발 가이드
- [ ] 배포 가이드 작성
  - [ ] `docs/DEPLOYMENT_GUIDE.md` - 배포 가이드 작성
- [ ] README 최종 업데이트
  - [ ] 프로젝트 개요, 설치, 실행 방법 등 완성

### 5.4 Phase 5 완료 검증
- [ ] 모든 테스트 통과 확인
- [ ] 테스트 커버리지 리포트 확인 (90% 이상)
- [ ] 성능 목표 달성 확인
- [ ] 모든 문서 업데이트 완료 확인
- [ ] 코드 리뷰 완료
- [ ] 프로젝트 완료 선언

