# Development Guide

## 1. Document Overview

### 1.1 Purpose
This document provides a comprehensive guide for setting up and developing the K-SectorRadar project.

### 1.2 Scope
This guide covers:
- Prerequisites and system requirements
- Database setup (MySQL - Primary, PostgreSQL - Alternative, SQLite - Testing only)
- Redis setup and configuration
- Environment variable configuration
- Development environment setup
- Testing and migration procedures

### 1.3 References
- API Specification: `docs/eng/03-API_SPECIFICATION.md`
- Database Schema: `docs/eng/04-DATABASE_SCHEMA.md`
- Requirements Specification: `docs/eng/01-Requirements-Specification.md`

---

## 2. Prerequisites

### 2.1 Required Software
- **Python**: 3.10 or higher
- **Node.js**: 18 or higher (for frontend)
- **Database**: MySQL 8.0+ (required for development and production)
- **Redis**: 7.x or higher
- **Git**: Latest version

**Note**: PostgreSQL is supported as an alternative, and SQLite can be used for testing only.

### 2.2 Optional Software
- **Docker & Docker Compose**: For containerized development
- **Postman/Insomnia**: For API testing
- **VS Code**: Recommended IDE with Python and TypeScript extensions

---

## 3. Database Setup

**⚠️ Important**: MySQL is the **primary and recommended** database for both development and production environments. PostgreSQL is supported as an alternative, and SQLite should only be used for testing.

### 3.1 MySQL Setup (Primary - Development & Production)

#### 3.1.1 Installation
**macOS (Homebrew)**:
```bash
brew install mysql
brew services start mysql
```

**Ubuntu/Debian**:
```bash
sudo apt update
sudo apt install mysql-server
sudo systemctl start mysql
sudo systemctl enable mysql
```

