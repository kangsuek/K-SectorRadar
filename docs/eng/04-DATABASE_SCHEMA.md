# Database Schema

## 1. Document Overview

### 1.1 Purpose
This document defines the database schema for the K-SectorRadar project.

### 1.2 Scope
This document includes table definitions, relationships, indexes, and constraints.

### 1.3 References
- Data Models: See `docs/eng/05-Data-API-Design-Specification.md` (Section 2)
- API Specification: See `docs/eng/03-API_SPECIFICATION.md`
- Requirements Specification: `docs/eng/01-Requirements-Specification.md`

---

## 2. Database Overview

### 2.1 Database Configuration
- **DBMS**: MySQL 8.0+ (Primary - Development & Production)
- **Encoding**: UTF-8 (UTF8MB4 for MySQL)
- **Timezone**: UTC
- **ORM**: SQLAlchemy 2.0+

### 2.2 Database Support
- **MySQL**: **Primary database** for both development and production environments (required)
- **PostgreSQL**: Optional alternative (supported but not recommended)
- **SQLite**: Testing only (do not use for development or production)

---

## 3. Table Definitions

### 3.1 stocks Table

**Purpose**: Stores stock/ETF basic information

**SQL Definition**:
```sql
CREATE TABLE stocks (
  ticker VARCHAR(10) PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  type VARCHAR(10) NOT NULL CHECK (type IN ('STOCK', 'ETF')),
  theme VARCHAR(200),
  fee DECIMAL(10, 6),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_stock_type (type),
  INDEX idx_stock_theme (theme)
);
```

**Column Descriptions**:
| Column | Type | Nullable | Description |
|:---|:---|:---|:---|
| `ticker` | VARCHAR(10) | NO | Stock code (Primary Key) |
| `name` | VARCHAR(100) | NO | Stock name |
| `type` | VARCHAR(10) | NO | Stock type (STOCK or ETF) |
| `theme` | VARCHAR(200) | YES | Theme classification |
| `fee` | DECIMAL(10, 6) | YES | Fee (ETF only, nullable) |
| `created_at` | TIMESTAMP | NO | Creation timestamp |
| `updated_at` | TIMESTAMP | NO | Last update timestamp |

**Indexes**:
- Primary Key: `ticker`
- Index: `idx_stock_type` on `type`
- Index: `idx_stock_theme` on `theme`

**Constraints**:
- Check constraint: `type` must be 'STOCK' or 'ETF'

**Relationships**:
- One-to-Many with `prices` table
- One-to-Many with `trading_trends` table
- One-to-Many with `news` table

---

### 3.2 prices Table

**Purpose**: Stores historical price data for stocks

**SQL Definition**:
```sql
CREATE TABLE prices (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  ticker VARCHAR(10) NOT NULL,
  date DATE NOT NULL,
  timestamp TIMESTAMP NOT NULL,
  current_price DECIMAL(12, 2) NOT NULL,
  change_rate DECIMAL(6, 2),
  change_amount DECIMAL(12, 2),
  open_price DECIMAL(12, 2),
  high_price DECIMAL(12, 2),
  low_price DECIMAL(12, 2),
  volume NUMERIC(20, 0),
  weekly_change_rate DECIMAL(6, 2),
  previous_close DECIMAL(12, 2),
  INDEX idx_price_ticker_date (ticker, date),
  INDEX idx_price_ticker_timestamp (ticker, timestamp),
  FOREIGN KEY (ticker) REFERENCES stocks(ticker) ON DELETE CASCADE
);
```

**Column Descriptions**:
| Column | Type | Nullable | Description |
|:---|:---|:---|:---|
| `id` | BIGINT | NO | Primary key (Auto-increment) |
| `ticker` | VARCHAR(10) | NO | Stock code (Foreign Key) |
| `date` | DATE | NO | Trading date |
| `timestamp` | TIMESTAMP | NO | Collection timestamp |
| `current_price` | DECIMAL(12, 2) | NO | Current price |
| `change_rate` | DECIMAL(6, 2) | YES | Change rate (%) |
| `change_amount` | DECIMAL(12, 2) | YES | Change amount |
| `open_price` | DECIMAL(12, 2) | YES | Open price |
| `high_price` | DECIMAL(12, 2) | YES | High price |
| `low_price` | DECIMAL(12, 2) | YES | Low price |
| `volume` | NUMERIC(20, 0) | YES | Trading volume |
| `weekly_change_rate` | DECIMAL(6, 2) | YES | Weekly change rate (%) |
| `previous_close` | DECIMAL(12, 2) | YES | Previous close price |

