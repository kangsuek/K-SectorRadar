# Database Schema Documentation

> **Project**: K-SectorRadar
> **Version**: 1.0
> **Last Updated**: 2025-11-15

---

## Table of Contents

1. [Database Overview](#1-database-overview)
2. [Table Schemas](#2-table-schemas)
3. [Entity Relationship Diagram](#3-entity-relationship-diagram)
4. [Indexing Strategy](#4-indexing-strategy)
5. [Migration Guide](#5-migration-guide)

---

## 1. Database Overview

### 1.1 Database Management System

- **Production DBMS**: MySQL 8.0+
- **Development DBMS**: SQLite 3.x (for local development)
- **ORM**: SQLAlchemy 2.0+
- **Migration Tool**: Alembic

### 1.2 Database Configuration

- **Character Encoding**: UTF-8 (utf8mb4 for MySQL)
- **Collation**: utf8mb4_unicode_ci (MySQL)
- **Timezone**: UTC
- **Connection Pooling**: Enabled (SQLAlchemy pool)

### 1.3 Naming Conventions

- **Tables**: Lowercase with underscores (e.g., `trading_trends`)
- **Columns**: Lowercase with underscores (e.g., `current_price`)
- **Indexes**: Prefix with `idx_` (e.g., `idx_ticker_date`)
- **Unique Constraints**: Prefix with `uk_` (e.g., `uk_url`)
- **Foreign Keys**: Prefix with `fk_` (implicit in SQLAlchemy)

---

## 2. Table Schemas

### 2.1 stocks

The `stocks` table stores information about stocks and ETFs.

#### 2.1.1 Table Structure

| Column | Type | Nullable | Default | Constraints | Description |
|--------|------|----------|---------|-------------|-------------|
| `ticker` | VARCHAR(10) | NO | - | PRIMARY KEY | Stock ticker code (unique identifier) |
| `name` | VARCHAR(100) | NO | - | - | Stock or ETF name |
| `type` | VARCHAR(10) | NO | - | CHECK IN ('STOCK', 'ETF') | Type of security |
| `theme` | VARCHAR(200) | YES | NULL | - | Investment theme or sector |
| `fee` | DECIMAL(10, 6) | YES | NULL | - | Management fee (ETF only) |
| `created_at` | DATETIME | NO | CURRENT_TIMESTAMP | - | Record creation timestamp |
| `updated_at` | DATETIME | NO | CURRENT_TIMESTAMP | ON UPDATE | Last update timestamp |

#### 2.1.2 Indexes

- **Primary Key**: `ticker`
- **Index**: `idx_type` on `type` - For filtering by stock type
- **Index**: `idx_theme` on `theme` - For filtering by theme

#### 2.1.3 Constraints

- **CHECK**: `type IN ('STOCK', 'ETF')` - Ensures type is either STOCK or ETF

#### 2.1.4 SQLAlchemy Model

```python
from sqlalchemy import Column, String, Numeric, DateTime, CheckConstraint, Index
from sqlalchemy.sql import func
from app.db_base import Base

class Stock(Base):
    """Stock information table"""

    __tablename__ = "stocks"

    ticker = Column(String(10), primary_key=True, comment="Stock ticker code")
    name = Column(String(100), nullable=False, comment="Stock or ETF name")
    type = Column(String(10), nullable=False, comment="Type (STOCK/ETF)")
    theme = Column(String(200), nullable=True, comment="Investment theme")
    fee = Column(Numeric(10, 6), nullable=True, comment="Management fee (ETF only)")
    created_at = Column(DateTime, default=func.now(), nullable=False, comment="Creation timestamp")
    updated_at = Column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Update timestamp",
    )

    __table_args__ = (
        CheckConstraint("type IN ('STOCK', 'ETF')", name="check_type"),
        Index("idx_type", "type"),
        Index("idx_theme", "theme"),
    )
```

#### 2.1.5 CREATE TABLE SQL (MySQL)

```sql
CREATE TABLE stocks (
    ticker VARCHAR(10) PRIMARY KEY COMMENT 'Stock ticker code',
    name VARCHAR(100) NOT NULL COMMENT 'Stock or ETF name',
    type VARCHAR(10) NOT NULL COMMENT 'Type (STOCK/ETF)',
    theme VARCHAR(200) DEFAULT NULL COMMENT 'Investment theme',
    fee DECIMAL(10, 6) DEFAULT NULL COMMENT 'Management fee (ETF only)',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation timestamp',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update timestamp',
    CONSTRAINT check_type CHECK (type IN ('STOCK', 'ETF')),
    INDEX idx_type (type),
    INDEX idx_theme (theme)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

### 2.2 prices

The `prices` table stores historical and real-time price data for stocks and ETFs.

#### 2.2.1 Table Structure

| Column | Type | Nullable | Default | Constraints | Description |
|--------|------|----------|---------|-------------|-------------|
| `id` | BIGINT | NO | AUTO_INCREMENT | PRIMARY KEY | Unique record ID |
| `ticker` | VARCHAR(10) | NO | - | FOREIGN KEY | Stock ticker code |
| `date` | DATE | NO | - | - | Trading date |
| `timestamp` | DATETIME | NO | - | - | Data collection timestamp |
| `current_price` | DECIMAL(12, 2) | NO | - | - | Current/closing price |
| `change_rate` | DECIMAL(6, 2) | YES | NULL | - | Price change rate (%) |
| `change_amount` | DECIMAL(12, 2) | YES | NULL | - | Price change amount |
| `open_price` | DECIMAL(12, 2) | YES | NULL | - | Opening price |
| `high_price` | DECIMAL(12, 2) | YES | NULL | - | Highest price |
| `low_price` | DECIMAL(12, 2) | YES | NULL | - | Lowest price |
| `volume` | DECIMAL(20, 0) | YES | NULL | - | Trading volume |
| `weekly_change_rate` | DECIMAL(6, 2) | YES | NULL | - | Weekly change rate (%) |
| `previous_close` | DECIMAL(12, 2) | YES | NULL | - | Previous day's closing price |

#### 2.2.2 Indexes

- **Primary Key**: `id` (auto-increment)
- **Index**: `idx_ticker_date` on `(ticker, date)` - For querying price data by ticker and date range
- **Index**: `idx_ticker_timestamp` on `(ticker, timestamp)` - For querying latest price data

#### 2.2.3 Foreign Keys

- **Foreign Key**: `ticker` REFERENCES `stocks(ticker)` ON DELETE CASCADE

#### 2.2.4 SQLAlchemy Model

```python
from sqlalchemy import Column, BigInteger, String, Numeric, DateTime, Date, ForeignKey, Index
from sqlalchemy.sql import func
from app.db_base import Base

class Price(Base):
    """Price data table"""

    __tablename__ = "prices"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="Unique ID")
    ticker = Column(String(10), ForeignKey("stocks.ticker", ondelete="CASCADE"), nullable=False, comment="Stock ticker code")
    date = Column(Date, nullable=False, comment="Trading date")
    timestamp = Column(DateTime, nullable=False, comment="Collection timestamp")
    current_price = Column(Numeric(12, 2), nullable=False, comment="Current price")
    change_rate = Column(Numeric(6, 2), nullable=True, comment="Change rate (%)")
    change_amount = Column(Numeric(12, 2), nullable=True, comment="Change amount")
    open_price = Column(Numeric(12, 2), nullable=True, comment="Open price")
    high_price = Column(Numeric(12, 2), nullable=True, comment="High price")
    low_price = Column(Numeric(12, 2), nullable=True, comment="Low price")
    volume = Column(Numeric(20, 0), nullable=True, comment="Trading volume")
    weekly_change_rate = Column(Numeric(6, 2), nullable=True, comment="Weekly change rate (%)")
    previous_close = Column(Numeric(12, 2), nullable=True, comment="Previous close")

    __table_args__ = (
        Index("idx_ticker_date", "ticker", "date"),
        Index("idx_ticker_timestamp", "ticker", "timestamp"),
    )
```

#### 2.2.5 CREATE TABLE SQL (MySQL)

```sql
CREATE TABLE prices (
    id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY COMMENT 'Unique ID',
    ticker VARCHAR(10) NOT NULL COMMENT 'Stock ticker code',
    date DATE NOT NULL COMMENT 'Trading date',
    timestamp DATETIME NOT NULL COMMENT 'Collection timestamp',
    current_price DECIMAL(12, 2) NOT NULL COMMENT 'Current price',
    change_rate DECIMAL(6, 2) DEFAULT NULL COMMENT 'Change rate (%)',
    change_amount DECIMAL(12, 2) DEFAULT NULL COMMENT 'Change amount',
    open_price DECIMAL(12, 2) DEFAULT NULL COMMENT 'Open price',
    high_price DECIMAL(12, 2) DEFAULT NULL COMMENT 'High price',
    low_price DECIMAL(12, 2) DEFAULT NULL COMMENT 'Low price',
    volume DECIMAL(20, 0) DEFAULT NULL COMMENT 'Trading volume',
    weekly_change_rate DECIMAL(6, 2) DEFAULT NULL COMMENT 'Weekly change rate (%)',
    previous_close DECIMAL(12, 2) DEFAULT NULL COMMENT 'Previous close',
    INDEX idx_ticker_date (ticker, date),
    INDEX idx_ticker_timestamp (ticker, timestamp),
    FOREIGN KEY (ticker) REFERENCES stocks(ticker) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

### 2.3 trading_trends

The `trading_trends` table stores investor trading trend data (individual, institutional, and foreign investors).

#### 2.3.1 Table Structure

| Column | Type | Nullable | Default | Constraints | Description |
|--------|------|----------|---------|-------------|-------------|
| `id` | BIGINT | NO | AUTO_INCREMENT | PRIMARY KEY | Unique record ID |
| `ticker` | VARCHAR(10) | NO | - | FOREIGN KEY | Stock ticker code |
| `date` | DATE | NO | - | - | Trading date |
| `timestamp` | DATETIME | NO | - | - | Data collection timestamp |
| `individual` | DECIMAL(20, 0) | YES | NULL | - | Individual investor net volume (+ buy, - sell) |
| `institution` | DECIMAL(20, 0) | YES | NULL | - | Institutional investor net volume |
| `foreign_investor` | DECIMAL(20, 0) | YES | NULL | - | Foreign investor net volume |
| `total` | DECIMAL(20, 0) | YES | NULL | - | Total trading volume |

#### 2.3.2 Indexes

- **Primary Key**: `id` (auto-increment)
- **Index**: `idx_ticker_date` on `(ticker, date)` - For querying trading trends by ticker and date
- **Index**: `idx_ticker_timestamp` on `(ticker, timestamp)` - For querying latest trading trends

#### 2.3.3 Foreign Keys

- **Foreign Key**: `ticker` REFERENCES `stocks(ticker)` ON DELETE CASCADE

#### 2.3.4 SQLAlchemy Model

```python
from sqlalchemy import Column, BigInteger, String, Numeric, DateTime, Date, ForeignKey, Index
from app.db_base import Base

class TradingTrend(Base):
    """Trading trend table"""

    __tablename__ = "trading_trends"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="Unique ID")
    ticker = Column(String(10), ForeignKey("stocks.ticker", ondelete="CASCADE"), nullable=False, comment="Stock ticker code")
    date = Column(Date, nullable=False, comment="Trading date")
    timestamp = Column(DateTime, nullable=False, comment="Collection timestamp")
    individual = Column(Numeric(20, 0), nullable=True, comment="Individual investor volume (net buy: +, net sell: -)")
    institution = Column(Numeric(20, 0), nullable=True, comment="Institutional investor volume")
    foreign_investor = Column(Numeric(20, 0), nullable=True, comment="Foreign investor volume")
    total = Column(Numeric(20, 0), nullable=True, comment="Total trading volume")

    __table_args__ = (
        Index("idx_ticker_date", "ticker", "date"),
        Index("idx_ticker_timestamp", "ticker", "timestamp"),
    )
```

#### 2.3.5 CREATE TABLE SQL (MySQL)

```sql
CREATE TABLE trading_trends (
    id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY COMMENT 'Unique ID',
    ticker VARCHAR(10) NOT NULL COMMENT 'Stock ticker code',
    date DATE NOT NULL COMMENT 'Trading date',
    timestamp DATETIME NOT NULL COMMENT 'Collection timestamp',
    individual DECIMAL(20, 0) DEFAULT NULL COMMENT 'Individual investor volume (net buy: +, net sell: -)',
    institution DECIMAL(20, 0) DEFAULT NULL COMMENT 'Institutional investor volume',
    foreign_investor DECIMAL(20, 0) DEFAULT NULL COMMENT 'Foreign investor volume',
    total DECIMAL(20, 0) DEFAULT NULL COMMENT 'Total trading volume',
    INDEX idx_ticker_date (ticker, date),
    INDEX idx_ticker_timestamp (ticker, timestamp),
    FOREIGN KEY (ticker) REFERENCES stocks(ticker) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

### 2.4 news

The `news` table stores news articles related to stocks and ETFs.

#### 2.4.1 Table Structure

| Column | Type | Nullable | Default | Constraints | Description |
|--------|------|----------|---------|-------------|-------------|
| `id` | VARCHAR(50) | NO | - | PRIMARY KEY | Unique news ID |
| `ticker` | VARCHAR(10) | NO | - | FOREIGN KEY | Related stock ticker code |
| `title` | VARCHAR(500) | NO | - | - | News article title |
| `url` | VARCHAR(1000) | NO | - | UNIQUE | News article URL |
| `source` | VARCHAR(100) | YES | NULL | - | News source |
| `published_at` | DATETIME | YES | NULL | - | Publication timestamp |
| `collected_at` | DATETIME | NO | CURRENT_TIMESTAMP | - | Collection timestamp |

#### 2.4.2 Indexes

- **Primary Key**: `id`
- **Index**: `idx_ticker_published` on `(ticker, published_at)` - For querying news by ticker and publication date
- **Index**: `idx_published_at` on `published_at` - For querying recent news
- **Unique Constraint**: `uk_url` on `url` - Prevents duplicate news articles

#### 2.4.3 Foreign Keys

- **Foreign Key**: `ticker` REFERENCES `stocks(ticker)` ON DELETE CASCADE

#### 2.4.4 SQLAlchemy Model

```python
from sqlalchemy import Column, String, DateTime, ForeignKey, Index, UniqueConstraint
from datetime import datetime
from app.db_base import Base

class News(Base):
    """News table"""

    __tablename__ = "news"

    id = Column(String(50), primary_key=True, comment="Unique ID")
    ticker = Column(String(10), ForeignKey("stocks.ticker", ondelete="CASCADE"), nullable=False, comment="Related stock ticker code")
    title = Column(String(500), nullable=False, comment="News title")
    url = Column(String(1000), nullable=False, comment="News URL")
    source = Column(String(100), nullable=True, comment="News source")
    published_at = Column(DateTime, nullable=True, comment="Publication timestamp")
    collected_at = Column(DateTime, nullable=False, default=datetime.utcnow, comment="Collection timestamp")

    __table_args__ = (
        Index("idx_ticker_published", "ticker", "published_at"),
        Index("idx_published_at", "published_at"),
        UniqueConstraint("url", name="uk_url"),
    )
```

#### 2.4.5 CREATE TABLE SQL (MySQL)

```sql
CREATE TABLE news (
    id VARCHAR(50) PRIMARY KEY COMMENT 'Unique ID',
    ticker VARCHAR(10) NOT NULL COMMENT 'Related stock ticker code',
    title VARCHAR(500) NOT NULL COMMENT 'News title',
    url VARCHAR(1000) NOT NULL COMMENT 'News URL',
    source VARCHAR(100) DEFAULT NULL COMMENT 'News source',
    published_at DATETIME DEFAULT NULL COMMENT 'Publication timestamp',
    collected_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Collection timestamp',
    INDEX idx_ticker_published (ticker, published_at),
    INDEX idx_published_at (published_at),
    UNIQUE KEY uk_url (url),
    FOREIGN KEY (ticker) REFERENCES stocks(ticker) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

## 3. Entity Relationship Diagram

### 3.1 Text-Based ERD

```
┌─────────────────┐
│     stocks      │
│─────────────────│
│ ticker (PK)     │
│ name            │
│ type            │
│ theme           │
│ fee             │
│ created_at      │
│ updated_at      │
└────────┬────────┘
         │
         │ 1:N
         │
    ┌────┴──────┬─────────────┬─────────────┐
    │           │             │             │
    ▼           ▼             ▼             ▼
┌───────┐  ┌─────────┐  ┌──────────┐  ┌──────┐
│prices │  │trading_ │  │   news   │  │ ...  │
│       │  │trends   │  │          │  │future│
└───────┘  └─────────┘  └──────────┘  └──────┘
```

### 3.2 Relationship Details

#### stocks (Parent Table)
- **Relationship**: One-to-Many with `prices`, `trading_trends`, and `news`
- **Cascade**: ON DELETE CASCADE (deleting a stock removes all related data)
- **Foreign Key Column**: `ticker` in child tables

#### prices (Child Table)
- **Parent**: `stocks.ticker`
- **Cardinality**: One stock can have many price records
- **Purpose**: Store historical and real-time price data

#### trading_trends (Child Table)
- **Parent**: `stocks.ticker`
- **Cardinality**: One stock can have many trading trend records
- **Purpose**: Store investor trading patterns

#### news (Child Table)
- **Parent**: `stocks.ticker`
- **Cardinality**: One stock can have many news articles
- **Purpose**: Store related news articles

---

## 4. Indexing Strategy

### 4.1 Index Overview

Indexes are strategically placed to optimize common query patterns while minimizing write overhead.

### 4.2 Index Details by Table

#### 4.2.1 stocks Table

| Index Name | Columns | Type | Purpose |
|------------|---------|------|---------|
| PRIMARY | `ticker` | Primary Key | Unique identifier lookup |
| `idx_type` | `type` | Non-unique | Filter stocks by type (STOCK/ETF) |
| `idx_theme` | `theme` | Non-unique | Filter stocks by investment theme |

**Query Optimization**:
- Fast lookup by ticker code
- Efficient filtering by stock type
- Quick theme-based searches

#### 4.2.2 prices Table

| Index Name | Columns | Type | Purpose |
|------------|---------|------|---------|
| PRIMARY | `id` | Primary Key | Unique record identifier |
| `idx_ticker_date` | `ticker`, `date` | Composite, Non-unique | Query price history by ticker and date range |
| `idx_ticker_timestamp` | `ticker`, `timestamp` | Composite, Non-unique | Query latest price data by ticker |

**Query Optimization**:
- Fast retrieval of price data for a specific ticker and date range
- Efficient sorting by date within a ticker
- Quick access to the latest price record

#### 4.2.3 trading_trends Table

| Index Name | Columns | Type | Purpose |
|------------|---------|------|---------|
| PRIMARY | `id` | Primary Key | Unique record identifier |
| `idx_ticker_date` | `ticker`, `date` | Composite, Non-unique | Query trading trends by ticker and date |
| `idx_ticker_timestamp` | `ticker`, `timestamp` | Composite, Non-unique | Query latest trading trends by ticker |

**Query Optimization**:
- Fast retrieval of trading trends for a specific ticker and date
- Efficient access to the latest trading trend data

#### 4.2.4 news Table

| Index Name | Columns | Type | Purpose |
|------------|---------|------|---------|
| PRIMARY | `id` | Primary Key | Unique record identifier |
| `idx_ticker_published` | `ticker`, `published_at` | Composite, Non-unique | Query news by ticker and publication date |
| `idx_published_at` | `published_at` | Non-unique | Query recent news across all stocks |
| `uk_url` | `url` | Unique | Prevent duplicate news articles |

**Query Optimization**:
- Fast retrieval of news for a specific ticker
- Efficient sorting by publication date
- Quick duplicate detection during news collection

### 4.3 Index Maintenance

- **Auto-increment IDs**: Used for child tables to ensure fast inserts
- **Composite Indexes**: Designed for common query patterns (ticker + date/timestamp)
- **Unique Constraints**: Enforced on `url` in news table to prevent duplicates

---

## 5. Migration Guide

### 5.1 Migration Tool: Alembic

K-SectorRadar uses Alembic for database schema migrations.

#### 5.1.1 Alembic Configuration

**Location**: `backend/alembic.ini`

**Key Settings**:
- `sqlalchemy.url`: Database connection URL (can be overridden by environment variable)
- `script_location`: `backend/alembic` (migration scripts directory)

#### 5.1.2 Migration Scripts Directory

```
backend/alembic/
├── versions/          # Migration version files
│   └── <version>_initial_schema.py
├── env.py             # Alembic environment configuration
├── script.py.mako     # Migration script template
└── README
```

### 5.2 Running Migrations

#### 5.2.1 Initial Migration (First Time Setup)

**Step 1**: Ensure database is created

For MySQL:
```bash
mysql -u root -p
CREATE DATABASE sectorradar CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

For SQLite (development):
```bash
# Database file will be created automatically
```

**Step 2**: Run migration script

```bash
cd backend
python scripts/run_migrations.py
```

Or manually with Alembic:
```bash
cd backend
alembic upgrade head
```

#### 5.2.2 Creating New Migrations

When you modify SQLAlchemy models, create a new migration:

```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
```

Review the generated migration file in `backend/alembic/versions/` and apply it:

```bash
alembic upgrade head
```

#### 5.2.3 Migration History

View migration history:
```bash
alembic history
```

Check current migration version:
```bash
alembic current
```

#### 5.2.4 Rollback Migrations

Rollback to a specific version:
```bash
alembic downgrade <version>
```

Rollback one version:
```bash
alembic downgrade -1
```

### 5.3 Seeding Initial Data

After running migrations, seed the database with initial stock data:

```bash
cd backend
python scripts/seed_stocks.py
```

This script:
- Reads stock data from `config/stocks.json`
- Inserts initial stock records into the `stocks` table
- Handles duplicates gracefully (updates existing records if needed)

### 5.4 Database Initialization Helper

For convenience, you can use the database initialization module:

```bash
cd backend
python -m app.database
```

This will:
- Create all tables based on SQLAlchemy models
- Suitable for development environments

---

## Appendix

### A. SQLAlchemy Base Configuration

**Location**: `backend/app/db_base.py`

```python
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
```

All models inherit from this `Base` class.

### B. Database Connection Configuration

**Location**: `backend/app/database.py`

Key functions:
- `get_db()`: Dependency injection for database sessions
- `init_db()`: Initialize database tables
- `engine`: SQLAlchemy engine instance

### C. Environment Variables

Required environment variables for database connection:

```bash
# MySQL (Production/Development)
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/sectorradar

# SQLite (Development Only)
DATABASE_URL=sqlite:///./sectorradar.db
```

---

**Document Version**: 1.0
**Author**: K-SectorRadar Development Team
**Last Updated**: 2025-11-15
