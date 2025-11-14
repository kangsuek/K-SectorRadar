## 1. Document Overview

### 1.1 Purpose
This document clearly defines the functional and non-functional requirements of the K-SectorRadar project and provides development and verification criteria.

### 1.2 Scope
This document includes functional and non-functional requirements of the K-SectorRadar system.

### 1.3 References
- Initial project development requirements and functional specification draft

### 1.4 Project Overview

#### 1.4.1 Project Information

| Item | Content |
|------|---------|
| Project Name | K-SectorRadar |
| Subtitle | Korean High-Growth Sector Analysis |
| Project Type | Web Application |
| Purpose | Provide comprehensive analysis and reporting services for registered stocks |

#### 1.4.2 Project Goals
- Real-time monitoring of Korean high-growth sector-related stocks
- Provide detailed analysis information for each stock
- Provide user-friendly dashboard interface
- Provide stock comparison analysis functionality

---

## 2. Functional Requirements (FR)

### 2.1 Data Collection Requirements (FR-DTS)

| ID | Item | Description |
|:---|:---|:---|
| **FR-DTS-01** | Data Source | **Price Data**: Naver Finance, **Trading Trends**: Naver Finance, **News Data**: Naver News are used as data sources. |
| **FR-DTS-02** | Initial Collection Targets | **4 ETFs**: Samsung KODEX AI Power Core Equipment ETF (487240), Shinhan SOL Shipbuilding TOP3 Plus ETF (466920), KB RISE Global Nuclear iSelect ETF (442320), KoAct Global Quantum Computing Active ETF (0020H0) / **2 Stocks**: Doosan Enerbility (034020), Hanwha Ocean (042660) are the initial collection targets. |
| **FR-DTS-03** | Data Collection Cycle | **Auto Refresh**: Data is refreshed at 30-second intervals (default). |
| **FR-DTS-04** | Manual Refresh | Must provide functionality to manually refresh all data upon user request. |

### 2.2 Page and Routing Requirements (FR-PG)

| ID | Path | Page Name | Description |
|:---|:---|:---|:---|
| **FR-PG-01** | / | Dashboard | Main dashboard. Provides monitoring functionality through stock cards. |
| **FR-PG-02** | /etf/:ticker | Detail | Stock detail analysis page. |
| **FR-PG-03** | /compare | Comparison | Stock comparison analysis page. |
| **FR-PG-04** | /settings | Settings | System settings page. |
| **FR-PG-05** | Navigation | Header Menu | Provides logo (home navigation), Dashboard, Comparison, Settings links, and external GitHub link. |

### 2.3 Dashboard Page Requirements (FR-DB)

| ID | Item | Detailed Requirements |
|:---|:---|:---|
| **FR-DB-06** | Header Area | Displays "SectorRadar Dashboard" title and "Total N stocks" count. |
| **FR-DB-07** | Filter and Sort | Provides sorting functionality: by type (default), by name, by theme, by change rate (high/low), by volume (high/low). (UI form: dropdown or tabs) |
| **FR-DB-08** | Update Information | Displays date in "YYYY-MM-DD Day" format, last collection time and last update time in "HH:MM:SS" format. |
| **FR-DB-09** | Auto Refresh Toggle | Provides checkbox-style "Auto Refresh (30 seconds)" toggle functionality, default is checked (enabled). |
| **FR-DB-17** | Refresh Button | Provides a refresh button to manually refresh all data. |
| **FR-DB-10** | Stock Card (General) | Displays stock name, type badge (STOCK/ETF), theme information, stock code. |
| **FR-DB-11** | Stock Card (Price) | Displays current price (large font), change rate (red/blue color distinction), open price, high price, low price, volume (with unit), weekly change rate. |
| **FR-DB-12** | Stock Card (Chart) | Includes a small candlestick chart showing 6 days of price movement. |
| **FR-DB-13** | Stock Card (Trading Trends) | Displays date in "Trading Trends (YYYY-MM-DD)" format and trading volume by individual, institutional, and foreign investors (amount and sign) with color distinction (blue: minus, red: plus). |
| **FR-DB-14** | Stock Card (News) | Displays news count ("N articles") and 1 latest news headline. Stock code is displayed at the bottom of the card. |
| **FR-DB-15** | Stock Card (ETF) | For ETFs, displays fee information in "Fee: X.XXXX%" format. |
| **FR-DB-16** | Card Interaction | Clicking the card navigates to the detail page of that stock, and hover applies shadow effect. |

### 2.4 Detail Page Requirements (FR-DT)

| ID | Item | Detailed Requirements |
|:---|:---|:---|
| **FR-DT-01** | Stock Detail Information | Displays stock detail information. (Detailed specification required) |

### 2.5 Comparison Page Requirements (FR-CP)

| ID | Item | Detailed Requirements |
|:---|:---|:---|
| **FR-CP-01** | Stock Comparison Analysis | Provides stock comparison analysis functionality. (Detailed specification required) |

### 2.6 Settings Page Requirements (FR-ST)

| ID | Item | Detailed Requirements |
|:---|:---|:---|
| **FR-ST-01** | System Settings | Provides system settings functionality. (Detailed specification required) |

---

## 3. Non-Functional Requirements (NFR)

| ID | Item | Detailed Requirements |
|:---|:---|:---|
| **NFR-PER-01** | Performance (Refresh) | Data refresh cycle: Must meet minimum 30 seconds. |
| **NFR-PER-02** | Performance (Loading) | Page loading time: Target within 3 seconds, chart rendering time: Target within 1 second. |
| **NFR-USE-01** | Usability | Must support intuitive user interface and **responsive web design** for use in mobile and desktop environments. |
| **NFR-SEC-01** | Security | Must establish error handling for external API calls and user data protection measures. |
| **NFR-CMP-01** | Compatibility | Must support latest versions of major web browsers (Chrome, Firefox, Safari, Edge). |
| **NFR-MNT-01** | Maintainability | Must have code comments and documentation, modular structure, and scalable architecture. |

---

## 4. Constraints

### 4.1 Technical Constraints
- Data Source: Must comply with Naver Finance and Naver News API call limits and web scraping constraints.
- Collection Cycle: Must adjust collection cycle considering API call limits.

### 4.2 Business Constraints
- Initial Stock Count: Limited to 6 stocks (4 ETFs, 2 stocks).

---

## 5. Future Expansion Plans

### 5.1 Functional Expansion
- Stock add/delete functionality
- User-customized notification functionality
- Report generation and download functionality

### 5.2 Data Expansion
- Additional data source integration
- Historical data analysis functionality
- Predictive analysis functionality

---

## 6. Glossary

| Term | Definition |
|------|-----------|
| Stock | Stock or ETF |
| Ticker | Unique code identifying a stock |
| Change Rate | Price change rate compared to previous day |
| Trading Trends | Trading status by investor type |
| Candlestick Chart | Chart form expressing stock price movement |

---

