# Development Guide

## 1. Document Overview

This guide covers setup and development for K-SectorRadar: prerequisites, database/Redis setup, environment configuration, testing, and migrations.

**References**: API Spec (`03-API_SPECIFICATION.md`), DB Schema (`04-DATABASE_SCHEMA.md`), Requirements (`01-Requirements-Specification.md`)

---

## 2. Prerequisites

**Required**: Python 3.10+, Node.js 18+ (frontend), MySQL 8.0+ (primary), Redis 7.x+, Git

**Optional**: Docker, Postman/Insomnia, VS Code

**Note**: PostgreSQL supported as alternative, SQLite for testing only.

---

## 3. Database Setup

**⚠️ MySQL is primary** (dev & prod). PostgreSQL supported as alternative. SQLite for testing only.

### 3.1 MySQL Setup

**Installation**:  
- macOS: `brew install mysql && brew services start mysql`
- Ubuntu/Debian: `sudo apt install mysql-server && sudo systemctl start mysql`
- Windows: Download from [mysql.com](https://dev.mysql.com/downloads/installer/)

**Database Creation**:
```bash
mysql -u root -p
CREATE DATABASE sectorradar CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
# Optional: CREATE USER 'sectorradar'@'localhost' IDENTIFIED BY 'password';
# Optional: GRANT ALL PRIVILEGES ON sectorradar.* TO 'sectorradar'@'localhost';
EXIT;
```

**Connection String**: `mysql+pymysql://username:password@localhost:3306/sectorradar`

### 3.2 PostgreSQL (Alternative)

**Connection String**: `postgresql://username:password@localhost:5432/sectorradar`  
See [PostgreSQL docs](https://www.postgresql.org/docs/) for installation.

### 3.3 SQLite (Testing Only)

**Connection String**: `sqlite:///./database/sectorradar.db`  
⚠️ Testing only - not for dev/prod.

### 3.4 Database Initialization

```bash
cd backend
python -m app.database  # Creates tables and seeds from config/stocks.json
# Or: python scripts/seed_stocks.py  # Seed only
```

---

## 4. Redis Setup

**Installation**:  
- macOS: `brew install redis && brew services start redis`
- Ubuntu/Debian: `sudo apt install redis-server && sudo systemctl start redis-server`
- Windows: Download from [redis.io](https://redis.io/download) or use WSL2
- Docker: `docker run -d -p 6379:6379 --name redis redis:7-alpine`

**Connection String**: `redis://localhost:6379/0`  
**Test**: `redis-cli ping` (should return `PONG`)

**Note**: App auto-tests Redis on startup. If unavailable, app runs but caching is disabled.

---

## 5. Environment Variables

### 5.1 Backend (.env in `backend/`)

**Required**:
```env
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/sectorradar
REDIS_URL=redis://localhost:6379/0
```

**Optional**:
```env
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
AUTO_REFRESH_INTERVAL=30
LOG_LEVEL=INFO
ENVIRONMENT=development
```

### 5.2 Frontend (.env in `frontend/`)

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

```bash
cd backend
pytest                                    # All tests
pytest --cov=app --cov-report=html       # With coverage (report in htmlcov/index.html)
pytest tests/test_database.py -v         # Specific file
pytest tests/test_api_stocks.py::TestGetStocks::test_get_stocks_empty -v  # Specific test
```

**Configuration**: `backend/pytest.ini` | **Test DB**: SQLite in-memory (auto cleanup)  
**Coverage Goals**: Phase 1-4: 80%+, Phase 5: 90%+ | **Current**: 88% ✅

### 8.2 Swagger UI Testing

**Access**: http://localhost:8000/docs (ReDoc: http://localhost:8000/redoc)

**Prerequisites**: DB initialized (`python -m app.database`), server running (`uvicorn app.main:app --reload`), Redis (optional)

**Steps**: Open Swagger UI → Click "Try it out" → Fill parameters → Execute → Review response

**Key Endpoints**: `/api/health`, `/api/stocks`, `/api/stocks/{ticker}`, `/api/prices/{ticker}`

**Troubleshooting**: Check server (`curl http://localhost:8000/api/health`), verify `.env`, seed data if needed

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

