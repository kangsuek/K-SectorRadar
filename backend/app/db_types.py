"""데이터베이스 타입 헬퍼"""

from sqlalchemy import BigInteger, Integer
from sqlalchemy.ext.compiler import compiles


class AutoIncrementBigInteger(BigInteger):
    """
    MySQL에서는 BigInteger(BIGINT)를 사용하고,
    SQLite에서는 Integer를 사용하는 조건부 타입

    이렇게 하면:
    - MySQL: BIGINT AUTO_INCREMENT (대용량 데이터 지원)
    - SQLite: INTEGER PRIMARY KEY (autoincrement 지원)
    """
    pass


@compiles(AutoIncrementBigInteger, 'sqlite')
def compile_autoinc_bigint_sqlite(type_, compiler, **kw):
    """SQLite에서는 INTEGER로 컴파일"""
    return "INTEGER"


@compiles(AutoIncrementBigInteger, 'mysql')
def compile_autoinc_bigint_mysql(type_, compiler, **kw):
    """MySQL에서는 BIGINT로 컴파일"""
    return "BIGINT"


@compiles(AutoIncrementBigInteger, 'postgresql')
def compile_autoinc_bigint_postgresql(type_, compiler, **kw):
    """PostgreSQL에서는 BIGINT로 컴파일"""
    return "BIGINT"
