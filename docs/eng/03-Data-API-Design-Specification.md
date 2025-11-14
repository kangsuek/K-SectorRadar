## 1. Document Overview

### 1.1 Purpose
This document defines the data models, database schema, and REST API design for the K-SectorRadar project.

### 1.2 Scope
This document includes data model definitions, database schema design, API endpoint design, request/response formats, etc.

### 1.3 References
- Requirements Specification
- System Design Document
- Data Collection and Processing Design Document

---

## 2. Data Models

### 2.1 Stock Information (Stock/ETF)

#### 2.1.1 JSON Schema
```json
{
  "ticker": "034020",
  "name": "Doosan Enerbility",
  "type": "STOCK",
  "theme": "Nuclear/Power Plant/Energy",
  "fee": null,
  "createdAt": "2025-01-01T00:00:00Z",
  "updatedAt": "2025-11-13T21:22:11Z"
}
```

#### 2.1.2 Field Descriptions
| Field | Type | Required | Description |
|:---|:---|:---|:---|
| `ticker` | string | ✓ | Stock code (unique identifier, PK) |
| `name` | string | ✓ | Stock name |
| `type` | string | ✓ | Stock type (STOCK or ETF) |
| `theme` | string | - | Theme classification |
| `fee` | number\|null | - | Fee (ETF only, nullable) |
| `createdAt` | string (ISO 8601) | ✓ | Creation timestamp |
| `updatedAt` | string (ISO 8601) | ✓ | Last update timestamp |

### 2.2 Price Data (Price)

#### 2.2.1 JSON Schema
```json
{
  "ticker": "034020",
  "date": "2025-11-13",
  "timestamp": "2025-11-13T15:30:00Z",
  "currentPrice": 83100,
  "changeRate": 2.5,
  "changeAmount": 2025,
  "openPrice": 82000,
  "highPrice": 83500,
  "lowPrice": 81800,
  "volume": 7900000,
  "weeklyChangeRate": 5.2,
  "previousClose": 81075
}
```

#### 2.2.2 Field Descriptions
| Field | Type | Required | Description |
|:---|:---|:---|:---|
| `ticker` | string | ✓ | Stock code |
| `date` | string (YYYY-MM-DD) | ✓ | Trading date |
| `timestamp` | string (ISO 8601) | ✓ | Collection timestamp |
| `currentPrice` | number | ✓ | Current price |
| `changeRate` | number | - | Change rate (%) |
| `changeAmount` | number | - | Change amount |
| `openPrice` | number | - | Open price |
| `highPrice` | number | - | High price |
| `lowPrice` | number | - | Low price |
| `volume` | number | - | Trading volume |
| `weeklyChangeRate` | number | - | Weekly change rate (%) |
| `previousClose` | number | - | Previous close price |

### 2.3 Trading Trend

#### 2.3.1 JSON Schema
```json
{
  "ticker": "034020",
  "date": "2025-11-13",
  "timestamp": "2025-11-13T15:30:00Z",
  "individual": -860000,
  "institution": 220000,
  "foreign": 650000,
  "total": 10000
}
```

#### 2.3.2 Field Descriptions
| Field | Type | Required | Description |
|:---|:---|:---|:---|
| `ticker` | string | ✓ | Stock code |
| `date` | string (YYYY-MM-DD) | ✓ | Trading date |
| `timestamp` | string (ISO 8601) | ✓ | Collection timestamp |
| `individual` | number | - | Individual investor trading volume (net buy: +, net sell: -) |
| `institution` | number | - | Institutional investor trading volume |
| `foreign` | number | - | Foreign investor trading volume |
| `total` | number | - | Total trading volume |

### 2.4 News Data

#### 2.4.1 JSON Schema
```json
{
  "id": "news_001",
  "ticker": "034020",
  "title": "Doosan Enerbility Expands Nuclear Business",
  "url": "https://...",
  "source": "Maeil Business",
  "publishedAt": "2025-11-13T10:00:00Z",
  "collectedAt": "2025-11-13T10:05:00Z"
}
```

#### 2.4.2 Field Descriptions
| Field | Type | Required | Description |
|:---|:---|:---|:---|
| `id` | string | ✓ | News unique ID (PK) |
| `ticker` | string | ✓ | Related stock code |
| `title` | string | ✓ | News title |
| `url` | string | ✓ | News URL |
| `source` | string | - | Source |
| `publishedAt` | string (ISO 8601) | - | Publication timestamp |
| `collectedAt` | string (ISO 8601) | ✓ | Collection timestamp |

