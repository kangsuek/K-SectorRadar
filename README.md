# K-SectorRadar

Korean high-growth sector analysis web application (improved version of ETFWeeklyReport)

## 📊 Project Overview

A web application that provides real-time monitoring, detailed analysis, and comparative analysis for Korean high-growth sector-related stocks (ETFs and stocks).

## 🎯 Key Features

- **Real-time Monitoring**: Automatic data refresh at 30-second intervals
- **Dashboard**: Card-based monitoring interface for each stock
- **Detailed Analysis**: Detailed information and chart analysis for each stock
- **Comparative Analysis**: Comparative analysis between multiple stocks
- **Settings Management**: System settings and stock management
- **Dark Mode**: Full dark mode support

## 📊 Initial Collection Targets

### 4 ETFs
1. **Samsung KODEX AI Power Core Equipment ETF** (487240) - AI & Power Infrastructure
2. **Shinhan SOL Shipbuilding TOP3 Plus ETF** (466920) - Shipbuilding
3. **KoAct Global Quantum Computing Active ETF** (0020H0) - Quantum Computing
4. **KB RISE Global Nuclear iSelect ETF** (442320) - Nuclear Power

### 2 Stocks
5. **Hanwha Ocean** (042660) - Shipbuilding/Defense
6. **Doosan Enerbility** (034020) - Energy/Power

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL (or MySQL)
- Redis 7.x+
- Docker & Docker Compose (optional)

### Run with Docker (Recommended)

```bash
docker-compose up -d
```

### Manual Setup

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Modify database and Redis settings in .env file
python -m app.database  # Initialize database
uvicorn app.main:app --reload
```
→ http://localhost:8000/docs

#### Frontend
```bash
cd frontend
npm install
npm run dev
```
→ http://localhost:5173

## 🔧 Technology Stack

### Backend
- **Framework**: FastAPI 0.104.x+
- **Database**: PostgreSQL/MySQL (production), SQLite (development)
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
- **Dark Mode**: Full support

## 📚 Documentation

- **[CLAUDE.md](./CLAUDE.md)** - Documentation index
- [Requirements Specification](./docs/eng/01-Requirements-Specification.md)
- [Technology Stack Specification](./docs/eng/02-System-Technology-Stack-Specification.md)
- [Data/API Design Specification](./docs/eng/03-Data-API-Design-Specification.md)
- [UI/UX Design Specification](./docs/eng/04-UI-UX-Design-Specification.md)

## 📖 Data Sources

- **Naver Finance**: Price data, investor trading trends
- **Naver News**: News data

## 🔄 Key Differences from ETFWeeklyReport

- ✅ TypeScript (improved type safety)
- ✅ PostgreSQL/MySQL support (instead of SQLite)
- ✅ Redis caching layer
- ✅ Enhanced dark mode support
- ✅ Better architecture and scalability
- ✅ Strict type checking

## 📝 License

MIT
