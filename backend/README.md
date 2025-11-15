# K-SectorRadar Backend

K-SectorRadar 백엔드 애플리케이션

## 기술 스택

- **Framework**: FastAPI 0.104.x+
- **Database**: MySQL (개발 및 프로덕션)
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

### 3. 데이터베이스 설정

#### 3.1 MySQL 설치 및 데이터베이스 생성

```bash
# MySQL 설치 (macOS)
brew install mysql
brew services start mysql

# MySQL 설치 (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install mysql-server
sudo systemctl start mysql

# MySQL 접속
mysql -u root -p

# 데이터베이스 생성
CREATE DATABASE sectorradar CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 사용자 생성 및 권한 부여 (선택사항)
CREATE USER 'sectorradar'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON sectorradar.* TO 'sectorradar'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### 3.2 환경 변수 설정

`.env` 파일을 생성하고 다음 내용을 추가하세요:

```bash
# Database Configuration
# MySQL (Development & Production)
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/sectorradar

# 또는 사용자 계정 사용 시
# DATABASE_URL=mysql+pymysql://sectorradar:your_password@localhost:3306/sectorradar

# PostgreSQL (Optional Alternative - not recommended)
# DATABASE_URL=postgresql://user:password@localhost:5432/sectorradar

# SQLite (Alternative - for testing only)
# DATABASE_URL=sqlite:///./data/sectorradar.db

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Data Collection
AUTO_REFRESH_INTERVAL=30
NAVER_FINANCE_BASE_URL=https://finance.naver.com
NAVER_NEWS_BASE_URL=https://search.naver.com

# Logging
LOG_LEVEL=INFO

# Environment (development, production)
ENVIRONMENT=development
```

### 4. 데이터베이스 초기화

#### 방법 1: 직접 실행 (권장)
```bash
python -m app.database
```

#### 방법 2: 시드 스크립트 사용
```bash
python scripts/seed_stocks.py
```

#### 방법 3: Alembic 마이그레이션 사용
```bash
# 초기 마이그레이션 생성
alembic revision --autogenerate -m "Initial migration"

# 마이그레이션 적용
alembic upgrade head

# 시드 데이터 로드
python scripts/seed_stocks.py
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

## 데이터베이스 마이그레이션

### Alembic 사용

```bash
# 현재 리비전 확인
alembic current

# 마이그레이션 히스토리 확인
alembic history

# 새 마이그레이션 생성 (모델 변경 후)
alembic revision --autogenerate -m "Description of changes"

# 마이그레이션 적용
alembic upgrade head

# 마이그레이션 롤백
alembic downgrade -1
```

또는 스크립트 사용:
```bash
python scripts/run_migrations.py upgrade
python scripts/run_migrations.py revision "Description"
```

## 테스트

```bash
pytest
pytest --cov=app --cov-report=html
```