### 2.5 Chart Data

#### 2.5.1 JSON Schema
```json
{
  "ticker": "034020",
  "date": "2025-11-13",
  "data": [
    {
      "date": "2025-11-08",
      "open": 80000,
      "high": 81000,
      "low": 79500,
      "close": 80500,
      "volume": 5000000
    }
  ]
}
```

#### 2.5.2 Field Descriptions
| Field | Type | Required | Description |
|:---|:---|:---|:---|
| `ticker` | string | ✓ | Stock code |
| `date` | string (YYYY-MM-DD) | ✓ | Base date |
| `data` | array | ✓ | Chart data array (last 6 days) |
| `data[].date` | string | ✓ | Trading date |
| `data[].open` | number | ✓ | Open price |
| `data[].high` | number | ✓ | High price |
| `data[].low` | number | ✓ | Low price |
| `data[].close` | number | ✓ | Close price |
| `data[].volume` | number | ✓ | Trading volume |

---

## 3. Database Schema

### 3.1 Database Overview
- **DBMS**: MySQL or PostgreSQL
- **Encoding**: UTF-8
- **Timezone**: UTC

### 3.2 Table Design

#### 3.2.1 stocks Table
```sql
CREATE TABLE stocks (
  ticker VARCHAR(10) PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  type VARCHAR(10) NOT NULL CHECK (type IN ('STOCK', 'ETF')),
  theme VARCHAR(200),
  fee DECIMAL(10, 6),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_type (type),
  INDEX idx_theme (theme)
);
```

