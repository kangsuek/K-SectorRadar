# ETFWeeklyReport 기능 분석 및 개선 계획

## 문서 개요

이 문서는 K-SectorRadar 프로젝트의 기반이 되는 ETFWeeklyReport 프로젝트의 기존 기능을 분석하고, 개선이 필요한 사항을 정리한 문서입니다.

**작성일**: 2025-01-XX  
**대상 프로젝트**: ETFWeeklyReport  
**개선 프로젝트**: K-SectorRadar

---

## 1. 기존 기능 분석

### 1.1 백엔드 기능

#### 1.1.1 API 엔드포인트

**구현 완료된 기능:**

1. **종목 관리 (ETFs)**
   - `GET /api/etfs/` - 전체 종목 목록 조회
   - `GET /api/etfs/{ticker}` - 종목 기본 정보 조회
   - `GET /api/etfs/{ticker}/prices` - 가격 데이터 조회 (날짜 범위 필터링 지원)
   - `GET /api/etfs/{ticker}/trading-flow` - 투자자별 매매 동향 조회
   - `GET /api/etfs/{ticker}/metrics` - 종목 지표 조회
   - `GET /api/etfs/compare` - 종목 비교 분석
   - `POST /api/etfs/{ticker}/collect` - 가격 데이터 수집 트리거
   - `POST /api/etfs/{ticker}/collect-trading-flow` - 매매 동향 데이터 수집 트리거

2. **뉴스 관리 (News)**
   - `GET /api/news/{ticker}` - 종목별 뉴스 조회 (날짜 범위 필터링 지원)
   - `POST /api/news/{ticker}/collect` - 뉴스 데이터 수집 트리거

3. **데이터 수집 관리 (Data)**
   - `POST /api/data/collect-all` - 전체 종목 데이터 일괄 수집
   - `POST /api/data/backfill` - 과거 데이터 백필
   - `GET /api/data/status` - 데이터 수집 상태 조회
   - `GET /api/data/scheduler-status` - 스케줄러 상태 조회
   - `GET /api/data/stats` - 데이터 통계 조회
   - `DELETE /api/data/reset` - 데이터베이스 초기화

4. **설정 관리 (Settings)**
   - `POST /api/settings/stocks` - 종목 추가
   - `PUT /api/settings/stocks/{ticker}` - 종목 정보 수정
   - `DELETE /api/settings/stocks/{ticker}` - 종목 삭제
   - `GET /api/settings/stocks/{ticker}/validate` - 종목 코드 검증

5. **리포트 (Reports)**
   - `POST /api/reports/generate` - 리포트 생성 (deprecated)

#### 1.1.2 데이터 수집 기능

**구현 완료:**
- Naver Finance 웹 스크래핑을 통한 가격 데이터 수집
- Naver Finance를 통한 투자자별 매매 동향 수집
- Naver News API를 통한 뉴스 데이터 수집
- Rate Limiter를 통한 API 호출 제한 관리
- Retry 메커니즘을 통한 안정적인 데이터 수집
- APScheduler를 사용한 자동 스케줄링 (주기적 데이터 수집)

**데이터 소스:**
- 가격 데이터: Naver Finance (웹 스크래핑)
- 매매 동향: Naver Finance (웹 스크래핑)
- 뉴스 데이터: Naver News API

#### 1.1.3 데이터베이스

**구현 완료:**
- SQLite 데이터베이스 (개발 환경)
- 4개 테이블: `etfs`, `prices`, `trading_flow`, `news`
- 기본 인덱스 설정 (ticker, date 기준)
- Foreign Key 제약 조건

**테이블 구조:**
- `etfs`: 종목 기본 정보 (ticker, name, type, theme, launch_date, expense_ratio 등)
- `prices`: 가격 데이터 (ticker, date, close_price, volume, daily_change_pct 등)
- `trading_flow`: 투자자별 매매 동향 (ticker, date, individual_net, institutional_net, foreign_net)
- `news`: 뉴스 데이터 (ticker, date, title, url, source, relevance_score)

### 1.2 프론트엔드 기능

#### 1.2.1 페이지 구성

**구현 완료된 페이지:**

