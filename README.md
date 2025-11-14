# K-SectorRadar

한국 고성장 섹터 분석 웹 애플리케이션 (ETFWeeklyReport 개선 버전)

## 📊 프로젝트 개요

한국 고성장 섹터 관련 종목(ETF 및 주식)에 대한 실시간 모니터링, 상세 분석, 비교 분석 기능을 제공하는 웹 애플리케이션입니다.

## 🎯 주요 기능

- **실시간 모니터링**: 30초 간격 자동 데이터 갱신
- **대시보드**: 종목별 카드 형태의 모니터링 인터페이스
- **상세 분석**: 종목별 상세 정보 및 차트 분석
- **비교 분석**: 여러 종목 간 비교 분석
- **설정 관리**: 시스템 설정 및 종목 관리
- **다크 모드**: 완전한 다크 모드 지원

## 📊 초기 수집 대상 종목

### ETF 4개
1. **삼성 KODEX AI전력핵심설비 ETF** (487240) - AI & 전력 인프라
2. **신한 SOL 조선TOP3플러스 ETF** (466920) - 조선업
3. **KoAct 글로벌양자컴퓨팅액티브 ETF** (0020H0) - 양자컴퓨팅
4. **KB RISE 글로벌원자력 iSelect ETF** (442320) - 원자력

### 주식 2개
5. **한화오션** (042660) - 조선/방산
6. **두산에너빌리티** (034020) - 에너지/전력

## 🚀 빠른 시작

### 사전 요구사항
- Python 3.10+
- Node.js 18+
- PostgreSQL (또는 MySQL)
- Redis 7.x+
- Docker & Docker Compose (선택사항)

### Docker를 사용한 실행 (권장)

```bash
docker-compose up -d
```

### 수동 실행

#### 백엔드
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# .env 파일에서 데이터베이스 및 Redis 설정 수정
python -m app.database  # 데이터베이스 초기화
uvicorn app.main:app --reload
```
→ http://localhost:8000/docs

#### 프론트엔드
```bash
cd frontend
npm install
npm run dev
```
→ http://localhost:5173

## 🔧 기술 스택

### Backend
- **Framework**: FastAPI 0.104.x+
- **Database**: PostgreSQL/MySQL (프로덕션), SQLite (개발)
- **ORM**: SQLAlchemy 2.0+
- **Cache**: Redis 7.x+
- **Scheduler**: APScheduler 3.10.x+
- **Data Collection**: BeautifulSoup4, Requests

### Frontend
- **Framework**: React 18.x+ with TypeScript 5.x+
- **Build Tool**: Vite 5.x+
- **Routing**: React Router 6.x+
- **State Management**: TanStack Query 5.x+ (server), Zustand/Context API (client)
- **Styling**: Tailwind CSS 3.x+
- **Charts**: Recharts
- **Dark Mode**: 완전 지원

## 📚 문서

- **[CLAUDE.md](./CLAUDE.md)** - 문서 인덱스
- [요구사항 명세서](./docs/eng/01-Requirements-Specification.md) (영문)
- [기술 스택 명세서](./docs/eng/02-System-Technology-Stack-Specification.md) (영문)
- [데이터/API 설계 명세서](./docs/eng/03-Data-API-Design-Specification.md) (영문)
- [UI/UX 설계 명세서](./docs/eng/04-UI-UX-Design-Specification.md) (영문)

## 📖 데이터 소스

- **Naver Finance**: 가격 데이터, 투자자별 매매 동향
- **Naver News**: 뉴스 데이터

## 🔄 ETFWeeklyReport와의 주요 차이점

- ✅ TypeScript 사용 (타입 안정성 향상)
- ✅ PostgreSQL/MySQL 지원 (SQLite 대신)
- ✅ Redis 캐싱 레이어 추가
- ✅ 향상된 다크 모드 지원
- ✅ 더 나은 아키텍처 및 확장성
- ✅ 엄격한 타입 체크

## 📝 라이선스

MIT