#### 3.2.2 prices Table
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
  volume BIGINT,
  weekly_change_rate DECIMAL(6, 2),
  previous_close DECIMAL(12, 2),
  INDEX idx_ticker_date (ticker, date),
  INDEX idx_ticker_timestamp (ticker, timestamp),
  FOREIGN KEY (ticker) REFERENCES stocks(ticker) ON DELETE CASCADE
);
```

#### 3.2.3 trading_trends Table
```sql
CREATE TABLE trading_trends (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  ticker VARCHAR(10) NOT NULL,
  date DATE NOT NULL,
  timestamp TIMESTAMP NOT NULL,
  individual BIGINT,
  institution BIGINT,
  foreign_investor BIGINT,
  total BIGINT,
  INDEX idx_ticker_date (ticker, date),
  INDEX idx_ticker_timestamp (ticker, timestamp),
  FOREIGN KEY (ticker) REFERENCES stocks(ticker) ON DELETE CASCADE
);
```

#### 3.2.4 news Table
```sql
CREATE TABLE news (
  id VARCHAR(50) PRIMARY KEY,
  ticker VARCHAR(10) NOT NULL,
  title VARCHAR(500) NOT NULL,
  url VARCHAR(1000) NOT NULL,
  source VARCHAR(100),
  published_at TIMESTAMP,
  collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_ticker_published (ticker, published_at),
  INDEX idx_published_at (published_at),
  FOREIGN KEY (ticker) REFERENCES stocks(ticker) ON DELETE CASCADE,
  UNIQUE KEY uk_url (url(255))
);
```

---

## 4. API Design

### 4.1 API Overview
- **Base URL**: `/api`
- **Authentication**: No authentication in initial version (expandable in future)
- **Response Format**: JSON
- **Character Encoding**: UTF-8

### 4.2 API Endpoints

#### 4.2.1 Stock List Retrieval
- **Method**: `GET`
- **Path**: `/api/stocks`
- **Description**: Retrieves the list of all stocks.
- **Query Parameters**:
  | Parameter | Type | Required | Description |
  |:---|:---|:---|:---|
  | `type` | string | - | Stock type filter (STOCK, ETF) |
  | `theme` | string | - | Theme filter |
  | `limit` | number | - | Query limit (default: 100) |
  | `offset` | number | - | Page offset (default: 0) |

- **Response Example**:
```json
{
  "success": true,
  "data": {
    "stocks": [
      {
        "ticker": "034020",
        "name": "Doosan Enerbility",
        "type": "STOCK",
        "theme": "Nuclear/Power Plant/Energy",
        "fee": null
      }
    ],
    "total": 50,
    "limit": 100,
    "offset": 0
  },
  "message": "",
  "timestamp": "2025-11-13T21:23:43Z"
}
```

#### 4.2.2 Stock Detail Retrieval
- **Method**: `GET`
- **Path**: `/api/stocks/{ticker}`
- **Description**: Retrieves detailed information of a specific stock.
- **Path Parameters**:
  | Parameter | Type | Required | Description |
  |:---|:---|:---|:---|
  | `ticker` | string | ✓ | Stock code |

- **Response Example**:
```json
{
  "success": true,
  "data": {
    "ticker": "034020",
    "name": "Doosan Enerbility",
    "type": "STOCK",
    "theme": "Nuclear/Power Plant/Energy",
    "fee": null,
    "createdAt": "2025-01-01T00:00:00Z",
    "updatedAt": "2025-11-13T21:22:11Z"
  },
  "message": "",
  "timestamp": "2025-11-13T21:23:43Z"
}
```

#### 4.2.3 Price Data Retrieval
- **Method**: `GET`
- **Path**: `/api/stocks/{ticker}/price`
- **Description**: Retrieves price data of a specific stock.
- **Path Parameters**:
  | Parameter | Type | Required | Description |
  |:---|:---|:---|:---|
  | `ticker` | string | ✓ | Stock code |

- **Query Parameters**:
  | Parameter | Type | Required | Description |
  |:---|:---|:---|:---|
  | `date` | string | - | Specific date query (YYYY-MM-DD, default: latest) |

- **Response Example**:
```json
{
  "success": true,
  "data": {
    "ticker": "034020",
    "date": "2025-11-13",
    "timestamp": "2025-11-13T15:30:00Z",
    "currentPrice": 83100,
    "changeRate": 2.5,
    "changeAmount": 2025,
    "openPrice": 82000,
    "highPrice": 83500,
    "lowPrice": 81800,
    "volume": 7900000,
    "weeklyChangeRate": 5.2,
    "previousClose": 81075
  },
  "message": "",
  "timestamp": "2025-11-13T21:23:43Z"
}
```

#### 4.2.4 Trading Trend Retrieval
- **Method**: `GET`
- **Path**: `/api/stocks/{ticker}/trading`
- **Description**: Retrieves trading trend data of a specific stock.
- **Path Parameters**:
  | Parameter | Type | Required | Description |
  |:---|:---|:---|:---|
  | `ticker` | string | ✓ | Stock code |

- **Query Parameters**:
  | Parameter | Type | Required | Description |
  |:---|:---|:---|:---|
  | `date` | string | - | Specific date query (YYYY-MM-DD, default: latest) |

- **Response Example**:
```json
{
  "success": true,
  "data": {
    "ticker": "034020",
    "date": "2025-11-13",
    "timestamp": "2025-11-13T15:30:00Z",
    "individual": -860000,
    "institution": 220000,
    "foreign": 650000,
    "total": 10000
  },
  "message": "",
  "timestamp": "2025-11-13T21:23:43Z"
}
```

#### 4.2.5 News Retrieval
- **Method**: `GET`
- **Path**: `/api/stocks/{ticker}/news`
- **Description**: Retrieves news list of a specific stock.
- **Path Parameters**:
  | Parameter | Type | Required | Description |
  |:---|:---|:---|:---|
  | `ticker` | string | ✓ | Stock code |

- **Query Parameters**:
  | Parameter | Type | Required | Description |
  |:---|:---|:---|:---|
  | `limit` | number | - | Query limit (default: 10, max: 50) |
  | `offset` | number | - | Page offset (default: 0) |

- **Response Example**:
```json
{
  "success": true,
  "data": {
    "news": [
      {
        "id": "news_001",
        "ticker": "034020",
        "title": "Doosan Enerbility Expands Nuclear Business",
        "url": "https://...",
        "source": "Maeil Business",
        "publishedAt": "2025-11-13T10:00:00Z",
        "collectedAt": "2025-11-13T10:05:00Z"
      }
    ],
    "total": 15,
    "limit": 10,
    "offset": 0
  },
  "message": "",
  "timestamp": "2025-11-13T21:23:43Z"
}
```

#### 4.2.6 Chart Data Retrieval
- **Method**: `GET`
- **Path**: `/api/stocks/{ticker}/chart`
- **Description**: Retrieves chart data of a specific stock.
- **Path Parameters**:
  | Parameter | Type | Required | Description |
  |:---|:---|:---|:---|
  | `ticker` | string | ✓ | Stock code |

- **Query Parameters**:
  | Parameter | Type | Required | Description |
  |:---|:---|:---|:---|
  | `days` | number | - | Query period (days, default: 6, max: 30) |

- **Response Example**:
```json
{
  "success": true,
  "data": {
    "ticker": "034020",
    "date": "2025-11-13",
    "data": [
      {
        "date": "2025-11-08",
        "open": 80000,
        "high": 81000,
        "low": 79500,
        "close": 80500,
        "volume": 5000000
      }
    ]
  },
  "message": "",
  "timestamp": "2025-11-13T21:23:43Z"
}
```

#### 4.2.7 Data Refresh
- **Method**: `POST`
- **Path**: `/api/refresh`
- **Description**: Manually refreshes data for all stocks.
- **Request Body**:
```json
{
  "tickers": ["034020", "005930"]
}
```
  | Field | Type | Required | Description |
  |:---|:---|:---|:---|
  | `tickers` | array | - | Array of stock codes to refresh (if empty, refresh all) |

- **Response Example**:
```json
{
  "success": true,
  "data": {
    "updated": 2,
    "failed": 0,
    "tickers": ["034020", "005930"]
  },
  "message": "Data refresh completed.",
  "timestamp": "2025-11-13T21:23:43Z"
}
```

### 4.3 API Response Format

#### 4.3.1 Success Response
```json
{
  "success": true,
  "data": {},
  "message": "",
  "timestamp": "2025-11-13T21:23:43Z"
}
```

#### 4.3.2 Error Response
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error message",
    "details": {}
  },
  "timestamp": "2025-11-13T21:23:43Z"
}
```