1. **대시보드 (`/`)**
   - 종목 카드 그리드 표시
   - 종목별 실시간 가격 정보
   - 종목별 미니 차트 (6일간 캔들스틱)
   - 투자자별 매매 동향 표시
   - 최신 뉴스 헤드라인 표시
   - 정렬 기능 (타입, 이름, 테마, 등락률, 거래량)
   - 자동 갱신 토글 (30초 간격)
   - 수동 새로고침 버튼

2. **종목 상세 페이지 (`/etf/:ticker`)**
   - 종목 기본 정보 표시
   - 가격 차트 (캔들스틱, 이동평균선)
   - 가격 테이블
   - 통계 요약 (수익률, 변동성 등)
   - 투자자별 매매 동향 차트
   - 뉴스 타임라인
   - 날짜 범위 선택 기능

3. **비교 페이지 (`/compare`)**
   - 여러 종목 선택 기능
   - 정규화된 가격 비교 차트
   - 비교 테이블

4. **설정 페이지 (`/settings`)**
   - 종목 관리 (추가, 수정, 삭제)
   - 데이터 관리 (통계, 수집, 초기화)
   - 일반 설정

#### 1.2.2 UI/UX 기능

**구현 완료:**
- ✅ 다크 모드 완전 지원 (모든 컴포넌트)
- ✅ 반응형 디자인 (모바일/데스크톱)
- ✅ 로딩 상태 표시 (Skeleton UI)
- ✅ 에러 처리 (Error Boundary)
- ✅ Toast 알림 시스템
- ✅ 차트 시각화 (Recharts)

#### 1.2.3 상태 관리

**구현 완료:**
- TanStack Query (React Query)를 사용한 서버 상태 관리
- Context API를 사용한 클라이언트 상태 관리 (Settings, Toast)
- 자동 캐싱 및 재조회 로직

### 1.3 기술 스택 현황

#### 1.3.1 백엔드

| 기술 | 버전 | 상태 | 비고 |
|------|------|------|------|
| Python | 3.10+ | ✅ | - |
| FastAPI | 0.104.1 | ✅ | - |
| SQLite | - | ✅ | 개발 환경만 |
| PostgreSQL | - | ❌ | 프로덕션 계획만 있음, 미구현 |
| APScheduler | - | ✅ | 스케줄러 구현 완료 |
| BeautifulSoup4 | 4.12.2 | ✅ | 웹 스크래핑 |
| requests | 2.31.0 | ✅ | HTTP 요청 |
| Redis | - | ❌ | 미구현 |

#### 1.3.2 프론트엔드

| 기술 | 버전 | 상태 | 비고 |
|------|------|------|------|
| React | 18.2.0 | ✅ | - |
| JavaScript | - | ✅ | **TypeScript 미사용** |
| Vite | 5.0.0 | ✅ | - |
| React Router | 6.20.0 | ✅ | - |
| TanStack Query | 5.8.4 | ✅ | - |
| TailwindCSS | 3.3.5 | ✅ | - |
| Recharts | 2.10.3 | ✅ | - |

### 1.4 테스트 현황

**백엔드:**
- pytest 사용
- 61개 테스트 (Phase 1)
- 196개 테스트 (Phase 2)
- 커버리지: 82% (Phase 1), 89% (Phase 2)

**프론트엔드:**
- Vitest 사용
- React Testing Library 사용
- 컴포넌트별 테스트 작성

---

## 2. 개선이 필요한 사항

### 2.1 기술 스택 개선 (High Priority)

#### 2.1.1 TypeScript 도입
**현재 상태:** JavaScript 사용 중  
**개선 필요성:**
- 타입 안정성 향상
- 개발 생산성 향상
- 런타임 에러 감소
- 코드 자동완성 및 리팩토링 지원

**영향 범위:**
- 모든 프론트엔드 파일 (.jsx → .tsx)
- 타입 정의 파일 생성 필요
- API 클라이언트 타입 정의

#### 2.1.2 데이터베이스 개선
**현재 상태:** SQLite만 사용 (개발 환경)  
**개선 필요성:**
- 프로덕션 환경 대비 (동시성, 성능)
- PostgreSQL/MySQL 지원 필요
- ORM 도입 검토 (SQLAlchemy 2.0+)

**영향 범위:**
- 데이터베이스 연결 로직
- 쿼리 작성 방식 (ORM 사용 시)
- 마이그레이션 시스템

