## 1. Document Overview

### 1.1 Purpose
This document defines the technology stack selection, system architecture design, and development environment configuration for the K-SectorRadar project to provide system development standards.

### 1.2 Scope
This document includes technology stacks for frontend, backend, database, infrastructure, and overall system architecture.

---

## 2. Technology Stack

### 2.1 Frontend

#### 2.1.1 Framework/Library
- **React**: UI Framework
  - Version: 18.x or higher
  - Selection Reason: Component-based development, rich ecosystem, high productivity

- **TypeScript**: Type Safety
  - Version: 5.x or higher
  - Selection Reason: Type safety, improved development productivity, runtime error prevention

#### 2.1.2 State Management
- **React Query (TanStack Query)**: Server State Management
  - Version: 5.x or higher
  - Selection Reason: Caching, auto refresh, error handling, loading state management

- **Zustand** or **Context API**: Client State Management
  - Selection Reason: Simple state management, lightweight, low learning curve

#### 2.1.3 Routing
- **React Router**: Client-side Routing
  - Version: 6.x or higher
  - Selection Reason: Standard routing solution, wide community support

#### 2.1.4 UI Library
- **Tailwind CSS**: Utility-based CSS
  - Version: 3.x or higher
  - Selection Reason: Fast development, easy customization, consistent design system

- **Recharts** or **Chart.js**: Chart Library
  - Selection Reason: React-friendly, various chart types, responsive support

#### 2.1.5 Build Tool
- **Vite**: Build Tool
  - Version: 5.x or higher
  - Selection Reason: Fast development server, optimized build, HMR support

### 2.2 Backend

#### 2.2.1 Framework
- **Python FastAPI**: API Server
  - Version: 0.104.x or higher
  - Selection Reason: Fast performance, automatic API documentation, async support, type hinting

#### 2.2.2 Data Collection
- **BeautifulSoup4**: HTML Parsing
  - Version: 4.12.x or higher
  - Selection Reason: Simple web scraping, intuitive API

- **Selenium** (Optional): Dynamic Web Page Processing
  - Version: 4.x or higher
  - Selection Reason: Used when JavaScript rendering is required

- **Requests**: HTTP Client
  - Version: 2.31.x or higher
  - Selection Reason: Simple API calls, widely used library

#### 2.2.3 Scheduling
- **APScheduler**: Job Scheduling
  - Version: 3.10.x or higher
  - Selection Reason: Flexible scheduling, background jobs, various trigger support

#### 2.2.4 Database ORM
- **SQLAlchemy**: ORM
  - Version: 2.0.x or higher
  - Selection Reason: Powerful ORM, various DB support, migration support

#### 2.2.5 Data Validation
- **Pydantic**: Data Validation and Configuration Management
  - Version: 2.x or higher
  - Selection Reason: FastAPI integration, type validation, automatic documentation

### 2.3 Database

#### 2.3.1 Relational Database
- **MySQL**
  - Version: 8.0 or higher
  - Selection Reason: Stability, performance, rich features, scalability, wide adoption

#### 2.3.2 Cache
- **Redis**: In-Memory Cache
  - Version: 7.x or higher
  - Selection Reason: Fast speed, various data structures, session management support

### 2.4 Development Tools

#### 2.4.1 Version Control
- **Git**: Version Control
- **GitHub**: Code Repository

#### 2.4.2 Package Management
- **npm** or **yarn**: Frontend Package Management
- **pip**: Backend Package Management
- **Poetry** (Optional): Python Dependency Management

#### 2.4.3 Code Quality
- **ESLint**: JavaScript/TypeScript Linter
- **Prettier**: Code Formatter
- **Black**: Python Code Formatter
- **Pylint**: Python Linter

#### 2.4.4 Testing
- **Jest**: Frontend Testing
- **React Testing Library**: React Component Testing
- **pytest**: Backend Testing

---

## 3. System Architecture