#### 4.3.3 Error Codes
| Code | HTTP Status | Description |
|:---|:---|:---|
| `NOT_FOUND` | 404 | Resource not found |
| `INVALID_PARAMETER` | 400 | Invalid parameter |
| `INTERNAL_ERROR` | 500 | Internal server error |
| `SERVICE_UNAVAILABLE` | 503 | Service unavailable |

---

## 5. Data Validation Rules

### 5.1 Price Data Validation
- Current price > 0
- High price >= Low price
- Current price exists within open, high, low price range
- Volume >= 0
- Change rate range: -100% ~ +100% (theoretical limit)

### 5.2 Trading Trend Validation
- Individual + Institution + Foreign = Total volume (approximate, ±5% allowed)
- Verify each value is numeric type
- Validate reasonableness of trading volume values

### 5.3 News Data Validation
- Title is not empty (minimum 1 character)
- URL is valid format (http:// or https://)
- Published timestamp is valid date format (ISO 8601)
- URL duplication prevention

### 5.4 Stock Information Validation
- Ticker is 6-digit numeric string
- Name is minimum 1 character, maximum 100 characters
- Type only allows 'STOCK' or 'ETF'
- Fee is required for ETF, null for STOCK

---

## 6. Caching Strategy

### 6.1 Cache Structure (Redis)
- **Cache Key Pattern**: `{prefix}:{type}:{ticker}`
- **Examples**:
  - `ksr:stock:034020`: Stock information
  - `ksr:price:034020`: Latest price data
  - `ksr:trading:034020`: Latest trading trend
  - `ksr:news:034020`: Latest news list
  - `ksr:chart:034020`: Chart data

### 6.2 Cache TTL (Time To Live)
| Data Type | TTL | Description |
|:---|:---|:---|
| Stock Information | 1 hour | Low change frequency |
| Price Data | 30 seconds | Real-time data |
| Trading Trend | 30 seconds | Real-time data |
| News Data | 10 minutes | Same as update cycle |
| Chart Data | 1 minute | Daily data |

### 6.3 Cache Invalidation Strategy
- Automatic cache update on data collection
- Delete and regenerate related cache on manual refresh
- Automatic deletion on TTL expiration

---

## 7. Performance Optimization

### 7.1 Database Optimization
- Index design: Create indexes on frequently queried fields
- Query optimization: Minimize JOINs, SELECT only necessary columns
- Partitioning: Consider date-based partitioning for prices table

### 7.2 API Optimization
- Response data compression (gzip)
- Pagination application
- Parallel processing: Parallel processing when querying multiple stocks
- Rate Limiting: API call limits (e.g., 100 requests per second)

---

