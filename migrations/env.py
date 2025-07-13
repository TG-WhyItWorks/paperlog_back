from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from database import Base  # Base는 모델들의 metadata가 연결된 객체
import os
from models import User,Review,Comment

# Alembic Config 객체
config = context.config

# 로깅 설정
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ✅ 여기에 실제 사용할 DB URL을 명시적으로 동기 방식으로 설정
config.set_main_option("sqlalchemy.url", "sqlite:///./app.db")

# ✅ 메타데이터 설정 (자동 생성 시 사용)
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
