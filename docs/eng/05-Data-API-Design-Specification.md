## 1. Document Overview

### 1.1 Purpose
This document defines the data models (JSON schemas) for the K-SectorRadar project.

### 1.2 Scope
This document includes data model definitions, JSON schemas, and field descriptions. For API endpoints and database schema, please refer to the dedicated documents.

### 1.3 References
- **API Specification**: See `docs/eng/03-API_SPECIFICATION.md` for REST API endpoints
- **Database Schema**: See `docs/eng/04-DATABASE_SCHEMA.md` for database table definitions
- **Requirements Specification**: `docs/eng/01-Requirements-Specification.md`
- **System Design Document**: `docs/eng/02-System-Technology-Stack-Specification.md`

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

## 3. Related Documents
- **Database Schema**: See `docs/eng/04-DATABASE_SCHEMA.md`
- **API Specification**: See `docs/eng/03-API_SPECIFICATION.md`

---

## 4. Data Validation Rules

### 4.1 Price Data Validation
- Current price > 0
- High price >= Low price
- Current price exists within open, high, low price range
- Volume >= 0
- Change rate range: -100% ~ +100% (theoretical limit)

### 4.2 Trading Trend Validation
- Individual + Institution + Foreign = Total volume (approximate, ±5% allowed)
- Verify each value is numeric type
- Validate reasonableness of trading volume values

### 4.3 News Data Validation
- Title is not empty (minimum 1 character)
- URL is valid format (http:// or https://)
- Published timestamp is valid date format (ISO 8601)
- URL duplication prevention

### 4.4 Stock Information Validation
- Ticker is 6-digit numeric string
- Name is minimum 1 character, maximum 100 characters
- Type only allows 'STOCK' or 'ETF'
- Fee is required for ETF, null for STOCK

---

## 5. Additional Information
- **Caching Strategy**: See `docs/eng/03-API_SPECIFICATION.md` (Section 4)
- **Performance Optimization**: See `docs/eng/03-API_SPECIFICATION.md` (Section 6) and `docs/eng/04-DATABASE_SCHEMA.md` (Section 9)

---

