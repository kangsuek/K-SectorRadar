# K-SectorRadar Frontend

K-SectorRadar 프론트엔드 애플리케이션

## 기술 스택

- **Framework**: React 18.x+ with TypeScript 5.x+
- **Build Tool**: Vite 5.x+
- **Routing**: React Router 6.x+
- **State Management**: TanStack Query 5.x+ (server), Zustand (client)
- **Styling**: Tailwind CSS 3.x+
- **Charts**: Recharts

## 설치 및 실행

### 1. 의존성 설치

```bash
npm install
```

### 2. 개발 서버 실행

```bash
npm run dev
```

서버는 http://localhost:5173 에서 실행됩니다.

### 3. 빌드

```bash
npm run build
```

### 4. 테스트

```bash
npm test
npm run test:coverage
```

## 프로젝트 구조

```
frontend/
├── src/
│   ├── components/   # 재사용 가능한 컴포넌트
│   │   ├── common/   # 공통 컴포넌트
│   │   ├── stock/    # 주식 관련 컴포넌트
│   │   └── chart/    # 차트 컴포넌트
│   ├── pages/        # 페이지 컴포넌트
│   ├── hooks/        # 커스텀 훅
│   ├── services/      # API 서비스
│   ├── utils/        # 유틸리티 함수
│   ├── types/        # TypeScript 타입 정의
│   ├── store/        # 상태 관리
│   └── styles/       # 스타일 파일
├── public/           # 정적 파일
└── test/             # 테스트 파일
```

## 환경 변수

`.env` 파일을 생성하여 다음 변수를 설정할 수 있습니다:

```
VITE_API_BASE_URL=http://localhost:8000/api
```

