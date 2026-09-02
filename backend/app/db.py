import os

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


database_url = make_url(os.environ["DATABASE_URL"])
engine_options: dict[str, object] = {"pool_pre_ping": True}
if database_url.get_backend_name() == "postgresql":
    # The provisioned role is limited to 20 sessions. Two overlapping rolling
    # containers stay below that limit while leaving room for migrations.
    engine_options.update(
        pool_size=5,
        max_overflow=3,
        pool_timeout=5,
        connect_args={"connect_timeout": 5},
    )

engine = create_engine(database_url, **engine_options)
