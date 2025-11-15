#!/usr/bin/env python3
"""초기 종목 데이터 시드 스크립트"""

import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import SessionLocal, init_db_with_seed, seed_stocks_from_json


def main():
    """메인 함수"""
    print("데이터베이스 초기화 중...")
    
    # 테이블 생성
    from app.database import Base, engine
    Base.metadata.create_all(bind=engine)
    
    # 시드 데이터 로드
    db = SessionLocal()
    try:
        print("종목 데이터 시드 중...")
        added_count = seed_stocks_from_json(db)
        print(f"✅ {added_count}개의 종목이 추가되었습니다.")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        sys.exit(1)
    finally:
        db.close()
    
    print("✅ 데이터베이스 초기화 완료!")


if __name__ == "__main__":
    main()

