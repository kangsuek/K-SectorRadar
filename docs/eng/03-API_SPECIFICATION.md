# API Specification

## 1. Document Overview

This document defines the REST API endpoints for the K-SectorRadar project, including request/response formats, error handling, and caching strategies.

**References**: Data Models (`05-Data-API-Design-Specification.md`), Database Schema (`04-DATABASE_SCHEMA.md`), Requirements (`01-Requirements-Specification.md`)

---

## 2. API Overview

**Base URL**: `/api` | **Format**: JSON | **Encoding**: UTF-8 | **Auth**: None (expandable)

### 2.1 Response Format

#### Success Response
```json
{
  "success": true,
  "data": {},
  "message": "",
  "timestamp": "2025-11-13T21:23:43Z"
}
```

#### Error Response
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

#### Error Codes
| Code | HTTP Status | Description |
|:---|:---|:---|
| `NOT_FOUND` | 404 | Resource not found |
| `INVALID_PARAMETER` | 400 | Invalid parameter |
| `INVALID_DATE_FORMAT` | 400 | Invalid date format |
| `INVALID_DATE_RANGE` | 400 | Invalid date range |
| `VALIDATION_ERROR` | 422 | Request validation error |
| `INTERNAL_ERROR` | 500 | Internal server error |
| `SERVICE_UNAVAILABLE` | 503 | Service unavailable |

---

## 3. API Endpoints

### 3.1 Health Check

#### GET /api/health
**Description**: Checks the health status of the server, database, and Redis.