#### 2.1.3 Redis 캐싱 레이어 추가
**현재 상태:** 미구현  
**개선 필요성:**
- API 응답 속도 향상
- 데이터베이스 부하 감소
- 실시간 데이터 캐싱
- 세션 관리 (향후 인증 기능 확장 시)

**영향 범위:**
- API 엔드포인트에 캐싱 로직 추가
- 캐시 무효화 전략 수립
- 캐시 TTL 설정

### 2.2 아키텍처 개선 (Medium Priority)

#### 2.2.1 ORM 도입
**현재 상태:** 직접 SQL 사용  
**개선 필요성:**
- 코드 가독성 향상
- 타입 안정성 향상
- 데이터베이스 독립성 확보
- 마이그레이션 관리 용이

**권장 기술:** SQLAlchemy 2.0+

#### 2.2.2 서비스 레이어 개선
**현재 상태:** 기본적인 서비스 레이어 존재  
**개선 필요성:**
- 의존성 주입 개선
- 인터페이스 분리
- 테스트 용이성 향상

#### 2.2.3 에러 처리 개선
**현재 상태:** 기본적인 에러 처리 구현  
**개선 필요성:**
- 일관된 에러 응답 형식
- 에러 로깅 개선
- 클라이언트 친화적 에러 메시지

### 2.3 기능 개선 (Medium Priority)

#### 2.3.1 실시간 데이터 갱신 개선
**현재 상태:** 30초 간격 자동 갱신 구현됨  
**개선 필요성:**
- WebSocket 또는 Server-Sent Events (SSE) 도입 검토
- 더 효율적인 데이터 갱신 전략
- 부분 갱신 (변경된 데이터만)

#### 2.3.2 데이터 수집 안정성 향상
**현재 상태:** Rate Limiter, Retry 메커니즘 구현됨  
**개선 필요성:**
- 더 정교한 에러 처리
- 수집 실패 알림 시스템
- 수집 이력 관리

#### 2.3.3 리포트 생성 기능 개선
**현재 상태:** deprecated 상태  
**개선 필요성:**
- PDF 생성 기능 구현
- 마크다운 리포트 개선
- 리포트 템플릿 시스템

### 2.4 UI/UX 개선 (Low Priority)

#### 2.4.1 성능 최적화
**현재 상태:** 기본적인 최적화 적용  
**개선 필요성:**
- 코드 스플리팅
- 이미지 최적화
- 가상 스크롤링 (대량 데이터 표시 시)

#### 2.4.2 접근성 개선
**현재 상태:** 기본적인 접근성 지원  
**개선 필요성:**
- ARIA 레이블 추가
- 키보드 네비게이션 개선
- 스크린 리더 지원

#### 2.4.3 국제화 (i18n) 지원
**현재 상태:** 한국어만 지원  
**개선 필요성:**
- 다국어 지원 (향후 확장 시)

### 2.5 테스트 개선 (Medium Priority)

#### 2.5.1 E2E 테스트 추가
**현재 상태:** 단위 테스트, 통합 테스트만 존재  
**개선 필요성:**
- Playwright 또는 Cypress 도입
- 주요 사용자 시나리오 테스트

#### 2.5.2 테스트 커버리지 향상
**현재 상태:** 백엔드 82-89%, 프론트엔드 미확인  
**개선 필요성:**
- 목표 커버리지 90% 이상
- 엣지 케이스 테스트 추가

### 2.6 문서화 개선 (Low Priority)

#### 2.6.1 API 문서 개선
**현재 상태:** Swagger UI 기본 제공  
**개선 필요성:**
- 더 상세한 예제 추가
- 에러 응답 예제 추가

#### 2.6.2 개발 가이드 개선
**현재 상태:** 기본적인 가이드 존재  
**개선 필요성:**
- 온보딩 가이드 추가
- 컨트리뷰션 가이드 추가

---

## 3. 우선순위별 개선 계획

### 3.1 Phase 1: 핵심 기술 스택 개선 (필수)

**목표:** K-SectorRadar의 핵심 차별화 요소 구현