**Indexes**:
- Primary Key: `id`
- Composite Index: `idx_price_ticker_date` on (`ticker`, `date`)
- Composite Index: `idx_price_ticker_timestamp` on (`ticker`, `timestamp`)

**Foreign Keys**:
- `ticker` → `stocks.ticker` (ON DELETE CASCADE)

**Notes**:
- Uses `AutoIncrementBigInteger` type for MySQL/SQLite compatibility
- `volume` uses NUMERIC(20, 0) to handle large trading volumes

---

### 3.3 trading_trends Table

**Purpose**: Stores trading trend data (individual, institution, foreign investor trading volumes)

**SQL Definition**:
```sql
CREATE TABLE trading_trends (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  ticker VARCHAR(10) NOT NULL,
  date DATE NOT NULL,
  timestamp TIMESTAMP NOT NULL,
  individual NUMERIC(20, 0),
  institution NUMERIC(20, 0),
  foreign_investor NUMERIC(20, 0),
  total NUMERIC(20, 0),
  INDEX idx_trading_ticker_date (ticker, date),
  INDEX idx_trading_ticker_timestamp (ticker, timestamp),
  FOREIGN KEY (ticker) REFERENCES stocks(ticker) ON DELETE CASCADE
);
```

**Column Descriptions**:
| Column | Type | Nullable | Description |
|:---|:---|:---|:---|
| `id` | BIGINT | NO | Primary key (Auto-increment) |
| `ticker` | VARCHAR(10) | NO | Stock code (Foreign Key) |
| `date` | DATE | NO | Trading date |
| `timestamp` | TIMESTAMP | NO | Collection timestamp |
| `individual` | NUMERIC(20, 0) | YES | Individual investor trading volume (net buy: +, net sell: -) |
| `institution` | NUMERIC(20, 0) | YES | Institutional investor trading volume |
| `foreign_investor` | NUMERIC(20, 0) | YES | Foreign investor trading volume |
| `total` | NUMERIC(20, 0) | YES | Total trading volume |

**Indexes**:
- Primary Key: `id`
- Composite Index: `idx_trading_ticker_date` on (`ticker`, `date`)
- Composite Index: `idx_trading_ticker_timestamp` on (`ticker`, `timestamp`)

**Foreign Keys**:
- `ticker` → `stocks.ticker` (ON DELETE CASCADE)

**Notes**:
- Uses `AutoIncrementBigInteger` type for MySQL/SQLite compatibility
- Trading volumes use NUMERIC(20, 0) to handle large values

---

### 3.4 news Table

**Purpose**: Stores news articles related to stocks

**SQL Definition**:
```sql
CREATE TABLE news (
  id VARCHAR(50) PRIMARY KEY,
  ticker VARCHAR(10) NOT NULL,
  title VARCHAR(500) NOT NULL,
  url VARCHAR(1000) NOT NULL,
  url_hash VARCHAR(64) NOT NULL,
  source VARCHAR(100),
  published_at TIMESTAMP,
  collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_news_ticker_published (ticker, published_at),
  INDEX idx_news_published_at (published_at),
  UNIQUE INDEX ix_news_url_hash (url_hash),
  FOREIGN KEY (ticker) REFERENCES stocks(ticker) ON DELETE CASCADE
);
```

**Column Descriptions**:
| Column | Type | Nullable | Description |
|:---|:---|:---|:---|
| `id` | VARCHAR(50) | NO | News unique ID (Primary Key) |
| `ticker` | VARCHAR(10) | NO | Related stock code (Foreign Key) |
| `title` | VARCHAR(500) | NO | News title |
| `url` | VARCHAR(1000) | NO | News URL |
| `url_hash` | VARCHAR(64) | NO | News URL SHA256 hash (for uniqueness check) |
| `source` | VARCHAR(100) | YES | Source |
| `published_at` | TIMESTAMP | YES | Publication timestamp |
| `collected_at` | TIMESTAMP | NO | Collection timestamp |

**Indexes**:
- Primary Key: `id`
- Composite Index: `idx_news_ticker_published` on (`ticker`, `published_at`)
- Index: `idx_news_published_at` on `published_at`
- Unique Index: `ix_news_url_hash` on `url_hash` (SHA256 hash of URL)

**Foreign Keys**:
- `ticker` → `stocks.ticker` (ON DELETE CASCADE)