### 3.1 Overall Architecture Overview
The system is based on a 3-layer architecture (Presentation, Application, Data Layer), and Frontend and Backend communicate through **REST API**.

### 3.2 Overall Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    Client Layer                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  React + TypeScript + Tailwind CSS               │   │
│  │  - Dashboard, Detail, Comparison, Settings      │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          │
                    HTTP/REST API
                          │
┌─────────────────────────────────────────────────────────┐
│                   Application Layer                      │
│  ┌──────────────────────────────────────────────────┐   │
│  │  FastAPI Server                                  │   │
│  │  - REST API Endpoints                            │   │
│  │  - Business Logic                                │   │
│  │  - Data Service                                  │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
┌───────▼──────┐  ┌───────▼──────┐  ┌───────▼──────┐
│   Database   │  │  Redis Cache  │  │ Data Collector│
│    (MySQL)   │  │               │  │  (Scheduler) │
│             │  │               │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
                          │
                          │
┌─────────────────────────────────────────────────────────┐
│              External Data Sources                       │
│  ┌──────────────┐  ┌──────────────┐                    │
│  │Naver Finance │  │ Naver News   │                    │
│  └──────────────┘  └──────────────┘                    │
└─────────────────────────────────────────────────────────┘
```

### 3.3 Layer Structure

#### 3.3.1 Presentation Layer
- User interface components
- Routing management
- State management (client state and server state)
- API calls
- User interaction handling

#### 3.3.2 Application Layer
- Business logic processing
- REST API endpoint provision
- Data transformation and processing
- Request/response processing
- Authentication and authorization management (future expansion)

#### 3.3.3 Data Layer
- Database access (using ORM)
- Cache management (Redis)
- External API calls
- Data validation and storage
- Scheduled data collection

### 3.4 Frontend Architecture

```
src/
├── components/          # Reusable components
│   ├── common/         # Common components
│   │   ├── Header.tsx
│   │   ├── SortFilter.tsx
│   │   └── AutoRefreshToggle.tsx
│   ├── stock/          # Stock-related components
│   │   └── StockCard.tsx
│   └── chart/          # Chart components
│       └── MiniChart.tsx
├── pages/              # Page components
│   ├── Dashboard.tsx
│   ├── Detail.tsx
│   ├── Comparison.tsx
│   └── Settings.tsx
├── hooks/              # Custom hooks
├── services/           # API services
│   └── apiClient.ts
├── utils/              # Utility functions
│   ├── dateFormatter.ts
│   └── numberFormatter.ts
├── types/              # TypeScript type definitions
├── store/              # State management
└── styles/             # Style files
```

### 3.5 Backend Architecture

```
backend/
├── app/
│   ├── api/            # API routers
│   │   ├── stocks.py
│   │   ├── prices.py
│   │   ├── trading.py
│   │   └── news.py
│   ├── models/         # Data models
│   ├── services/       # Business logic
│   │   └── data_service.py
│   ├── collectors/     # Data collectors
│   │   ├── finance.py
│   │   └── news.py
│   ├── schemas/        # Pydantic schemas
│   └── utils/          # Utilities
├── database/           # DB related
│   ├── models.py
│   └── connection.py
├── scheduler/          # Scheduler
│   └── tasks.py
└── main.py             # FastAPI app entry point
```

---

## 4. Development Environment Setup

### 4.1 Frontend Development Environment

#### 4.1.1 Prerequisites
- Node.js: 18.x or higher
- npm: 9.x or higher

#### 4.1.2 Project Initialization
```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
```

#### 4.1.3 Main Package Installation
```bash
npm install react-router-dom
npm install @tanstack/react-query
npm install zustand
npm install tailwindcss postcss autoprefixer
npm install recharts
```

### 4.2 Backend Development Environment

#### 4.2.1 Prerequisites
- Python: 3.10 or higher
- pip: Latest version

#### 4.2.2 Virtual Environment Setup
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

#### 4.2.3 Main Package Installation
```bash
pip install fastapi uvicorn
pip install sqlalchemy
pip install pymysql cryptography  # MySQL driver
pip install beautifulsoup4 requests
pip install apscheduler
pip install redis
pip install pydantic
```

### 4.3 Database Setup

#### 4.3.1 MySQL Installation and Setup
- Local Development: 
  - macOS: `brew install mysql && brew services start mysql`
  - Ubuntu/Debian: `sudo apt-get install mysql-server && sudo systemctl start mysql`
  - Docker: `docker run --name mysql -e MYSQL_ROOT_PASSWORD=password -d mysql:8.0`
- Production Environment: Cloud DB service or self-hosted server

#### 4.3.2 Database Creation
```bash
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

