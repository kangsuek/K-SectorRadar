# API Specification

## 1. Document Overview

### 1.1 Purpose
This document defines the REST API endpoints for the K-SectorRadar project.

### 1.2 Scope
This document includes API endpoint definitions, request/response formats, error handling, and caching strategies.

### 1.3 References
- Data Models: See `docs/eng/05-Data-API-Design-Specification.md` (Section 2)
- Database Schema: See `docs/eng/04-DATABASE_SCHEMA.md`
- Requirements Specification: `docs/eng/01-Requirements-Specification.md`

---

## 2. API Overview

### 2.1 Base Information
- **Base URL**: `/api`
- **Authentication**: No authentication in initial version (expandable in future)
- **Response Format**: JSON
- **Character Encoding**: UTF-8

### 2.2 Response Format

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
- Price data endpoint with date range filtering
- Basic error handling
- Redis caching implementation

### Planned (Phase 2+)
- Trading trend endpoint
- News endpoint
- Chart data endpoint
- Data refresh endpoint