1. **TypeScript 도입**
   - [ ] 프론트엔드 TypeScript 설정
   - [ ] 기존 .jsx 파일을 .tsx로 변환
   - [ ] 타입 정의 파일 생성
   - [ ] API 클라이언트 타입 정의

2. **PostgreSQL/MySQL 지원**
   - [ ] 데이터베이스 연결 설정
   - [ ] SQLite → PostgreSQL 마이그레이션 스크립트
   - [ ] 환경별 데이터베이스 설정

3. **Redis 캐싱 레이어**
   - [ ] Redis 연결 설정
   - [ ] 주요 API 엔드포인트에 캐싱 적용
   - [ ] 캐시 무효화 전략 구현

**예상 기간:** 2-3주

### 3.2 Phase 2: 아키텍처 개선

1. **ORM 도입 (SQLAlchemy 2.0+)**
   - [ ] SQLAlchemy 모델 정의
   - [ ] 기존 SQL 쿼리를 ORM으로 변환
   - [ ] 마이그레이션 시스템 구축

2. **서비스 레이어 개선**
   - [ ] 의존성 주입 개선
   - [ ] 인터페이스 분리
   - [ ] 테스트 용이성 향상

**예상 기간:** 2-3주

### 3.3 Phase 3: 기능 개선

1. **실시간 데이터 갱신 개선**
   - [ ] WebSocket 또는 SSE 도입 검토
   - [ ] 부분 갱신 전략 구현

2. **데이터 수집 안정성 향상**
   - [ ] 수집 실패 알림 시스템
   - [ ] 수집 이력 관리

3. **리포트 생성 기능 개선**
   - [ ] PDF 생성 기능 구현
   - [ ] 리포트 템플릿 시스템

**예상 기간:** 3-4주

### 3.4 Phase 4: 테스트 및 최적화

1. **E2E 테스트 추가**
   - [ ] Playwright 또는 Cypress 설정
   - [ ] 주요 시나리오 테스트 작성

2. **성능 최적화**
   - [ ] 코드 스플리팅
   - [ ] 이미지 최적화
   - [ ] 캐싱 전략 최적화

**예상 기간:** 2-3주

---

## 4. 마이그레이션 전략

### 4.1 데이터 마이그레이션

**SQLite → PostgreSQL:**
1. SQLite 데이터 덤프
2. PostgreSQL 스키마 생성
3. 데이터 변환 및 이관
4. 검증 스크립트 실행

### 4.2 코드 마이그레이션

**JavaScript → TypeScript:**
1. 점진적 마이그레이션 (파일 단위)
2. 타입 정의 우선 생성
3. 기존 코드에 타입 추가
4. 타입 에러 수정

### 4.3 호환성 유지

- 기존 API 엔드포인트 유지
- 점진적 개선 (Breaking Change 최소화)
- 버전 관리 전략 수립

---

## 5. 참고 자료

### 5.1 ETFWeeklyReport 문서
- [API 명세서](../ETFWeeklyReport/docs/API_SPECIFICATION.md)
- [아키텍처 문서](../ETFWeeklyReport/docs/ARCHITECTURE.md)
- [데이터베이스 스키마](../ETFWeeklyReport/docs/DATABASE_SCHEMA.md)
- [기술 스택](../ETFWeeklyReport/docs/TECH_STACK.md)

### 5.2 K-SectorRadar 문서
- [요구사항 명세서](./eng/01-Requirements-Specification.md)
- [기술 스택 명세서](./eng/02-System-Technology-Stack-Specification.md)
- [데이터/API 설계 명세서](./eng/05-Data-API-Design-Specification.md)
- [UI/UX 설계 명세서](./eng/06-UI-UX-Design-Specification.md)

---

## 6. 체크리스트

### 6.1 필수 개선 사항
- [ ] TypeScript 도입
- [ ] PostgreSQL/MySQL 지원
- [ ] Redis 캐싱 레이어
- [ ] ORM 도입 (SQLAlchemy 2.0+)

### 6.2 권장 개선 사항
- [ ] 실시간 데이터 갱신 개선
- [ ] E2E 테스트 추가
- [ ] 성능 최적화
- [ ] 리포트 생성 기능 개선

### 6.3 선택적 개선 사항
- [ ] 국제화 (i18n) 지원
- [ ] 접근성 개선
- [ ] 문서화 개선

---