#### 4.3.3 Redis Installation and Setup
- Local Development: Docker recommended
- Production Environment: Cloud cache service or self-hosted server

---

## 5. Deployment Architecture

### 5.1 Development Environment
- Local development server
- Development database
- Development cache server

### 5.2 Production Environment (Recommended)

#### 5.2.1 Option 1: Cloud Platform
- **Vercel** or **Netlify**: Frontend deployment
- **Railway** or **Render**: Backend deployment
- **PlanetScale**, **AWS RDS**, or **Google Cloud SQL**: MySQL database
- **Upstash**: Redis cache

#### 5.2.2 Option 2: Self-Hosted Server
- **Nginx**: Reverse proxy
- **Gunicorn** or **Uvicorn**: ASGI server
- **Docker**: Containerization
- **Docker Compose**: Orchestration

### 5.3 CI/CD (Optional)
- **GitHub Actions**: Automated build and deployment
- Automatic test execution
- Automated deployment pipeline

---

## 6. Security Considerations

### 6.1 API Security
- CORS configuration
- Rate Limiting
- Input data validation (Pydantic)
- SQL Injection prevention (using ORM)

### 6.2 Data Security
- Environment variable management (.env)
- Database access control
- HTTPS usage
- Sensitive information encryption

### 6.3 Authentication and Authorization
- Initial version: No authentication (public service)
- Future expansion: User authentication system (JWT, etc.)

---

## 7. Performance Optimization

### 7.1 Frontend Optimization
- Code splitting
- Image optimization
- Bundle size optimization
- React Query caching utilization

### 7.2 Backend Optimization
- Database query optimization
- Caching strategy (Redis)
  - Real-time data: 30 seconds cache
  - Stock information: 1 hour cache
  - News data: 10 minutes cache
- Async processing
- Database index design

---

## 8. Monitoring and Logging

### 8.1 Logging
- Structured logging
- Log level management
- API request/response logs
- Error logs
- Data collection logs

### 8.2 Monitoring (Optional)
- **Sentry**: Error monitoring
- **Prometheus** + **Grafana**: Metric monitoring
- System resource monitoring
- API response time monitoring
- Data collection status monitoring

---

## 9. Scalability Considerations

### 9.1 Horizontal Scaling
- Stateless architecture
- Load balancing
- Distributed caching

### 9.2 Vertical Scaling
- Server resource expansion
- Database optimization
- Data partitioning (if needed)

---

## 10. Error Handling

### 10.1 Error Classification
- Client errors (4xx)
- Server errors (5xx)
- External API errors

### 10.2 Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error message"
  },
  "timestamp": "2025-11-13T21:23:43Z"
}
```

---

## 11. Data Flow

### 11.1 Data Collection Flow
```
1. Data Collector scheduler execution
2. External API call for each stock
3. Data validation and transformation
4. Database storage
5. Cache update
```

### 11.2 Data Retrieval Flow
```
1. User request
2. Frontend API call
3. Backend request processing
4. Cache check
5. Database query on cache miss
6. Data processing and return
7. Frontend rendering
```

---

