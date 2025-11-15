# Development Guide

> **Project**: K-SectorRadar
> **Version**: 1.0
> **Last Updated**: 2025-11-15

---

## Table of Contents

1. [Development Environment Requirements](#1-development-environment-requirements)
2. [Project Structure](#2-project-structure)
3. [Backend Setup](#3-backend-setup)
4. [Frontend Setup](#4-frontend-setup)
5. [Running Tests](#5-running-tests)
6. [API Documentation](#6-api-documentation)
7. [Development Workflow](#7-development-workflow)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. Development Environment Requirements

### 1.1 Required Software

- **Python**: 3.10 or higher
- **Node.js**: 18.x or higher
- **npm**: 9.x or higher (comes with Node.js)
- **MySQL**: 8.0 or higher (production and development)
- **Redis**: 7.x or higher
- **Git**: Latest version

### 1.2 Optional Software

- **Docker**: 20.x or higher (for containerized MySQL/Redis)
- **Docker Compose**: 1.29 or higher

### 1.3 Operating Systems

The project is compatible with:
- **macOS**: 10.15 (Catalina) or later
- **Linux**: Ubuntu 20.04+, Debian 11+, or equivalent
- **Windows**: 10/11 (with WSL2 recommended for best experience)

---

## 2. Project Structure

### 2.1 Root Directory Structure

```
K-SectorRadar/
├── backend/              # Backend (FastAPI)
│   ├── alembic/         # Database migrations
│   ├── app/             # Application code
│   ├── config/          # Configuration files
│   ├── scripts/         # Utility scripts
│   ├── tests/           # Test files
│   ├── requirements.txt # Python dependencies
│   └── .env.example     # Environment variables template
├── frontend/            # Frontend (React + TypeScript)
│   ├── src/            # Source code
│   ├── public/         # Static assets
│   ├── package.json    # Node.js dependencies
│   └── vite.config.ts  # Vite configuration
├── docs/               # Documentation
│   ├── eng/           # English documentation
│   └── project-management/ # Project management files
├── README.md          # Project README
└── docker-compose.yml # Docker Compose configuration (optional)
```

### 2.2 Backend Directory Structure

```
backend/
├── alembic/
│   ├── versions/          # Migration version files
│   ├── env.py            # Alembic environment
│   └── script.py.mako    # Migration template
├── app/
│   ├── api/              # API route handlers
│   │   ├── stocks.py    # Stock endpoints
│   │   ├── prices.py    # Price endpoints
│   │   ├── trading.py   # Trading trend endpoints
│   │   ├── news.py      # News endpoints
│   │   └── chart.py     # Chart endpoints
│   ├── models/           # SQLAlchemy models
│   │   ├── stock.py     # Stock model
│   │   ├── price.py     # Price model
│   │   ├── trading_trend.py  # Trading trend model
│   │   └── news.py      # News model
│   ├── schemas/          # Pydantic schemas
│   │   ├── stock.py     # Stock schemas
│   │   ├── price.py     # Price schemas
│   │   └── response.py  # Common response schemas
│   ├── utils/            # Utility functions
│   │   ├── cache.py     # Caching utilities
│   │   └── redis.py     # Redis client
│   ├── config.py         # Application configuration
│   ├── database.py       # Database setup
│   ├── exceptions.py     # Custom exceptions
│   ├── db_base.py        # SQLAlchemy base
│   └── main.py           # Application entry point
├── config/
│   └── stocks.json       # Initial stock data
├── scripts/
│   ├── seed_stocks.py    # Seed database script
│   └── run_migrations.py # Migration runner
└── tests/
    ├── conftest.py       # pytest configuration
    ├── test_database.py  # Database tests
    ├── test_cache.py     # Cache tests
    ├── test_api_*.py     # API tests
    └── test_integration.py # Integration tests
```

---

## 3. Backend Setup

### 3.1 Clone the Repository

```bash
git clone https://github.com/your-org/K-SectorRadar.git
cd K-SectorRadar
```

### 3.2 Create Python Virtual Environment

#### macOS/Linux

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

#### Windows (Command Prompt)

```cmd
cd backend
python -m venv venv
venv\Scripts\activate
```

#### Windows (PowerShell)

```powershell
cd backend
python -m venv venv
venv\Scripts\Activate.ps1
```

**Note**: If you encounter a PowerShell execution policy error, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3.3 Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Required Packages** (from `requirements.txt`):
- **FastAPI**: 0.104.1 - Web framework
- **Uvicorn**: 0.24.0 - ASGI server
- **Pydantic**: 2.5.0 - Data validation
- **SQLAlchemy**: 2.0.23 - ORM
- **Alembic**: 1.12.1 - Database migrations
- **PyMySQL**: 1.1.0 - MySQL driver
- **Redis**: 5.0.1 - Redis client
- **Requests**: 2.31.0 - HTTP client
- **BeautifulSoup4**: 4.12.2 - HTML parsing

### 3.4 Configure Environment Variables

#### Step 1: Copy Environment Template

```bash
cp .env.example .env
```

#### Step 2: Edit `.env` File

Open `.env` in your favorite text editor and configure the following:

```bash
# Database Configuration
# MySQL (recommended for development and production)
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/sectorradar

# OR SQLite (for local testing only)
# DATABASE_URL=sqlite:///./data/sectorradar.db

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Data Collection Settings
AUTO_REFRESH_INTERVAL=30
NAVER_FINANCE_BASE_URL=https://finance.naver.com
NAVER_NEWS_BASE_URL=https://search.naver.com

# Logging
LOG_LEVEL=INFO

# Environment (development or production)
ENVIRONMENT=development

# Naver API (optional, for news collection)
# Get your credentials from https://developers.naver.com
NAVER_CLIENT_ID=your_client_id_here
NAVER_CLIENT_SECRET=your_client_secret_here
```

**Important Notes**:
- Replace `username` and `password` with your MySQL credentials
- Never commit the `.env` file to Git (it's already in `.gitignore`)
- Naver API credentials are optional for Phase 1 but required for Phase 2 news collection

### 3.5 Database Setup

#### Option A: MySQL (Recommended)

##### Step 1: Install MySQL

**macOS** (using Homebrew):
```bash
brew install mysql@8.0
brew services start mysql@8.0
```

**Ubuntu/Debian**:
```bash
sudo apt update
sudo apt install mysql-server
sudo systemctl start mysql
sudo systemctl enable mysql
```

**Windows**:
- Download MySQL Installer from [https://dev.mysql.com/downloads/installer/](https://dev.mysql.com/downloads/installer/)
- Follow the installation wizard

##### Step 2: Create Database

```bash
# Connect to MySQL
mysql -u root -p

# In MySQL prompt:
CREATE DATABASE sectorradar CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

##### Step 3: Run Migrations

```bash
# From backend directory
python scripts/run_migrations.py
```

Or manually with Alembic:
```bash
alembic upgrade head
```

##### Step 4: Seed Initial Data

```bash
python scripts/seed_stocks.py
```

This will populate the database with initial stock data from `config/stocks.json`.

#### Option B: SQLite (Development/Testing Only)

##### Step 1: Update `.env`

```bash
DATABASE_URL=sqlite:///./data/sectorradar.db
```

##### Step 2: Create Data Directory

```bash
mkdir -p data
```

##### Step 3: Initialize Database

```bash
python -m app.database
```

##### Step 4: Seed Initial Data

```bash
python scripts/seed_stocks.py
```

**Note**: SQLite is suitable for development and testing but not recommended for production due to concurrency limitations.

### 3.6 Redis Setup

#### Option A: Docker (Recommended)

```bash
docker run -d \
  --name redis-sectorradar \
  -p 6379:6379 \
  redis:7-alpine
```

To stop Redis:
```bash
docker stop redis-sectorradar
```

To start Redis again:
```bash
docker start redis-sectorradar
```

#### Option B: Local Installation

**macOS** (using Homebrew):
```bash
brew install redis
brew services start redis
```

**Ubuntu/Debian**:
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

**Windows**:
- Download Redis for Windows from [https://github.com/tporadowski/redis/releases](https://github.com/tporadowski/redis/releases)
- Extract and run `redis-server.exe`

#### Verify Redis Connection

```bash
redis-cli ping
# Expected output: PONG
```

### 3.7 Run the Backend Server

#### Development Mode (with auto-reload)

```bash
# From backend directory
uvicorn app.main:app --reload
```

The server will start at:
- **API Base**: [http://localhost:8000](http://localhost:8000)
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

#### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### With Custom Host/Port

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

---

## 4. Frontend Setup

**Note**: Frontend implementation is planned for Phase 3. This section will be updated when frontend development begins.

### 4.1 Install Node.js Dependencies

```bash
cd frontend
npm install
```

### 4.2 Run Development Server

```bash
npm run dev
```

The frontend will start at: [http://localhost:5173](http://localhost:5173)

---

## 5. Running Tests

### 5.1 Prerequisites

Ensure you have:
- Python virtual environment activated
- Database configured (MySQL or SQLite)
- Redis running

### 5.2 Install Test Dependencies

Test dependencies are included in `requirements.txt`. If not already installed:

```bash
pip install pytest pytest-cov pytest-asyncio httpx
```

### 5.3 Run All Tests

```bash
# From backend directory
pytest tests/ -v
```

**Expected Output**:
```
tests/test_api_health.py::test_health_check PASSED
tests/test_api_prices.py::test_get_price_success PASSED
tests/test_api_stocks.py::test_get_stocks PASSED
...
========================= 20 passed in 5.23s =========================
```

### 5.4 Run Tests with Coverage

```bash
pytest --cov=app --cov-report=html tests/
```

This generates an HTML coverage report in `htmlcov/index.html`. Open it in your browser:

```bash
# macOS
open htmlcov/index.html

# Linux
xdg-open htmlcov/index.html

# Windows
start htmlcov/index.html
```

### 5.5 Run Specific Test Files

```bash
# Test only stock API
pytest tests/test_api_stocks.py -v

# Test only caching
pytest tests/test_cache.py -v

# Test only database
pytest tests/test_database.py -v
```

### 5.6 Run Tests with Verbose Output

```bash
pytest tests/ -vv
```

### 5.7 Target Coverage

- **Phase 1 Goal**: 80% code coverage
- **Final Goal**: 90% code coverage

---

## 6. API Documentation

### 6.1 Swagger UI (Interactive)

Visit [http://localhost:8000/docs](http://localhost:8000/docs) after starting the backend server.

**Features**:
- Interactive API testing
- Try out endpoints directly from the browser
- View request/response schemas
- See example requests and responses

### 6.2 ReDoc (Alternative)

Visit [http://localhost:8000/redoc](http://localhost:8000/redoc) for a cleaner, read-only API documentation.

### 6.3 Testing Endpoints with Swagger UI

#### Step 1: Open Swagger UI

Navigate to [http://localhost:8000/docs](http://localhost:8000/docs)

#### Step 2: Expand an Endpoint

Click on any endpoint (e.g., `GET /api/stocks`)

#### Step 3: Click "Try it out"

This enables the interactive form.

#### Step 4: Fill in Parameters

Enter any required or optional parameters.

#### Step 5: Click "Execute"

The API request will be sent and the response displayed below.

### 6.4 Testing Endpoints with curl

```bash
# Health check
curl -X GET "http://localhost:8000/api/health"

# Get all stocks
curl -X GET "http://localhost:8000/api/stocks"

# Get stock detail
curl -X GET "http://localhost:8000/api/stocks/034020"

# Get price data with date range
curl -X GET "http://localhost:8000/api/prices/034020?start_date=2025-01-01&end_date=2025-12-31"
```

---

## 7. Development Workflow

### 7.1 Code Style Guidelines

#### Python (Backend)

The project follows PEP 8 style guidelines.

**Tools**:
- **Black**: Code formatter (line length: 100)
- **Flake8**: Linter
- **isort**: Import sorter

**Install Formatting Tools**:
```bash
pip install black flake8 isort
```

**Format Code**:
```bash
# Format with Black
black app/ tests/

# Sort imports
isort app/ tests/

# Lint with Flake8
flake8 app/ tests/
```

#### TypeScript (Frontend - Phase 3)

- **ESLint**: Linter
- **Prettier**: Code formatter

### 7.2 Git Workflow

#### Branch Naming Convention

- `feature/` - New features (e.g., `feature/user-authentication`)
- `bugfix/` - Bug fixes (e.g., `bugfix/price-calculation`)
- `hotfix/` - Urgent production fixes
- `docs/` - Documentation updates
- `test/` - Test additions/improvements

#### Commit Message Format

Follow the Conventional Commits specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, missing semicolons, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples**:
```
feat(api): add stock filtering by theme

Add query parameter 'theme' to GET /api/stocks endpoint
to allow filtering stocks by investment theme.

Closes #123
```

```
fix(cache): correct TTL calculation for price data

The cache TTL was incorrectly set to 30 seconds instead
of 30 minutes (1800 seconds).

Fixes #124
```

### 7.3 Pull Request Process

1. Create a feature branch from `main`
2. Make your changes and commit
3. Write or update tests for your changes
4. Ensure all tests pass (`pytest tests/ -v`)
5. Push your branch to the repository
6. Create a Pull Request on GitHub
7. Request code review from team members
8. Address review comments
9. Merge after approval

### 7.4 Testing Before Committing

Always run tests before committing:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest --cov=app tests/

# Ensure coverage is above 80% for Phase 1
```

---

## 8. Troubleshooting

### 8.1 Database Connection Errors

#### Problem: "Can't connect to MySQL server"

**Solution**:
1. Ensure MySQL is running:
   ```bash
   # macOS
   brew services list

   # Linux
   sudo systemctl status mysql
   ```

2. Check credentials in `.env`:
   ```bash
   DATABASE_URL=mysql+pymysql://username:password@localhost:3306/sectorradar
   ```

3. Verify the database exists:
   ```bash
   mysql -u root -p
   SHOW DATABASES;
   ```

#### Problem: "Access denied for user"

**Solution**:
1. Reset MySQL password:
   ```bash
   # macOS
   mysql_secure_installation

   # Linux
   sudo mysql_secure_installation
   ```

2. Create a new user with proper privileges:
   ```sql
   CREATE USER 'sectorradar'@'localhost' IDENTIFIED BY 'your_password';
   GRANT ALL PRIVILEGES ON sectorradar.* TO 'sectorradar'@'localhost';
   FLUSH PRIVILEGES;
   ```

3. Update `.env` with new credentials.

### 8.2 Redis Connection Errors

#### Problem: "Error connecting to Redis"

**Solution**:
1. Check if Redis is running:
   ```bash
   redis-cli ping
   # Expected: PONG
   ```

2. Start Redis if not running:
   ```bash
   # Docker
   docker start redis-sectorradar

   # macOS
   brew services start redis

   # Linux
   sudo systemctl start redis-server
   ```

3. Verify `REDIS_URL` in `.env`:
   ```bash
   REDIS_URL=redis://localhost:6379/0
   ```

#### Problem: "Redis connection timeout"

**Solution**:
1. Check Redis configuration file:
   ```bash
   # macOS
   cat /usr/local/etc/redis.conf | grep bind

   # Linux
   cat /etc/redis/redis.conf | grep bind
   ```

2. Ensure `bind 127.0.0.1` is set (for local development).

### 8.3 Port Already in Use

#### Problem: "Address already in use" (port 8000)

**Solution**:
1. Find the process using port 8000:
   ```bash
   # macOS/Linux
   lsof -i :8000

   # Windows
   netstat -ano | findstr :8000
   ```

2. Kill the process:
   ```bash
   # macOS/Linux
   kill -9 <PID>

   # Windows
   taskkill /PID <PID> /F
   ```

3. Or use a different port:
   ```bash
   uvicorn app.main:app --port 8080 --reload
   ```

### 8.4 Migration Errors

#### Problem: "Target database is not up to date"

**Solution**:
1. Check current migration version:
   ```bash
   alembic current
   ```

2. Upgrade to the latest version:
   ```bash
   alembic upgrade head
   ```

#### Problem: "Can't locate revision identified by '<hash>'"

**Solution**:
1. Delete all migration files except `__init__.py`:
   ```bash
   rm backend/alembic/versions/*.py
   ```

2. Recreate the initial migration:
   ```bash
   alembic revision --autogenerate -m "Initial schema"
   ```

3. Apply the migration:
   ```bash
   alembic upgrade head
   ```

### 8.5 Python Import Errors

#### Problem: "ModuleNotFoundError: No module named 'app'"

**Solution**:
1. Ensure virtual environment is activated:
   ```bash
   # You should see (venv) in your prompt
   source venv/bin/activate
   ```

2. Reinstall dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run commands from the `backend/` directory:
   ```bash
   cd backend
   python -m app.database
   ```

### 8.6 Test Failures

#### Problem: Tests fail with database errors

**Solution**:
1. Ensure test database is configured:
   ```bash
   # tests/conftest.py uses SQLite in-memory database by default
   # No additional configuration needed
   ```

2. Run tests with verbose output to see detailed errors:
   ```bash
   pytest tests/ -vv
   ```

#### Problem: Cache tests fail

**Solution**:
1. Ensure Redis is running:
   ```bash
   redis-cli ping
   ```

2. Clear Redis cache before testing:
   ```bash
   redis-cli FLUSHALL
   ```

### 8.7 Performance Issues

#### Problem: API responses are slow

**Solution**:
1. Check database query performance:
   ```bash
   # Enable SQLAlchemy query logging in app/config.py
   # Set LOG_LEVEL=DEBUG in .env
   ```

2. Verify Redis caching is working:
   ```bash
   redis-cli MONITOR
   # Should show GET/SET operations
   ```

3. Check database indexes:
   ```sql
   SHOW INDEX FROM prices;
   SHOW INDEX FROM stocks;
   ```

### 8.8 Common Windows-Specific Issues

#### Problem: "pip" is not recognized

**Solution**:
```cmd
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

#### Problem: MySQL not starting on Windows

**Solution**:
1. Open Services (Win + R → `services.msc`)
2. Find "MySQL80" service
3. Right-click → Start

#### Problem: Redis not available on Windows

**Solution**:
Use Docker Desktop for Windows or WSL2 (Windows Subsystem for Linux):
```bash
# In WSL2
docker run -d --name redis -p 6379:6379 redis:7-alpine
```

---

## Appendix

### A. Useful Commands Cheatsheet

#### Database

```bash
# Create database
mysql -u root -p
CREATE DATABASE sectorradar CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Run migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Seed database
python scripts/seed_stocks.py
```

#### Redis

```bash
# Start Redis (Docker)
docker start redis-sectorradar

# Connect to Redis CLI
redis-cli

# Check connection
redis-cli ping

# Clear all cache
redis-cli FLUSHALL
```

#### Backend

```bash
# Activate venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn app.main:app --reload

# Run tests
pytest tests/ -v

# Check coverage
pytest --cov=app --cov-report=html tests/
```

### B. Environment Variables Reference

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `DATABASE_URL` | string | - | Database connection string |
| `REDIS_URL` | string | `redis://localhost:6379/0` | Redis connection string |
| `API_HOST` | string | `0.0.0.0` | API host address |
| `API_PORT` | integer | `8000` | API port number |
| `API_RELOAD` | boolean | `true` | Enable auto-reload |
| `CORS_ORIGINS` | string | `http://localhost:5173,...` | Allowed CORS origins (comma-separated) |
| `AUTO_REFRESH_INTERVAL` | integer | `30` | Data refresh interval (seconds) |
| `LOG_LEVEL` | string | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `ENVIRONMENT` | string | `development` | Environment mode |
| `NAVER_CLIENT_ID` | string | - | Naver API client ID (optional) |
| `NAVER_CLIENT_SECRET` | string | - | Naver API client secret (optional) |

### C. Related Documentation

- **[DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md)** - Database schema documentation
- **[API_SPECIFICATION.md](./API_SPECIFICATION.md)** - API specification
- **[README.md](../../README.md)** - Project overview
- **[TODO.md](../project-management/TODO.md)** - Project task list

---

**Document Version**: 1.0
**Author**: K-SectorRadar Development Team
**Last Updated**: 2025-11-15
