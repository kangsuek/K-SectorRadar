# 초기 데이터베이스 생성 및 데이터 로드 가이드

이 문서는 K-SectorRadar 프로젝트의 초기 데이터베이스 생성 및 초기 데이터 로드를 위한 단계별 가이드입니다.

## 목차

1. [사전 요구사항](#1-사전-요구사항)
2. [데이터베이스 생성](#2-데이터베이스-생성)
3. [환경 변수 설정](#3-환경-변수-설정)
4. [데이터베이스 초기화](#4-데이터베이스-초기화)
5. [초기 데이터 로드](#5-초기-데이터-로드)
6. [데이터 검증](#6-데이터-검증)
7. [문제 해결](#7-문제-해결)

---

## 1. 사전 요구사항

### 1.1 MySQL 설치 및 실행

MySQL이 설치되어 있고 실행 중이어야 합니다.

**macOS:**
```bash
brew install mysql
brew services start mysql
brew services list | grep mysql  # 실행 상태 확인
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install mysql-server
sudo systemctl start mysql
sudo systemctl enable mysql
```

**Windows:**
- MySQL 공식 사이트에서 MySQL Installer 다운로드 및 설치
- 서비스 관리자에서 MySQL 서비스가 실행 중인지 확인

### 1.2 Python 가상 환경 활성화

```bash
cd backend
source venv/bin/activate  # 또는 Windows: venv\Scripts\activate
```

---

## 2. 데이터베이스 생성

### 2.1 MySQL 접속

```bash
mysql -u root -p
```

### 2.2 데이터베이스 및 사용자 생성

MySQL 프롬프트에서 다음 명령어를 실행하세요:

```sql
-- 데이터베이스 생성
CREATE DATABASE sectorradar CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 전용 사용자 생성 (권장)
CREATE USER 'sectorradar'@'localhost' IDENTIFIED BY 'your_secure_password';

-- 권한 부여
GRANT ALL PRIVILEGES ON sectorradar.* TO 'sectorradar'@'localhost';

-- 권한 적용
FLUSH PRIVILEGES;

-- 데이터베이스 확인
SHOW DATABASES;
EXIT;
```

**참고**: root 사용자를 사용하는 경우 이 단계를 건너뛸 수 있습니다.

---

## 3. 환경 변수 설정

### 3.1 .env 파일 생성

`backend` 디렉토리에 `.env` 파일을 생성하세요:

```bash
cd backend
touch .env  # 또는 Windows: type nul > .env
```

### 3.2 .env 파일 내용

**옵션 1: 전용 사용자 사용 (권장)**
```bash
# Database Configuration - MySQL only
DATABASE_URL=mysql+pymysql://sectorradar:your_secure_password@localhost:3306/sectorradar
```

**옵션 2: root 사용자 사용**
```bash
# Database Configuration - MySQL only
DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/sectorradar
```

**전체 .env 파일 예시:**
```bash
# Database Configuration - MySQL only
DATABASE_URL=mysql+pymysql://sectorradar:your_secure_password@localhost:3306/sectorradar

# Redis Configuration (Optional)
REDIS_URL=redis://localhost:6379/0

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# CORS Origins (쉼표로 구분된 문자열 또는 JSON 배열 형식)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Environment
ENVIRONMENT=development
```

### 3.3 연결 테스트

```bash
cd backend
python3 -c "
from app.config import settings
from sqlalchemy import create_engine, text
try:
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1'))
        print('✅ MySQL 연결 성공!')
        print(f'데이터베이스: {settings.DATABASE_URL.split(\"/\")[-1]}')
except Exception as e:
    print(f'❌ MySQL 연결 실패: {e}')
"
```

---

## 4. 데이터베이스 초기화

데이터베이스 초기화는 테이블을 생성하는 과정입니다.

### 4.1 방법 1: 직접 실행 (권장)

```bash
cd backend
source venv/bin/activate

# 테이블 생성
python3 -c "from app.database import init_db; import asyncio; asyncio.run(init_db())"
```

**예상 출력:**
```
✅ 테이블 생성 완료
```

### 4.2 방법 2: Python 스크립트 사용

```bash
cd backend
source venv/bin/activate

python3 << EOF
import asyncio
from app.database import init_db

async def main():
    print("데이터베이스 초기화 중...")
    await init_db()
    print("✅ 테이블 생성 완료")

asyncio.run(main())
EOF
```

### 4.3 생성되는 테이블 확인

다음 테이블들이 생성됩니다:

- `stocks`: 종목 정보 테이블
- `prices`: 가격 데이터 테이블
- `trading_trends`: 매매 동향 테이블
- `news`: 뉴스 데이터 테이블

**테이블 생성 확인:**
```bash
python3 -c "
from app.database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
tables = inspector.get_table_names()
print('✅ 생성된 테이블:')
for table in sorted(tables):
    print(f'  - {table}')
"
```

---

## 5. 초기 데이터 로드

초기 종목 데이터를 데이터베이스에 로드합니다.

### 5.1 시드 스크립트 실행

```bash
cd backend
source venv/bin/activate
python scripts/seed_stocks.py
```

**예상 출력:**
```
데이터베이스 초기화 중...
종목 데이터 시드 중...
✅ 150개의 종목이 추가되었습니다.
✅ 데이터베이스 초기화 완료!
```

### 5.2 시드 데이터 소스

초기 종목 데이터는 `backend/config/stocks.json` 파일에서 로드됩니다.

**파일 구조 예시:**
```json
[
  {
    "ticker": "487240",
    "name": "두산에너빌리티",
    "type": "STOCK",
    "theme": "Nuclear/Power Plant/Energy",
    "fee": null
  },
  ...
]
```

### 5.3 시드 데이터 커스터마이징

자신만의 종목 데이터를 추가하려면:

1. `backend/config/stocks.json` 파일을 편집하거나
2. 다른 JSON 파일을 사용하려면:
```bash
python3 -c "
from app.database import SessionLocal, seed_stocks_from_json

db = SessionLocal()
try:
    count = seed_stocks_from_json(db, json_path='path/to/your/stocks.json')
    print(f'✅ {count}개의 종목이 추가되었습니다.')
finally:
    db.close()
"
```

---

## 6. 데이터 검증

초기화 및 데이터 로드가 성공적으로 완료되었는지 확인합니다.

### 6.1 테이블 구조 확인

```bash
python3 -c "
from app.database import engine
from sqlalchemy import inspect, text

inspector = inspect(engine)

# 테이블 목록
tables = inspector.get_table_names()
print('📊 생성된 테이블:')
for table in sorted(tables):
    print(f'  ✅ {table}')

# stocks 테이블 컬럼 확인
if 'stocks' in tables:
    print('\n📋 stocks 테이블 구조:')
    columns = inspector.get_columns('stocks')
    for col in columns:
        print(f'  - {col[\"name\"]}: {col[\"type\"]}')
"
```

### 6.2 데이터 개수 확인

```bash
python3 -c "
from app.database import SessionLocal
from app.models import Stock, Price, TradingTrend, News

db = SessionLocal()
try:
    stock_count = db.query(Stock).count()
    price_count = db.query(Price).count()
    trading_count = db.query(TradingTrend).count()
    news_count = db.query(News).count()
    
    print('📊 데이터 개수:')
    print(f'  - 종목(stocks): {stock_count}개')
    print(f'  - 가격(prices): {price_count}개')
    print(f'  - 매매동향(trading_trends): {trading_count}개')
    print(f'  - 뉴스(news): {news_count}개')
    
    if stock_count > 0:
        print('\n✅ 초기 데이터 로드 성공!')
    else:
        print('\n⚠️ 종목 데이터가 없습니다. seed_stocks.py를 실행하세요.')
finally:
    db.close()
"
```

### 6.3 샘플 데이터 확인

```bash
python3 -c "
from app.database import SessionLocal
from app.models import Stock

db = SessionLocal()
try:
    # 처음 5개 종목 조회
    stocks = db.query(Stock).limit(5).all()
    print('📋 샘플 종목 데이터:')
    for stock in stocks:
        print(f'  - {stock.ticker}: {stock.name} ({stock.type})')
finally:
    db.close()
"
```

### 6.4 MySQL 클라이언트로 확인

```bash
mysql -u sectorradar -p sectorradar
```

```sql
-- 테이블 목록 확인
SHOW TABLES;

-- 종목 개수 확인
SELECT COUNT(*) FROM stocks;

-- 샘플 데이터 확인
SELECT ticker, name, type, theme FROM stocks LIMIT 5;

-- 테이블 구조 확인
DESCRIBE stocks;
DESCRIBE prices;
DESCRIBE trading_trends;
DESCRIBE news;

EXIT;
```

---

## 7. 문제 해결

### 7.1 오류: "Access denied for user"

**원인**: 비밀번호가 잘못되었거나 사용자가 존재하지 않음

**해결 방법:**
```bash
# MySQL에 root로 접속
mysql -u root -p

# 사용자 비밀번호 재설정
ALTER USER 'sectorradar'@'localhost' IDENTIFIED BY 'new_password';
FLUSH PRIVILEGES;

# .env 파일의 비밀번호 업데이트
```

### 7.2 오류: "Unknown database 'sectorradar'"

**원인**: 데이터베이스가 생성되지 않음

**해결 방법:**
```sql
CREATE DATABASE sectorradar CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 7.3 오류: "Can't connect to MySQL server"

**원인**: MySQL 서버가 실행되지 않음

**해결 방법:**
```bash
# macOS
brew services start mysql

# Ubuntu/Debian
sudo systemctl start mysql

# 상태 확인
brew services list | grep mysql  # macOS
sudo systemctl status mysql       # Ubuntu/Debian
```

### 7.4 오류: "Table already exists"

**원인**: 테이블이 이미 존재함

**해결 방법:**

**옵션 1: 기존 테이블 유지 (권장)**
- 테이블이 이미 존재하면 초기화를 건너뛰고 데이터만 로드

**옵션 2: 테이블 삭제 후 재생성 (주의: 모든 데이터 삭제)**
```bash
python3 -c "
from app.database import engine, Base
from app.models import Stock, Price, TradingTrend, News

# 모든 테이블 삭제
Base.metadata.drop_all(bind=engine)
print('✅ 기존 테이블 삭제 완료')

# 테이블 재생성
Base.metadata.create_all(bind=engine)
print('✅ 테이블 재생성 완료')
"
```

### 7.5 오류: "Specified key was too long"

**원인**: MySQL 인덱스 키 길이 제한 초과 (이미 해결됨)

**해결 방법:**
- `news` 테이블의 `url_hash` 필드를 사용하도록 이미 수정되었습니다.
- 이 오류가 발생하면 최신 코드로 업데이트하세요.

### 7.6 시드 데이터가 로드되지 않음

**원인**: `stocks.json` 파일이 없거나 경로가 잘못됨

**해결 방법:**
```bash
# stocks.json 파일 확인
ls -la backend/config/stocks.json

# 파일이 없으면 생성하거나 경로 확인
python3 -c "
from pathlib import Path
json_path = Path('backend/config/stocks.json')
if json_path.exists():
    print(f'✅ 파일 존재: {json_path}')
    print(f'파일 크기: {json_path.stat().st_size} bytes')
else:
    print(f'❌ 파일 없음: {json_path}')
"
```

### 7.7 중복 데이터 오류

**원인**: 이미 데이터가 존재하는데 다시 시드 실행

**해결 방법:**
- 시드 스크립트는 중복 체크를 하므로 안전하게 재실행 가능
- 특정 종목만 삭제하려면:
```sql
DELETE FROM stocks WHERE ticker = 'TICKER_CODE';
```

---

## 8. 완전 초기화 (전체 재설정)

모든 데이터를 삭제하고 처음부터 다시 시작하려면:

```bash
cd backend
source venv/bin/activate

# 1. 모든 테이블 삭제
python3 -c "
from app.database import engine, Base
from app.models import Stock, Price, TradingTrend, News
Base.metadata.drop_all(bind=engine)
print('✅ 모든 테이블 삭제 완료')
"

# 2. 테이블 재생성
python3 -c "from app.database import init_db; import asyncio; asyncio.run(init_db())"

# 3. 초기 데이터 로드
python scripts/seed_stocks.py
```

---

## 9. 다음 단계

초기 데이터베이스 생성 및 데이터 로드가 완료되면:

1. **서버 실행:**
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn app.main:app --reload
   ```

2. **API 테스트:**
   - Swagger UI: http://localhost:8000/docs
   - Health Check: http://localhost:8000/api/health
   - 종목 목록: http://localhost:8000/api/stocks

3. **데이터 수집:**
   - API를 통해 데이터 수집 시작
   - 스케줄러 설정 확인

자세한 내용은 다음 문서를 참조하세요:
- [README.md](./README.md) - 서버 실행 및 기본 사용법
- [docs/eng/08-SWAGGER_UI_TESTING_GUIDE.md](../../docs/eng/08-SWAGGER_UI_TESTING_GUIDE.md) - API 테스트 가이드
- [docs/eng/04-DATABASE_SCHEMA.md](../../docs/eng/04-DATABASE_SCHEMA.md) - 데이터베이스 스키마 상세

---

## 10. 요약 체크리스트

초기 데이터베이스 설정을 완료하기 위한 체크리스트:

- [ ] MySQL 설치 및 실행 확인
- [ ] 데이터베이스 `sectorradar` 생성
- [ ] 사용자 계정 생성 및 권한 부여 (선택사항)
- [ ] `.env` 파일 생성 및 `DATABASE_URL` 설정
- [ ] MySQL 연결 테스트 성공
- [ ] 테이블 생성 완료 (4개 테이블)
- [ ] 초기 종목 데이터 로드 완료
- [ ] 데이터 검증 완료
- [ ] 서버 실행 및 API 테스트 성공

---

**참고**: 프로덕션 환경에서는 보안 설정(SSL 연결, 강력한 비밀번호, 최소 권한 원칙 등)을 추가로 고려해야 합니다.
