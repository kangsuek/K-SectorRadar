# 테스트 실행 가이드

## Phase 1.5 테스트 및 검증

Phase 1.5의 모든 테스트 파일이 작성되었습니다. 테스트를 실행하기 전에 순환 import 문제를 해결해야 합니다.

## 현재 상태

✅ 작성 완료된 테스트 파일:
- `tests/test_database.py` - 데이터베이스 연결 및 모델 테스트
- `tests/test_cache.py` - Redis 캐싱 테스트 (TTL, 무효화 포함)
- `tests/test_api_health.py` - Health Check API 테스트
- `tests/test_api_stocks.py` - 종목 API 테스트
- `tests/test_api_prices.py` - 가격 데이터 API 테스트
- `tests/test_integration.py` - 통합 테스트

## 알려진 문제

현재 순환 import 문제로 인해 테스트 실행 시 RecursionError가 발생합니다.

### 문제 원인
- `app.database` → `app.models` → `app.database` 순환 구조
- `app.main` → `app.database` → `app.models` → `app.database` 순환 구조

### 해결 방법

1. **Base를 별도 파일로 분리** (권장)
   - `app/db_base.py` 생성하여 `Base` 정의
   - `app/database.py`와 `app/models/*.py`에서 `app.db_base`에서 import

2. **또는 모델 import를 지연** (현재 부분 적용됨)
   - 함수 내에서만 모델 import
   - 하지만 여전히 일부 순환 import 발생

## 테스트 실행 방법

순환 import 문제 해결 후:

```bash
cd backend

# 모든 테스트 실행
python3 -m pytest tests/ -v

# 커버리지 포함 실행
python3 -m pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing

# 특정 테스트 파일만 실행
python3 -m pytest tests/test_database.py -v
python3 -m pytest tests/test_api_stocks.py -v
python3 -m pytest tests/test_api_health.py -v
python3 -m pytest tests/test_api_prices.py -v
python3 -m pytest tests/test_integration.py -v

# 특정 테스트 클래스만 실행
python3 -m pytest tests/test_api_stocks.py::TestGetStocks -v

# 특정 테스트만 실행
python3 -m pytest tests/test_api_stocks.py::TestGetStocks::test_get_stocks_empty -v
```

## 테스트 커버리지 목표

- Phase 1: 80% 이상
- 최종: 90% 이상

## 다음 단계

1. 순환 import 문제 해결
2. 모든 테스트 통과 확인
3. 커버리지 80% 이상 달성 확인
4. Swagger UI를 통한 API 수동 테스트

