#!/usr/bin/env python3
"""Alembic 마이그레이션 실행 스크립트"""

import sys
import subprocess
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def run_migration(command: str = "upgrade", revision: str = "head"):
    """
    Alembic 마이그레이션 실행
    
    Args:
        command: 마이그레이션 명령 (upgrade, downgrade, revision 등)
        revision: 리비전 (기본값: head)
    """
    backend_dir = Path(__file__).resolve().parent.parent
    
    if command == "upgrade":
        cmd = ["alembic", "upgrade", revision]
    elif command == "downgrade":
        cmd = ["alembic", "downgrade", revision]
    elif command == "revision":
        cmd = ["alembic", "revision", "--autogenerate", "-m", revision]
    elif command == "current":
        cmd = ["alembic", "current"]
    elif command == "history":
        cmd = ["alembic", "history"]
    else:
        print(f"❌ 알 수 없는 명령: {command}")
        sys.exit(1)
    
    try:
        result = subprocess.run(cmd, cwd=backend_dir, check=True)
        print(f"✅ 마이그레이션 {command} 완료")
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"❌ 마이그레이션 실행 실패: {e}")
        sys.exit(1)


def main():
    """메인 함수"""
    if len(sys.argv) < 2:
        print("사용법:")
        print("  python scripts/run_migrations.py upgrade [revision]  # 마이그레이션 적용")
        print("  python scripts/run_migrations.py downgrade [revision]  # 마이그레이션 롤백")
        print("  python scripts/run_migrations.py revision 'message'  # 새 마이그레이션 생성")
        print("  python scripts/run_migrations.py current  # 현재 리비전 확인")
        print("  python scripts/run_migrations.py history  # 마이그레이션 히스토리")
        sys.exit(1)
    
    command = sys.argv[1]
    revision = sys.argv[2] if len(sys.argv) > 2 else "head"
    
    run_migration(command, revision)


if __name__ == "__main__":
    main()

