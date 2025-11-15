# K-SectorRadar Development Guide

## Table of Contents
1. [Development Environment Setup](#1-development-environment-setup)
2. [Database Configuration](#2-database-configuration)
3. [Redis Configuration](#3-redis-configuration)
4. [Running the Application](#4-running-the-application)
5. [Testing](#5-testing)
6. [Database Migrations](#6-database-migrations)
7. [API Documentation](#7-api-documentation)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. Development Environment Setup

### 1.1 Prerequisites

- **Python**: 3.10 or higher
- **Node.js**: 18.x or higher
- **MySQL**: 8.0 or higher
- **Redis**: 7.x or higher
- **Git**: For version control

### 1.2 Clone Repository

```bash
git clone <repository-url>
cd K-SectorRadar
```

### 1.3 Backend Setup

#### Create Virtual Environment

```bash
cd backend
python -m venv venv

# On macOS/Linux
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

#### Install Dependencies

```bash
# Production dependencies
pip install -r requirements.txt

# Development dependencies (includes testing tools)
pip install -r requirements-dev.txt
```

### 1.4 Frontend Setup

```bash
cd frontend
npm install
```

---

## 2. Database Configuration

### 2.1 MySQL Installation

#### macOS
```bash
brew install mysql@8.0
brew services start mysql
```

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install mysql-server
sudo systemctl start mysql
sudo systemctl enable mysql
```

#### Windows
Download and install MySQL from [MySQL Official Website](https://dev.mysql.com/downloads/mysql/)

### 2.2 Database Creation

```bash
# Connect to MySQL
mysql -u root -p

# Create database
CREATE DATABASE sectorradar CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Create user (optional, recommended for production)
CREATE USER 'sectorradar'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON sectorradar.* TO 'sectorradar'@'localhost';
FLUSH PRIVILEGES;

# Exit MySQL
EXIT;
```

### 2.3 Environment Variables

Create a `.env` file in the `backend` directory:

```bash
# Copy example file
cp .env.example .env
```

Edit `.env` and configure the database URL:

```env
# MySQL Configuration (Recommended)
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/sectorradar

# Or with custom user
# DATABASE_URL=mysql+pymysql://sectorradar:your_secure_password@localhost:3306/sectorradar

# PostgreSQL (Alternative)
# DATABASE_URL=postgresql://user:password@localhost:5432/sectorradar

# SQLite (For testing only, not recommended for production)
# DATABASE_URL=sqlite:///./data/sectorradar.db
```

### 2.4 Database Initialization

#### Method 1: Direct Execution (Recommended)

```bash
cd backend
python -m app.database
```

This will:
- Create all tables based on SQLAlchemy models
- Load initial stock data from `config/stocks.json`

#### Method 2: Alembic Migrations

```bash
# Generate initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head

# Load seed data
python scripts/seed_stocks.py
```

### 2.5 Database Schema

The following tables will be created:

1. **stocks** - Stock/ETF information
2. **prices** - Price data
3. **trading_trends** - Trading trend data
4. **news** - News data

See [03-Data-API-Design-Specification.md](./03-Data-API-Design-Specification.md) for detailed schema.

---

## 3. Redis Configuration

### 3.1 Redis Installation

#### macOS
```bash
brew install redis
brew services start redis
```

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

#### Windows
Download Redis from [Redis Windows Download](https://github.com/microsoftarchive/redis/releases) or use WSL.

### 3.2 Redis Configuration

Add Redis URL to `.env` file:

```env
# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# For Redis with password
# REDIS_URL=redis://:password@localhost:6379/0

# For Redis on different host
# REDIS_URL=redis://remote-host:6379/0
```

### 3.3 Verify Redis Connection

```bash
# Test Redis connection
redis-cli ping
# Expected output: PONG

# Check Redis info
redis-cli info
```

### 3.4 Redis Usage in Application

Redis is used for caching in the application:

- **Stock List Cache**: TTL 1 hour
- **Stock Detail Cache**: TTL 1 hour
- **Price Data Cache**: TTL 30 minutes

Cache keys follow the pattern: `stocks:list:*`, `stocks:detail:{ticker}`, `prices:{ticker}:*`

### 3.5 Redis Management

```bash
# Clear all cache (use with caution in production)
redis-cli FLUSHDB

# Clear specific pattern
redis-cli KEYS "stocks:*" | xargs redis-cli DEL

# Monitor cache in real-time
redis-cli MONITOR
```

---

## 4. Running the Application

### 4.1 Backend Server

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 4.2 Frontend Development Server

```bash
cd frontend
npm run dev
```

The frontend will be available at:
- **Frontend**: http://localhost:5173

### 4.3 Docker Compose (Recommended for Development)

```bash
# Start all services (backend, frontend, MySQL, Redis)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild services
docker-compose up -d --build
```

---

## 5. Testing

### 5.1 Backend Testing

```bash
cd backend

# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html --cov-report=term-missing

# Run specific test file
pytest tests/test_api_stocks.py

# Run tests in verbose mode
pytest -v

# Run tests matching a pattern
pytest -k "test_get_stocks"
```

### 5.2 Test Coverage

View HTML coverage report:

```bash
# After running pytest with --cov-report=html
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

**Phase 1 Coverage Goal**: 80%+
**Final Coverage Goal**: 90%+

### 5.3 Frontend Testing

```bash
cd frontend

# Run unit tests
npm test

# Run tests with coverage
npm run test:coverage

# Run E2E tests (if configured)
npm run test:e2e
```

---

## 6. Database Migrations

### 6.1 Alembic Commands

```bash
cd backend

# Check current migration
alembic current

# View migration history
alembic history

# Create new migration (after model changes)
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>
```

### 6.2 Using Migration Scripts

```bash
# Upgrade to latest
python scripts/run_migrations.py upgrade

# Create new revision
python scripts/run_migrations.py revision "Add new column"
```

### 6.3 Best Practices

1. **Always review auto-generated migrations** before applying
2. **Test migrations on development database first**
3. **Backup production database** before running migrations
4. **Never edit applied migrations** - create new ones instead

---

## 7. API Documentation

### 7.1 Swagger UI

Visit http://localhost:8000/docs after starting the backend server.

Features:
- Interactive API documentation
- Test API endpoints directly
- View request/response schemas
- Download OpenAPI specification

### 7.2 ReDoc

Visit http://localhost:8000/redoc for alternative documentation view.

### 7.3 API Specification

See [03-Data-API-Design-Specification.md](./03-Data-API-Design-Specification.md) for complete API specification.

### 7.4 Phase 1 Implemented Endpoints

✅ **Implemented:**
- `GET /api/health` - Health check
- `GET /api/stocks` - List all stocks
- `GET /api/stocks/{ticker}` - Get stock details
- `GET /api/prices/{ticker}` - Get price data

⏸️ **Planned for Phase 2:**
- `GET /api/stocks/{ticker}/trading` - Trading trends
- `GET /api/stocks/{ticker}/news` - News data
- `GET /api/stocks/{ticker}/chart` - Chart data
- `POST /api/refresh` - Data refresh

---

## 8. Troubleshooting

### 8.1 Database Connection Issues

**Problem**: `sqlalchemy.exc.OperationalError: (2003, "Can't connect to MySQL server")`

**Solutions**:
1. Check if MySQL is running: `mysql.server status` or `systemctl status mysql`
2. Verify DATABASE_URL in `.env` file
3. Check MySQL credentials
4. Ensure database exists: `SHOW DATABASES;`

### 8.2 Redis Connection Issues

**Problem**: Application warns "Redis connection failed"

**Solutions**:
1. Check if Redis is running: `redis-cli ping`
2. Verify REDIS_URL in `.env` file
3. Check Redis logs: `redis-cli info`
4. Restart Redis: `brew services restart redis` or `systemctl restart redis-server`

### 8.3 Port Already in Use

**Problem**: `OSError: [Errno 48] Address already in use`

**Solutions**:
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use different port
uvicorn app.main:app --reload --port 8001
```

### 8.4 Migration Errors

**Problem**: `alembic.util.exc.CommandError: Can't locate revision`

**Solutions**:
1. Check alembic version table: `SELECT * FROM alembic_version;`
2. Reset migrations (development only):
   ```bash
   alembic downgrade base
   rm -rf alembic/versions/*
   alembic revision --autogenerate -m "Initial migration"
   alembic upgrade head
   ```

### 8.5 Import Errors

**Problem**: `ModuleNotFoundError: No module named 'app'`

**Solutions**:
1. Ensure virtual environment is activated
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Run from correct directory: `cd backend`
4. Add to PYTHONPATH: `export PYTHONPATH="${PYTHONPATH}:$(pwd)"`

### 8.6 Cache Issues

**Problem**: Stale data being returned

**Solutions**:
```bash
# Clear Redis cache
redis-cli FLUSHDB

# Or clear specific keys
redis-cli KEYS "stocks:*" | xargs redis-cli DEL
```

---

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Redis Documentation](https://redis.io/documentation)
- [Pytest Documentation](https://docs.pytest.org/)

---

**Last Updated**: 2025-11-15 (Phase 1.6)
