from sqlalchemy import create_engine

from app.core.settings import settings

from sqlalchemy.engine.url import make_url

# Ensure the use of the psycopg driver for PostgreSQL
db_url = make_url(settings.get_uri())
if db_url.drivername.startswith("postgresql") and "+psycopg" not in db_url.drivername:
    db_url = db_url.set(drivername="postgresql+psycopg")

engine = create_engine(
    db_url,
    pool_size=10,              # reasonable default for web apps
    max_overflow=20,           # allow up to 20 extra connections
    pool_timeout=30,           # seconds to wait before giving up on getting a connection
    pool_recycle=1800,         # recycle connections every 30 minutes
    pool_pre_ping=True,        # check connections before using
)
