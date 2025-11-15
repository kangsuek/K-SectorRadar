# API Specification

> **Project**: K-SectorRadar
> **API Version**: 1.0
> **Last Updated**: 2025-11-15

---

## Table of Contents

1. [API Overview](#1-api-overview)
2. [Common Response Format](#2-common-response-format)
3. [Implemented Endpoints (Phase 1)](#3-implemented-endpoints-phase-1)
4. [Planned Endpoints (Phase 2+)](#4-planned-endpoints-phase-2)
5. [Error Handling](#5-error-handling)
6. [Schema Definitions](#6-schema-definitions)

---

## 1. API Overview

### 1.1 General Information

- **Base URL**: `/api`
- **Protocol**: HTTP/HTTPS
- **Response Format**: JSON
- **Character Encoding**: UTF-8
- **Authentication**: None (will be added in future versions)

### 1.2 API Documentation

The K-SectorRadar API provides automatically generated interactive documentation:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### 1.3 CORS Configuration

The API accepts requests from the following origins:
- `http://localhost:5173` (Vite development server)
- `http://localhost:3000` (Alternative frontend server)

### 1.4 Caching Strategy

The API implements Redis-based caching with the following TTL (Time To Live) values:

| Data Type | TTL | Description |
|-----------|-----|-------------|
| Stock Information | 1 hour (3600s) | Low change frequency |
| Price Data | 30 minutes (1800s) | Real-time data |
| Trading Trends | 30 seconds | Real-time data (future) |
| News Data | 10 minutes | Same as update cycle (future) |

---

## 2. Common Response Format

### 2.1 Success Response

All successful API responses follow this structure:

```json
{
  "success": true,
  "data": {},
  "message": "",
  "timestamp": "2025-11-15T10:00:00Z"
}
```

**Fields**:
- `success` (boolean): Always `true` for successful responses
- `data` (any): Response payload (varies by endpoint)
- `message` (string): Optional message (usually empty for success)
- `timestamp` (string | null): ISO 8601 timestamp of the response

### 2.2 Error Response

All error responses follow this structure:

```json
{
  "success": false,
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "detail": "Detailed error information",
  "timestamp": "2025-11-15T10:00:00Z"
}
```

**Fields**:
- `success` (boolean): Always `false` for error responses
- `error` (string): Human-readable error message
- `error_code` (string | null): Machine-readable error code
- `detail` (string | null): Additional error details (may be omitted in production)
- `timestamp` (string | null): ISO 8601 timestamp of the error

---

## 3. Implemented Endpoints (Phase 1)

### 3.1 Health Check

Check the health status of the API server, database, and Redis cache.

#### Endpoint

```
GET /api/health
```

#### Request Parameters

None

#### Response (Success - Healthy)

**Status Code**: `200 OK`

```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "timestamp": "2025-11-15T10:00:00.123456"
}
```

#### Response (Success - Unhealthy)

**Status Code**: `200 OK`

```json
{
  "status": "unhealthy",
  "database": "disconnected",
  "redis": "connected",
  "timestamp": "2025-11-15T10:00:00.123456"
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Overall system status (`healthy` or `unhealthy`) |
| `database` | string | Database connection status (`connected` or `disconnected`) |
| `redis` | string | Redis connection status (`connected` or `disconnected`) |
| `timestamp` | string | ISO 8601 timestamp |

#### Curl Example

```bash
curl -X GET "http://localhost:8000/api/health"
```

---

### 3.2 Get Stock List

Retrieve a list of all stocks and ETFs with optional filtering and pagination.

#### Endpoint

```
GET /api/stocks
```

#### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `type` | string | No | - | Filter by stock type (`STOCK` or `ETF`) |
| `theme` | string | No | - | Filter by investment theme |
| `limit` | integer | No | 100 | Maximum number of results to return |
| `offset` | integer | No | 0 | Number of results to skip (for pagination) |

#### Response (Success)

**Status Code**: `200 OK`

```json
{
  "success": true,
  "data": {
    "stocks": [
      {
        "ticker": "034020",
        "name": "두산에너빌리티",
        "type": "STOCK",
        "theme": "Nuclear/Power Plant/Energy",
        "fee": null,
        "createdAt": "2025-01-01T00:00:00Z",
        "updatedAt": "2025-11-13T21:22:11Z"
      },
      {
        "ticker": "442320",
        "name": "KB RISE 글로벌원자력 iSelect ETF",
        "type": "ETF",
        "theme": "Nuclear Power",
        "fee": 0.500000,
        "createdAt": "2025-01-01T00:00:00Z",
        "updatedAt": "2025-11-13T21:22:11Z"
      }
    ],
    "total": 6,
    "limit": 100,
    "offset": 0
  },
  "message": "",
  "timestamp": "2025-11-15T10:00:00Z"
}
```

#### Response Data Fields

| Field | Type | Description |
|-------|------|-------------|
| `stocks` | array | Array of stock objects |
| `stocks[].ticker` | string | Stock ticker code (unique identifier) |
| `stocks[].name` | string | Stock or ETF name |
| `stocks[].type` | string | Type of security (`STOCK` or `ETF`) |
| `stocks[].theme` | string \| null | Investment theme or sector |
| `stocks[].fee` | number \| null | Management fee (ETF only) |
| `stocks[].createdAt` | string | ISO 8601 creation timestamp |
| `stocks[].updatedAt` | string | ISO 8601 last update timestamp |
| `total` | integer | Total number of stocks matching the filter |
| `limit` | integer | Page size limit |
| `offset` | integer | Pagination offset |

#### Caching

- **Cached**: Yes
- **TTL**: 1 hour (3600 seconds)
- **Cache Key Pattern**: `stocks:list:type:{type}:theme:{theme}:limit:{limit}:offset:{offset}`

#### Curl Examples

Get all stocks:
```bash
curl -X GET "http://localhost:8000/api/stocks"
```

Filter by type (ETF only):
```bash
curl -X GET "http://localhost:8000/api/stocks?type=ETF"
```

Filter by theme:
```bash
curl -X GET "http://localhost:8000/api/stocks?theme=Nuclear%20Power"
```

With pagination:
```bash
curl -X GET "http://localhost:8000/api/stocks?limit=10&offset=0"
```

---

### 3.3 Get Stock Detail

Retrieve detailed information for a specific stock or ETF.

#### Endpoint

```
GET /api/stocks/{ticker}
```

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ticker` | string | Yes | Stock ticker code (e.g., `034020`) |

#### Response (Success)

**Status Code**: `200 OK`

```json
{
  "success": true,
  "data": {
    "ticker": "034020",
    "name": "두산에너빌리티",
    "type": "STOCK",
    "theme": "Nuclear/Power Plant/Energy",
    "fee": null,
    "createdAt": "2025-01-01T00:00:00Z",
    "updatedAt": "2025-11-13T21:22:11Z"
  },
  "message": "",
  "timestamp": "2025-11-15T10:00:00Z"
}
```

#### Response (Not Found)

**Status Code**: `404 Not Found`

```json
{
  "success": false,
  "error": "Stock with ticker '123456' not found",
  "error_code": "NOT_FOUND",
  "detail": "Stock with ticker '123456' not found",
  "timestamp": "2025-11-15T10:00:00Z"
}
```

#### Response Data Fields

| Field | Type | Description |
|-------|------|-------------|
| `ticker` | string | Stock ticker code (unique identifier) |
| `name` | string | Stock or ETF name |
| `type` | string | Type of security (`STOCK` or `ETF`) |
| `theme` | string \| null | Investment theme or sector |
| `fee` | number \| null | Management fee (ETF only) |
| `createdAt` | string | ISO 8601 creation timestamp |
| `updatedAt` | string | ISO 8601 last update timestamp |

#### Caching

- **Cached**: Yes
- **TTL**: 1 hour (3600 seconds)
- **Cache Key Pattern**: `stocks:detail:{ticker}`

#### Curl Examples

Get stock detail:
```bash
curl -X GET "http://localhost:8000/api/stocks/034020"
```

Get ETF detail:
```bash
curl -X GET "http://localhost:8000/api/stocks/442320"
```

---

### 3.4 Get Price Data

Retrieve historical and real-time price data for a specific stock or ETF.

#### Endpoint

```
GET /api/prices/{ticker}
```

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ticker` | string | Yes | Stock ticker code (e.g., `034020`) |

#### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `start_date` | string | No | - | Start date in `YYYY-MM-DD` format (e.g., `2025-01-01`) |
| `end_date` | string | No | - | End date in `YYYY-MM-DD` format (e.g., `2025-12-31`) |
| `limit` | integer | No | - | Maximum number of results to return |
| `offset` | integer | No | 0 | Number of results to skip (for pagination) |

#### Response (Success)

**Status Code**: `200 OK`

```json
{
  "success": true,
  "data": {
    "prices": [
      {
        "id": 1,
        "ticker": "034020",
        "date": "2025-11-13",
        "timestamp": "2025-11-13T15:30:00Z",
        "currentPrice": 83100.00,
        "changeRate": 2.50,
        "changeAmount": 2025.00,
        "openPrice": 82000.00,
        "highPrice": 83500.00,
        "lowPrice": 81800.00,
        "volume": 7900000,
        "weeklyChangeRate": 5.20,
        "previousClose": 81075.00
      }
    ],
    "total": 1,
    "limit": null,
    "offset": 0
  },
  "message": "",
  "timestamp": "2025-11-15T10:00:00Z"
}
```

#### Response (Stock Not Found)

**Status Code**: `404 Not Found`

```json
{
  "success": false,
  "error": "Stock with ticker '123456' not found",
  "error_code": "NOT_FOUND",
  "detail": "Stock with ticker '123456' not found",
  "timestamp": "2025-11-15T10:00:00Z"
}
```

#### Response (Invalid Date Format)

**Status Code**: `400 Bad Request`

```json
{
  "success": false,
  "error": "Invalid start_date format. Expected YYYY-MM-DD, got: 2025/01/01",
  "error_code": "INVALID_DATE_FORMAT",
  "detail": "Invalid start_date format. Expected YYYY-MM-DD, got: 2025/01/01",
  "timestamp": "2025-11-15T10:00:00Z"
}
```

#### Response (Invalid Date Range)

**Status Code**: `400 Bad Request`

```json
{
  "success": false,
  "error": "start_date must be before or equal to end_date",
  "error_code": "INVALID_DATE_RANGE",
  "detail": "start_date must be before or equal to end_date",
  "timestamp": "2025-11-15T10:00:00Z"
}
```

#### Response Data Fields

| Field | Type | Description |
|-------|------|-------------|
| `prices` | array | Array of price objects |
| `prices[].id` | integer | Unique price record ID |
| `prices[].ticker` | string | Stock ticker code |
| `prices[].date` | string | Trading date (YYYY-MM-DD) |
| `prices[].timestamp` | string | ISO 8601 data collection timestamp |
| `prices[].currentPrice` | number | Current/closing price |
| `prices[].changeRate` | number \| null | Price change rate (%) |
| `prices[].changeAmount` | number \| null | Price change amount |
| `prices[].openPrice` | number \| null | Opening price |
| `prices[].highPrice` | number \| null | Highest price |
| `prices[].lowPrice` | number \| null | Lowest price |
| `prices[].volume` | number \| null | Trading volume |
| `prices[].weeklyChangeRate` | number \| null | Weekly change rate (%) |
| `prices[].previousClose` | number \| null | Previous day's closing price |
| `total` | integer | Total number of price records matching the filter |
| `limit` | integer \| null | Page size limit |
| `offset` | integer | Pagination offset |

#### Sorting

Price data is returned in **descending order by date** (most recent first).

#### Caching

- **Cached**: Yes
- **TTL**: 30 minutes (1800 seconds)
- **Cache Key Pattern**: `prices:{ticker}:start:{start_date}:end:{end_date}:limit:{limit}:offset:{offset}`

#### Curl Examples

Get all price data for a stock:
```bash
curl -X GET "http://localhost:8000/api/prices/034020"
```

Get price data for a specific date range:
```bash
curl -X GET "http://localhost:8000/api/prices/034020?start_date=2025-01-01&end_date=2025-12-31"
```

Get recent price data with pagination:
```bash
curl -X GET "http://localhost:8000/api/prices/034020?limit=10&offset=0"
```

---

## 4. Planned Endpoints (Phase 2+)

The following endpoints have basic routing structure in place but are not yet fully implemented. They will be completed in Phase 2 and beyond.

### 4.1 Get Trading Trends

**Endpoint**: `GET /api/stocks/{ticker}/trading`

**Status**: TODO (Phase 2)

**Description**: Retrieve investor trading trend data (individual, institutional, and foreign investors).

**Query Parameters**:
- `date` (string, optional): Specific date query (YYYY-MM-DD, default: latest)

---

### 4.2 Get News

**Endpoint**: `GET /api/stocks/{ticker}/news`

**Status**: TODO (Phase 2)

**Description**: Retrieve news articles related to a specific stock or ETF.

**Query Parameters**:
- `limit` (integer, optional): Query limit (default: 10, max: 50)
- `offset` (integer, optional): Page offset (default: 0)

---

### 4.3 Get Chart Data

**Endpoint**: `GET /api/stocks/{ticker}/chart`

**Status**: TODO (Phase 2)

**Description**: Retrieve chart data for a specific stock or ETF.

**Query Parameters**:
- `days` (integer, optional): Query period in days (default: 6, max: 30)

---

## 5. Error Handling

### 5.1 Error Response Structure

See [Section 2.2](#22-error-response) for the general error response format.

### 5.2 HTTP Status Codes

| Status Code | Error Code | Description |
|-------------|------------|-------------|
| `400` | `BAD_REQUEST` | Invalid request parameters or format |
| `400` | `INVALID_DATE_FORMAT` | Date parameter is not in YYYY-MM-DD format |
| `400` | `INVALID_DATE_RANGE` | start_date is after end_date |
| `404` | `NOT_FOUND` | Requested resource (stock, price, etc.) not found |
| `422` | `VALIDATION_ERROR` | Request validation failed (Pydantic validation) |
| `500` | `INTERNAL_ERROR` | Internal server error |
| `500` | `DATABASE_ERROR` | Database connection or query error |

### 5.3 Error Code Details

#### 5.3.1 NOT_FOUND (404)

**Trigger**: When a requested resource does not exist in the database.

**Example**:
```json
{
  "success": false,
  "error": "Stock with ticker '999999' not found",
  "error_code": "NOT_FOUND",
  "detail": "Stock with ticker '999999' not found",
  "timestamp": "2025-11-15T10:00:00Z"
}
```

#### 5.3.2 BAD_REQUEST (400)

**Trigger**: When request parameters are invalid or incorrectly formatted.

**Example**:
```json
{
  "success": false,
  "error": "Invalid request parameters",
  "error_code": "BAD_REQUEST",
  "detail": "Parameter 'limit' must be a positive integer",
  "timestamp": "2025-11-15T10:00:00Z"
}
```

#### 5.3.3 INVALID_DATE_FORMAT (400)

**Trigger**: When date parameters are not in YYYY-MM-DD format.

**Example**:
```json
{
  "success": false,
  "error": "Invalid start_date format. Expected YYYY-MM-DD, got: 2025/01/01",
  "error_code": "INVALID_DATE_FORMAT",
  "detail": "Invalid start_date format. Expected YYYY-MM-DD, got: 2025/01/01",
  "timestamp": "2025-11-15T10:00:00Z"
}
```

#### 5.3.4 INVALID_DATE_RANGE (400)

**Trigger**: When start_date is after end_date.

**Example**:
```json
{
  "success": false,
  "error": "start_date must be before or equal to end_date",
  "error_code": "INVALID_DATE_RANGE",
  "detail": "start_date must be before or equal to end_date",
  "timestamp": "2025-11-15T10:00:00Z"
}
```

#### 5.3.5 VALIDATION_ERROR (422)

**Trigger**: When Pydantic request validation fails.

**Example**:
```json
{
  "success": false,
  "error": "Validation error",
  "error_code": "VALIDATION_ERROR",
  "detail": "Field 'ticker' is required",
  "timestamp": "2025-11-15T10:00:00Z"
}
```

#### 5.3.6 INTERNAL_ERROR (500)

**Trigger**: When an unexpected server error occurs.

**Example**:
```json
{
  "success": false,
  "error": "Internal server error",
  "error_code": "INTERNAL_ERROR",
  "detail": null,
  "timestamp": "2025-11-15T10:00:00Z"
}
```

**Note**: The `detail` field may be omitted or null in production environments for security reasons.

---

## 6. Schema Definitions

### 6.1 Common Schemas

#### 6.1.1 APIResponse

**Purpose**: Wrapper for all successful API responses.

**Fields**:
- `success` (boolean): Always `true`
- `data` (any): Response payload
- `message` (string): Optional message
- `timestamp` (string | null): ISO 8601 timestamp

**Example**:
```json
{
  "success": true,
  "data": {},
  "message": "",
  "timestamp": "2025-11-15T10:00:00Z"
}
```

#### 6.1.2 ErrorResponse

**Purpose**: Wrapper for all error responses.

**Fields**:
- `success` (boolean): Always `false`
- `error` (string): Human-readable error message
- `error_code` (string | null): Machine-readable error code
- `detail` (string | null): Additional error details
- `timestamp` (string | null): ISO 8601 timestamp

**Example**:
```json
{
  "success": false,
  "error": "Resource not found",
  "error_code": "NOT_FOUND",
  "detail": "Stock with ticker '123456' not found",
  "timestamp": "2025-11-15T10:00:00Z"
}
```

### 6.2 Stock Schemas

#### 6.2.1 StockResponse

**Purpose**: Represents a single stock or ETF.

**Fields**:
- `ticker` (string): Stock ticker code
- `name` (string): Stock or ETF name
- `type` (string): Type (`STOCK` or `ETF`)
- `theme` (string | null): Investment theme
- `fee` (number | null): Management fee (ETF only)
- `createdAt` (string): ISO 8601 creation timestamp
- `updatedAt` (string): ISO 8601 last update timestamp

**Example**:
```json
{
  "ticker": "034020",
  "name": "두산에너빌리티",
  "type": "STOCK",
  "theme": "Nuclear/Power Plant/Energy",
  "fee": null,
  "createdAt": "2025-01-01T00:00:00Z",
  "updatedAt": "2025-11-13T21:22:11Z"
}
```

#### 6.2.2 StockListResponse

**Purpose**: Represents a paginated list of stocks.

**Fields**:
- `stocks` (array): Array of `StockResponse` objects
- `total` (integer): Total number of stocks matching the filter
- `limit` (integer): Page size limit
- `offset` (integer): Pagination offset

**Example**:
```json
{
  "stocks": [...],
  "total": 6,
  "limit": 100,
  "offset": 0
}
```

### 6.3 Price Schemas

#### 6.3.1 PriceResponse

**Purpose**: Represents a single price data record.

**Fields**:
- `id` (integer): Unique price record ID
- `ticker` (string): Stock ticker code
- `date` (string): Trading date (YYYY-MM-DD)
- `timestamp` (string): ISO 8601 collection timestamp
- `currentPrice` (number): Current/closing price
- `changeRate` (number | null): Price change rate (%)
- `changeAmount` (number | null): Price change amount
- `openPrice` (number | null): Opening price
- `highPrice` (number | null): Highest price
- `lowPrice` (number | null): Lowest price
- `volume` (number | null): Trading volume
- `weeklyChangeRate` (number | null): Weekly change rate (%)
- `previousClose` (number | null): Previous day's closing price

**Example**:
```json
{
  "id": 1,
  "ticker": "034020",
  "date": "2025-11-13",
  "timestamp": "2025-11-13T15:30:00Z",
  "currentPrice": 83100.00,
  "changeRate": 2.50,
  "changeAmount": 2025.00,
  "openPrice": 82000.00,
  "highPrice": 83500.00,
  "lowPrice": 81800.00,
  "volume": 7900000,
  "weeklyChangeRate": 5.20,
  "previousClose": 81075.00
}
```

#### 6.3.2 PriceListResponse

**Purpose**: Represents a paginated list of price data records.

**Fields**:
- `prices` (array): Array of `PriceResponse` objects
- `total` (integer): Total number of price records matching the filter
- `limit` (integer | null): Page size limit
- `offset` (integer): Pagination offset

**Example**:
```json
{
  "prices": [...],
  "total": 100,
  "limit": 10,
  "offset": 0
}
```

---

## Appendix

### A. API Client Examples

#### A.1 Python (requests)

```python
import requests

# Get all stocks
response = requests.get("http://localhost:8000/api/stocks")
data = response.json()
print(data)

# Get stock detail
response = requests.get("http://localhost:8000/api/stocks/034020")
stock = response.json()["data"]
print(stock)

# Get price data with date range
params = {
    "start_date": "2025-01-01",
    "end_date": "2025-12-31",
    "limit": 10
}
response = requests.get("http://localhost:8000/api/prices/034020", params=params)
prices = response.json()["data"]
print(prices)
```

#### A.2 JavaScript (fetch)

```javascript
// Get all stocks
fetch('http://localhost:8000/api/stocks')
  .then(response => response.json())
  .then(data => console.log(data));

// Get stock detail
fetch('http://localhost:8000/api/stocks/034020')
  .then(response => response.json())
  .then(data => console.log(data.data));

// Get price data with date range
const params = new URLSearchParams({
  start_date: '2025-01-01',
  end_date: '2025-12-31',
  limit: 10
});
fetch(`http://localhost:8000/api/prices/034020?${params}`)
  .then(response => response.json())
  .then(data => console.log(data.data));
```

### B. Related Documentation

- **[DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md)** - Database schema documentation
- **[DEVELOPMENT_GUIDE.md](./DEVELOPMENT_GUIDE.md)** - Development setup guide
- **[03-Data-API-Design-Specification.md](./03-Data-API-Design-Specification.md)** - Original API design specification

---

**Document Version**: 1.0
**Author**: K-SectorRadar Development Team
**Last Updated**: 2025-11-15