**Windows**:
Download MySQL Installer from [mysql.com](https://dev.mysql.com/downloads/installer/)

#### 3.1.2 Database Creation
```bash
# MySQL 접속
mysql -u root -p

# 데이터베이스 생성
CREATE DATABASE sectorradar CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 사용자 생성 및 권한 부여 (선택사항)
CREATE USER 'sectorradar'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON sectorradar.* TO 'sectorradar'@'localhost';
FLUSH PRIVILEGES;

# 종료
EXIT;
```

#### 3.1.3 Connection String Format
```
mysql+pymysql://username:password@localhost:3306/sectorradar
```

**Example**:
```
mysql+pymysql://root:password@localhost:3306/sectorradar
```

### 3.2 PostgreSQL Setup (Optional Alternative)

**Note**: PostgreSQL is supported but not recommended. Use only if you have specific requirements.

**Connection String**: `postgresql://username:password@localhost:5432/sectorradar`

For installation and setup details, refer to [PostgreSQL official documentation](https://www.postgresql.org/docs/).

### 3.3 SQLite Setup (Testing Only)

**⚠️ Warning**: SQLite is for testing only. Do not use for development or production.

**Connection String**: `sqlite:///./database/sectorradar.db`

No installation required. The database file is created automatically.

### 3.4 Database Initialization

```bash
cd backend
python -m app.database
```

This creates all tables and seeds initial stock data from `config/stocks.json`.

**Alternative**: Use `python scripts/seed_stocks.py` to seed data only.

---

## 4. Redis Setup

### 4.1 Installation

**macOS**: `brew install redis && brew services start redis`  
**Ubuntu/Debian**: `sudo apt install redis-server && sudo systemctl start redis-server`  
**Windows**: Download from [redis.io](https://redis.io/download) or use WSL2  
**Docker**: `docker run -d -p 6379:6379 --name redis redis:7-alpine`

### 4.2 Configuration

**Connection String**: `redis://localhost:6379/0`

**Test Connection**: `redis-cli ping` (should return `PONG`)

### 4.3 Verification

The application automatically tests Redis connection on startup. If Redis is unavailable, the app will run but caching will be disabled.

---

## 5. Environment Variables

### 5.1 Backend Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
cd backend
cp .env.example .env  # If .env.example exists
# Or create .env manually
```

#### 5.1.1 Required Variables

```env
# Database (MySQL - Primary, required for development & production)
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/sectorradar

# Alternative databases (not recommended for production):
# PostgreSQL: DATABASE_URL=postgresql://postgres:password@localhost:5432/sectorradar
# SQLite (testing only): DATABASE_URL=sqlite:///./database/sectorradar.db

# Redis
REDIS_URL=redis://localhost:6379/0
```

#### 5.1.2 Optional Variables

```env
# API Settings
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# CORS
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]

# Data Collection
AUTO_REFRESH_INTERVAL=30
NAVER_FINANCE_BASE_URL=https://finance.naver.com
NAVER_NEWS_BASE_URL=https://search.naver.com

# Logging
LOG_LEVEL=INFO

# Environment
ENVIRONMENT=development
```

### 5.2 Frontend Environment Variables

Create a `.env` file in the `frontend/` directory:

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

---

## 6. Development Environment Setup

### 6.1 Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
# Create .env file with DATABASE_URL and REDIS_URL
python -m app.database  # Initialize database
uvicorn app.main:app --reload
```

**URLs**: API (http://localhost:8000), Swagger UI (http://localhost:8000/docs), ReDoc (http://localhost:8000/redoc)

### 6.2 Frontend Setup

```bash
cd frontend
npm install
echo "VITE_API_BASE_URL=http://localhost:8000/api" > .env
npm run dev
```

**URL**: http://localhost:5173

---

## 7. Database Migrations

**Using Migration Script** (Recommended):
```bash
cd backend
python scripts/run_migrations.py upgrade        # Apply all
python scripts/run_migrations.py downgrade -1   # Rollback
python scripts/run_migrations.py revision "Description"  # Create new
```

**Using Alembic Directly**:
```bash
alembic upgrade head
alembic downgrade -1
alembic revision --autogenerate -m "Description"
```

**Best Practices**: Review migrations before applying, test on dev first, create backups for production.

---

## 8. Testing

### 8.1 Running Tests

#### 8.1.1 Run All Tests
```bash
cd backend
pytest
```

#### 8.1.2 Run with Coverage
```bash
pytest --cov=app --cov-report=html --cov-report=term-missing
```

Coverage report will be generated in `backend/htmlcov/index.html`

#### 8.1.3 Run Specific Test File
```bash
pytest tests/test_database.py -v
pytest tests/test_api_stocks.py -v
pytest tests/test_cache.py -v
```

#### 8.1.4 Run Specific Test
```bash
pytest tests/test_api_stocks.py::TestGetStocks::test_get_stocks_empty -v
```

### 8.2 Test Configuration

Test configuration is in `backend/pytest.ini`:
- Test paths: `tests/`
- Coverage: `app/`
- Reports: HTML and terminal

### 8.3 Test Database

Tests use SQLite in-memory database by default (configured in `tests/conftest.py`). This ensures:
- Fast test execution
- No external database dependency
- Automatic cleanup after tests

### 8.4 Test Coverage Goals

- **Phase 1-4**: Minimum 80% coverage
- **Phase 5 (Final)**: Minimum 90% coverage

Current coverage: **88%** ✅

### 8.5 Swagger UI Manual Testing

**Access**: http://localhost:8000/docs (ReDoc: http://localhost:8000/redoc)

**Prerequisites**:
1. Database initialized: `python -m app.database`
2. Backend server running: `uvicorn app.main:app --reload`
3. Redis running (optional): `redis-cli ping`

**Testing Steps**:
1. Open Swagger UI in browser
2. Click "Try it out" on any endpoint
3. Fill parameters and click "Execute"
4. Review response

**Phase 1 Endpoints to Test**:
- `GET /api/health` - Verify server/database/Redis status
- `GET /api/stocks` - List all stocks (with optional filters: type, theme, limit, offset)
- `GET /api/stocks/{ticker}` - Get stock detail (test with valid/invalid ticker)
- `GET /api/prices/{ticker}` - Get price data (with optional date range: start_date, end_date)

**Verification Checklist**:
- [ ] All endpoints return expected response format
- [ ] Error handling works (404, invalid date format, etc.)
- [ ] Caching works (second request faster)
- [ ] Filters and pagination work correctly

**Troubleshooting**:
- **Failed to fetch**: Check server is running (`curl http://localhost:8000/api/health`)
- **Database errors**: Verify `DATABASE_URL` in `.env` and run `python -m app.database`
- **Empty responses**: Seed data with `python scripts/seed_stocks.py`

---

## 9. Project Structure

### 9.1 Backend Structure
```
backend/
├── app/
│   ├── api/           # API 라우터
│   ├── models/        # SQLAlchemy 모델
│   ├── schemas/       # Pydantic 스키마
│   ├── utils/         # 유틸리티 함수
│   ├── collectors/    # 데이터 수집기
│   ├── services/      # 비즈니스 로직
│   ├── config.py      # 설정
│   ├── database.py    # 데이터베이스 연결
│   └── main.py        # FastAPI 앱 진입점
├── alembic/           # 마이그레이션 파일
├── tests/             # 테스트 파일
├── scripts/           # 유틸리티 스크립트
├── config/            # 설정 파일 (stocks.json)
└── requirements.txt   # Python 의존성
```

### 9.2 Frontend Structure
```
frontend/
├── src/
│   ├── components/    # React 컴포넌트
│   ├── pages/         # 페이지 컴포넌트
│   ├── hooks/         # 커스텀 훅
│   ├── services/      # API 서비스
│   ├── utils/         # 유틸리티 함수
│   ├── types/         # TypeScript 타입
│   └── store/         # 상태 관리
├── public/            # 정적 파일
└── package.json       # Node.js 의존성
```

---

## 10. Troubleshooting

**Database Connection**:
- Verify MySQL is running: `mysql -u root -p`
- Check `DATABASE_URL` in `.env` (format: `mysql+pymysql://user:pass@host:port/db`)
- Ensure database exists and user has permissions
- For MySQL: Ensure UTF8MB4 encoding: `ALTER DATABASE sectorradar CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;`

**Redis Connection**:
- Verify Redis is running: `redis-cli ping` (should return `PONG`)
- Check `REDIS_URL` in `.env` (default: `redis://localhost:6379/0`)
- Note: Redis is optional - app works without it (caching disabled)

**Migration Issues**:
- Check status: `alembic current`
- Review migration files for errors
- Test on development database first

**Import Errors**:
- Activate virtual environment
- Install dependencies: `pip install -r requirements.txt`
- Check you're in `backend/` directory

---

## 11. Additional Resources

### 11.1 Documentation
- **API Specification**: `docs/eng/03-API_SPECIFICATION.md`
- **Database Schema**: `docs/eng/04-DATABASE_SCHEMA.md`
- **Requirements**: `docs/eng/01-Requirements-Specification.md`
- **TODO**: `docs/project-management/TODO.md`

### 11.2 External Resources
- **FastAPI**: https://fastapi.tiangolo.com/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **Alembic**: https://alembic.sqlalchemy.org/
- **Redis**: https://redis.io/documentation
- **React**: https://react.dev/
- **TypeScript**: https://www.typescriptlang.org/

---

## 12. Quick Reference

### 12.1 Common Commands

```bash
# Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Database
python -m app.database
python scripts/seed_stocks.py

# Migrations
python scripts/run_migrations.py upgrade
python scripts/run_migrations.py revision "Description"

# Tests
pytest
pytest --cov=app --cov-report=html

# Frontend
cd frontend
npm install
npm run dev
```

### 12.2 Important URLs

- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs (Interactive API testing)
- **ReDoc**: http://localhost:8000/redoc (Alternative API documentation)
- **Frontend**: http://localhost:5173


---

## 13. Version History

**Version 1.2.0**: MySQL as primary database, documentation simplified  
**Version 1.1.0**: Added Swagger UI testing guide  
**Version 1.0.0**: Initial development guide