**Notes**:
- URL uniqueness is enforced via `url_hash` field (SHA256 hash) to avoid MySQL index key length limitations
- `url_hash` is automatically generated from the URL when saving news data
- `collected_at` defaults to current timestamp

---

## 4. Entity Relationship Diagram

```
stocks (1) ──< (N) prices
    │
    ├──< (N) trading_trends
    │
    └──< (N) news
```

**Relationship Types**:
- `stocks` → `prices`: One-to-Many (CASCADE DELETE)
- `stocks` → `trading_trends`: One-to-Many (CASCADE DELETE)
- `stocks` → `news`: One-to-Many (CASCADE DELETE)

---

## 5. Index Strategy

### 5.1 Primary Indexes
- All tables have primary keys for unique identification
- `stocks.ticker`: Used as foreign key reference

### 5.2 Composite Indexes
- `prices`: (`ticker`, `date`) and (`ticker`, `timestamp`) for efficient date range queries
- `trading_trends`: (`ticker`, `date`) and (`ticker`, `timestamp`) for efficient date range queries
- `news`: (`ticker`, `published_at`) for efficient news retrieval by stock and date

### 5.3 Single Column Indexes
- `stocks.type`: For filtering by stock type
- `stocks.theme`: For filtering by theme
- `news.published_at`: For time-based news queries
- `news.url_hash`: Unique index for URL deduplication (SHA256 hash)

---

## 6. Data Types and Compatibility

### 6.1 Cross-Database Compatibility
- **AutoIncrementBigInteger**: Custom type for MySQL/SQLite compatibility
  - MySQL: `BIGINT AUTO_INCREMENT`
  - SQLite: `INTEGER PRIMARY KEY AUTOINCREMENT`
- **DECIMAL/NUMERIC**: Used for precise financial calculations
- **VARCHAR**: String types with appropriate length limits
- **TIMESTAMP**: UTC timestamps for consistency

### 6.2 MySQL Considerations
- **Index Key Length Limitation**: MySQL has a maximum index key length of 3072 bytes (with utf8mb4, each character can be up to 4 bytes)
- **Solution for long URLs**: Use `url_hash` (SHA256 hash) instead of direct URL for UNIQUE constraints
- **Foreign key constraints**: Automatically enforced with CASCADE DELETE

### 6.3 SQLite Considerations (Testing Only)
- Foreign key constraints must be explicitly enabled
- Unique constraints on long VARCHAR fields may have limitations
- Index names must be globally unique

---

## 7. Migration History

### Initial Schema (Phase 1.2)
- Created all four tables: `stocks`, `prices`, `trading_trends`, `news`
- Defined relationships and foreign keys
- Created indexes for performance optimization
- Implemented cross-database compatibility

### Schema Update (Phase 1.4)
- **news table**: Added `url_hash` field (VARCHAR(64)) for URL uniqueness constraint
  - Replaced direct URL UNIQUE constraint to avoid MySQL index key length limitations
  - `url_hash` uses SHA256 hash of the URL for efficient duplicate detection

### Migration Tools
- **Alembic**: Used for database migrations
- Migration scripts: `backend/scripts/run_migrations.py`

---

## 8. Data Seeding

### Initial Data
- Stock data is seeded from `backend/config/stocks.json`
- Seed script: `backend/scripts/seed_stocks.py`

### Seed Process
1. Initialize database schema
2. Load stock data from JSON file
3. Insert into `stocks` table
4. Verify data integrity

---

## 9. Performance Considerations

### 9.1 Query Optimization
- Composite indexes on frequently queried columns
- Date range queries optimized with composite indexes
- Foreign key indexes for JOIN operations

### 9.2 Partitioning (Future)
- Consider date-based partitioning for `prices` table
- Consider date-based partitioning for `trading_trends` table

### 9.3 Data Retention
- Historical data retention policy (to be defined)
- Archive strategy for old data (to be defined)

---

## 10. Security Considerations

### 10.1 Data Protection
- Sensitive financial data stored with appropriate precision
- Timestamps in UTC for consistency
- Foreign key constraints ensure referential integrity

### 10.2 Access Control
- Database user permissions (to be configured in production)
- Read-only access for API queries (recommended)
- Write access only for data collection services

---

## 11. Maintenance

### 11.1 Regular Tasks
- Monitor index usage and optimize as needed
- Review query performance
- Check foreign key integrity
- Monitor table sizes and growth

### 11.2 Backup Strategy
- Regular database backups (to be configured)
- Point-in-time recovery capability (to be configured)