**Response Example**:
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "timestamp": "2025-11-13T21:23:43Z"
}
```

**Status Values**:
- `healthy`: All services are operational
- `unhealthy`: One or more services are unavailable

---

### 3.2 Stock Management

#### GET /api/stocks
**Description**: Retrieves the list of all stocks with optional filtering.

**Query Parameters**:
| Parameter | Type | Required | Description |
|:---|:---|:---|:---|
| `type` | string | - | Stock type filter (STOCK, ETF) |
| `theme` | string | - | Theme filter |
| `limit` | number | - | Query limit (default: 100) |
| `offset` | number | - | Page offset (default: 0) |

**Response Example**:
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
        "fee": null,
        "createdAt": "2025-01-01T00:00:00Z",
        "updatedAt": "2025-11-13T21:22:11Z"
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

**Caching**: TTL 1 hour

---

#### GET /api/stocks/{ticker}
**Description**: Retrieves detailed information of a specific stock.

**Path Parameters**:
| Parameter | Type | Required | Description |
|:---|:---|:---|:---|
| `ticker` | string | ✓ | Stock code |

**Response Example**:
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

**Error Responses**:
- `404 NOT_FOUND`: Stock with ticker '{ticker}' not found

**Caching**: TTL 1 hour

---

#### POST /api/stocks
**Description**: Creates a new stock in the database (Admin only).

**Request Body**:
```json
{
  "ticker": "034020",
  "name": "Doosan Enerbility",
  "type": "STOCK",
  "theme": "Nuclear/Power Plant/Energy",
  "fee": null
}
```

| Field | Type | Required | Description |
|:---|:---|:---|:---|
| `ticker` | string | ✓ | Stock code (unique) |
| `name` | string | ✓ | Stock name |
| `type` | string | ✓ | Stock type (STOCK/ETF) |
| `theme` | string | - | Theme classification |
| `fee` | number | - | Fee (ETF only) |

**Response Example**:
```json
{
  "success": true,
  "data": {
    "ticker": "034020",
    "name": "Doosan Enerbility",
    "type": "STOCK",
    "theme": "Nuclear/Power Plant/Energy",
    "fee": null,
    "createdAt": "2025-11-14T10:30:00Z",
    "updatedAt": "2025-11-14T10:30:00Z"
  },
  "message": "Stock '034020' created successfully",
  "timestamp": "2025-11-14T10:30:00Z"
}
```

**Error Responses**:
- `400 BAD_REQUEST`: Stock with ticker '{ticker}' already exists (DUPLICATE_TICKER)
- `400 BAD_REQUEST`: Invalid stock type. Must be 'STOCK' or 'ETF' (INVALID_STOCK_TYPE)
- `500 INTERNAL_ERROR`: Failed to create stock

**Status Code**: 201 Created

**Note**: This endpoint invalidates all stock list caches.

---

#### PUT /api/stocks/{ticker}
**Description**: Updates an existing stock's information (Admin only).

**Path Parameters**:
| Parameter | Type | Required | Description |
|:---|:---|:---|:---|
| `ticker` | string | ✓ | Stock code |

**Request Body**:
```json
{
  "name": "Doosan Enerbility (Updated)",
  "theme": "Nuclear/Power Plant/Energy/Updated"
}
```

| Field | Type | Required | Description |
|:---|:---|:---|:---|
| `name` | string | - | Stock name |
| `type` | string | - | Stock type (STOCK/ETF) |
| `theme` | string | - | Theme classification |
| `fee` | number | - | Fee (ETF only) |

**Response Example**:
```json
{
  "success": true,
  "data": {
    "ticker": "034020",
    "name": "Doosan Enerbility (Updated)",
    "type": "STOCK",
    "theme": "Nuclear/Power Plant/Energy/Updated",
    "fee": null,
    "createdAt": "2025-01-01T00:00:00Z",
    "updatedAt": "2025-11-14T10:30:00Z"
  },
  "message": "Stock '034020' updated successfully",
  "timestamp": "2025-11-14T10:30:00Z"
}
```

**Error Responses**:
- `404 NOT_FOUND`: Stock with ticker '{ticker}' not found
- `400 BAD_REQUEST`: Invalid stock type. Must be 'STOCK' or 'ETF' (INVALID_STOCK_TYPE)
- `500 INTERNAL_ERROR`: Failed to update stock

**Note**: Only provided fields are updated. This endpoint invalidates related caches.

---

#### DELETE /api/stocks/{ticker}
**Description**: Deletes a stock from the database (Admin only).

**Path Parameters**:
| Parameter | Type | Required | Description |
|:---|:---|:---|:---|
| `ticker` | string | ✓ | Stock code |

**Response Example**:
```json
{
  "success": true,
  "data": {
    "ticker": "034020"
  },
  "message": "Stock '034020' deleted successfully",
  "timestamp": "2025-11-14T10:30:00Z"
}
```

**Error Responses**:
- `404 NOT_FOUND`: Stock with ticker '{ticker}' not found
- `500 INTERNAL_ERROR`: Failed to delete stock

**Note**: Deleting a stock may require separate handling of related price data, trading trend data, and news data. This endpoint invalidates related caches.

---

### 3.3 Price Data

#### GET /api/prices/{ticker}
**Description**: Retrieves price data of a specific stock with optional date range filtering.

**Path Parameters**:
| Parameter | Type | Required | Description |
|:---|:---|:---|:---|
| `ticker` | string | ✓ | Stock code |

**Query Parameters**:
| Parameter | Type | Required | Description |
|:---|:---|:---|:---|
| `start_date` | string | - | Start date (YYYY-MM-DD format) |
| `end_date` | string | - | End date (YYYY-MM-DD format) |
| `limit` | number | - | Page size (optional) |
| `offset` | number | - | Page offset (default: 0) |

**Response Example**:
```json
{
  "success": true,
  "data": {
    "prices": [
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
    ],
    "total": 100,
    "limit": 100,
    "offset": 0
  },
  "message": "",
  "timestamp": "2025-11-13T21:23:43Z"
}
```

**Error Responses**:
- `404 NOT_FOUND`: Stock with ticker '{ticker}' not found
- `400 INVALID_DATE_FORMAT`: Invalid date format. Expected YYYY-MM-DD
- `400 INVALID_DATE_RANGE`: start_date must be before or equal to end_date

**Caching**: TTL 30 minutes

**Notes**:
- Results are sorted by date in descending order (newest first)
- If no date range is specified, returns all available price data
- Date filtering is inclusive (start_date <= date <= end_date)

---

### 3.4 Trading Trend (Planned)

#### GET /api/stocks/{ticker}/trading
**Description**: Retrieves trading trend data of a specific stock.

**Status**: ⚠️ Structure only, implementation pending

**Path Parameters**:
| Parameter | Type | Required | Description |
|:---|:---|:---|:---|
| `ticker` | string | ✓ | Stock code |

**Query Parameters**:
| Parameter | Type | Required | Description |
|:---|:---|:---|:---|
| `date` | string | - | Specific date query (YYYY-MM-DD, default: latest) |

---

### 3.5 News (Planned)

#### GET /api/stocks/{ticker}/news
**Description**: Retrieves news list of a specific stock.

**Status**: ⚠️ Structure only, implementation pending

**Path Parameters**:
| Parameter | Type | Required | Description |
|:---|:---|:---|:---|
| `ticker` | string | ✓ | Stock code |

**Query Parameters**:
| Parameter | Type | Required | Description |
|:---|:---|:---|:---|
| `limit` | number | - | Query limit (default: 10, max: 50) |
| `offset` | number | - | Page offset (default: 0) |

---

### 3.6 Chart Data (Planned)

#### GET /api/stocks/{ticker}/chart
**Description**: Retrieves chart data of a specific stock.

**Status**: ⚠️ Structure only, implementation pending

**Path Parameters**:
| Parameter | Type | Required | Description |
|:---|:---|:---|:---|
| `ticker` | string | ✓ | Stock code |

**Query Parameters**:
| Parameter | Type | Required | Description |
|:---|:---|:---|:---|
| `days` | number | - | Query period (days, default: 6, max: 30) |

---

### 3.7 Data Refresh (Planned)

#### POST /api/refresh
**Description**: Manually refreshes data for specified stocks.

**Status**: ⚠️ Structure only, implementation pending

**Request Body**:
```json
{
  "tickers": ["034020", "005930"]
}
```

| Field | Type | Required | Description |
|:---|:---|:---|:---|
| `tickers` | array | - | Array of stock codes to refresh (if empty, refresh all) |

---

### 3.8 Data Collection (Phase 2)

#### POST /api/data/collect/prices/{ticker}
**Description**: Collects price data from Naver Finance for a specific stock and saves it to the database.

**Path Parameters**:
| Parameter | Type | Required | Description |
|:---|:---|:---|:---|
| `ticker` | string | ✓ | Stock code |

**Query Parameters**:
| Parameter | Type | Required | Description |
|:---|:---|:---|:---|
| `days` | number | - | Number of days to collect (default: 10, min: 1, max: 365) |

**Response Example**:
```json
{
  "success": true,
  "data": {
    "ticker": "487240",
    "saved_count": 10,
    "days": 10
  },
  "message": "Price data collected successfully. 10 records saved.",
  "timestamp": "2025-11-14T10:30:00Z"
}
```

**Error Responses**:
- `404 NOT_FOUND`: Stock with ticker '{ticker}' not found
- `400 INVALID_PARAMETER`: Invalid days parameter (must be between 1 and 365)
- `500 INTERNAL_ERROR`: Failed to collect price data

---

#### POST /api/data/collect/trading/{ticker}
**Description**: Collects trading trend data from Naver Finance for a specific stock and saves it to the database.

**Path Parameters**:
| Parameter | Type | Required | Description |
|:---|:---|:---|:---|
| `ticker` | string | ✓ | Stock code |

**Query Parameters**:
| Parameter | Type | Required | Description |
|:---|:---|:---|:---|
| `days` | number | - | Number of days to collect (default: 10, min: 1, max: 365) |
| `start_date` | string | - | Start date (YYYY-MM-DD format, optional) |
| `end_date` | string | - | End date (YYYY-MM-DD format, optional) |

**Response Example**:
```json
{
  "success": true,
  "data": {
    "ticker": "487240",
    "saved_count": 10,
    "days": 10,
    "start_date": "2025-11-01",
    "end_date": "2025-11-10"
  },
  "message": "Trading flow data collected successfully. 10 records saved.",
  "timestamp": "2025-11-14T10:30:00Z"
}
```

**Error Responses**:
- `404 NOT_FOUND`: Stock with ticker '{ticker}' not found
- `400 INVALID_DATE_FORMAT`: Invalid date format. Expected YYYY-MM-DD
- `400 INVALID_DATE_RANGE`: start_date must be before or equal to end_date
- `500 INTERNAL_ERROR`: Failed to collect trading flow data

---

#### POST /api/data/collect/news/{ticker}
**Description**: Collects news data from Naver Finance for a specific stock and saves it to the database.

**Path Parameters**:
| Parameter | Type | Required | Description |
|:---|:---|:---|:---|
| `ticker` | string | ✓ | Stock code |

**Query Parameters**:
| Parameter | Type | Required | Description |
|:---|:---|:---|:---|
| `max_items` | number | - | Maximum number of news items to collect (default: 50, min: 1, max: 200) |

**Response Example**:
```json
{
  "success": true,
  "data": {
    "ticker": "487240",
    "saved_count": 50,
    "max_items": 50
  },
  "message": "News data collected successfully. 50 records saved.",
  "timestamp": "2025-11-14T10:30:00Z"
}
```

**Error Responses**:
- `404 NOT_FOUND`: Stock with ticker '{ticker}' not found
- `400 INVALID_PARAMETER`: Invalid max_items parameter (must be between 1 and 200)
- `500 INTERNAL_ERROR`: Failed to collect news data

---

### 3.9 Scheduler Management (Phase 2)

#### GET /api/scheduler/status
**Description**: Retrieves the current status of the data collection scheduler.

**Response Example**:
```json
{
  "success": true,
  "data": {
    "is_running": true,
    "interval_seconds": 30,
    "next_run_time": "2025-11-14T10:30:30Z",
    "last_run_time": "2025-11-14T10:30:00Z",
    "last_run_status": "success",
    "last_run_error": null
  },
  "message": "Scheduler status retrieved successfully",
  "timestamp": "2025-11-14T10:30:05Z"
}
```

**Status Fields**:
- `is_running`: Whether the scheduler is currently running
- `interval_seconds`: Data collection interval in seconds
- `next_run_time`: Next scheduled run time (ISO 8601 format)
- `last_run_time`: Last execution time (ISO 8601 format)
- `last_run_status`: Status of last run ("success" or "error")
- `last_run_error`: Error message if last run failed (null if successful)

**Error Responses**:
- `500 INTERNAL_ERROR`: Failed to get scheduler status

---

#### POST /api/scheduler/start
**Description**: Starts the data collection scheduler. If already running, restarts it with the specified interval.

**Query Parameters**:
| Parameter | Type | Required | Description |
|:---|:---|:---|:---|
| `interval_seconds` | number | - | Data collection interval in seconds (default: 30, min: 10, max: 3600) |

**Response Example**:
```json
{
  "success": true,
  "data": {
    "is_running": true,
    "interval_seconds": 30,
    "message": "Scheduler started successfully"
  },
  "message": "Scheduler started successfully",
  "timestamp": "2025-11-14T10:30:00Z"
}
```

**Error Responses**:
- `400 INVALID_PARAMETER`: Invalid interval_seconds parameter (must be between 10 and 3600)
- `500 INTERNAL_ERROR`: Failed to start scheduler

---

#### POST /api/scheduler/stop
**Description**: Stops the running data collection scheduler.

**Response Example**:
```json
{
  "success": true,
  "data": {
    "is_running": false,
    "message": "Scheduler stopped successfully"
  },
  "message": "Scheduler stopped successfully",
  "timestamp": "2025-11-14T10:30:00Z"
}
```

**Error Responses**:
- `500 INTERNAL_ERROR`: Failed to stop scheduler

---

## 4. Caching Strategy

### 4.1 Cache Structure (Redis)
- **Cache Key Pattern**: `{prefix}:{type}:{identifier}`
- **Examples**:
  - `stocks:list:type:STOCK:limit:100:offset:0`: Stock list with filters
  - `stocks:detail:034020`: Stock detail
  - `prices:034020:start:2025-01-01:end:2025-12-31:limit:100:offset:0`: Price data with filters

### 4.2 Cache TTL (Time To Live)
| Data Type | TTL | Description |
|:---|:---|:---|
| Stock Information | 1 hour | Low change frequency |
| Price Data | 30 minutes | Historical data |
| Trading Trend | 30 seconds | Real-time data (when implemented) |
| News Data | 10 minutes | Same as update cycle (when implemented) |
| Chart Data | 1 minute | Daily data (when implemented) |

### 4.3 Cache Invalidation Strategy
- Automatic cache update on data collection
- Delete and regenerate related cache on manual refresh
- Automatic deletion on TTL expiration

---

## 5. Data Validation Rules

For detailed data validation rules, please refer to:
- **`docs/eng/05-Data-API-Design-Specification.md`** (Section 4: Data Validation Rules)

This includes validation rules for:
- Price Data
- Trading Trend
- News Data
- Stock Information

---

## 6. Performance Optimization

### 6.1 API Optimization
- Response data compression (gzip)
- Pagination application
- Parallel processing: Parallel processing when querying multiple stocks
- Rate Limiting: API call limits (e.g., 100 requests per second)

### 6.2 Caching
- Redis caching for frequently accessed data
- Cache key strategy for efficient invalidation
- TTL-based automatic expiration

---

## 7. Swagger UI

Interactive API documentation is available at:
- **Development**: http://localhost:8000/docs
- **Production**: {BASE_URL}/docs

All endpoints are automatically documented with request/response examples.

---

## 8. Version History

### Version 1.0.0 (Phase 1.4)
- Health Check endpoint
- Stock list and detail endpoints
- Stock management endpoints (POST, PUT, DELETE) - Admin only
- Price data endpoint with date range filtering
- Basic error handling
- Redis caching implementation

### Version 2.0.0 (Phase 2)
- Data collection endpoints
  - Price data collection API (`POST /api/data/collect/prices/{ticker}`)
  - Trading trend data collection API (`POST /api/data/collect/trading/{ticker}`)
  - News data collection API (`POST /api/data/collect/news/{ticker}`)
- Scheduler management endpoints
  - Scheduler status API (`GET /api/scheduler/status`)
  - Scheduler start/stop APIs (`POST /api/scheduler/start`, `POST /api/scheduler/stop`)
- Data validation utilities
- Automatic data collection scheduler (30-second interval)

### Planned (Phase 3+)
- Trading trend endpoint (GET)
- News endpoint (GET)
- Chart data endpoint
- Data refresh endpoint

