import asyncio
import logging

from pony import orm

from config import Config

logger = logging.getLogger(__name__)
db = orm.Database()

FILE_HASHES: set[str] = set()


class FileHashes(db.Entity):
    __table__ = "hashes"
    hash = orm.PrimaryKey(str)


@db.on_connect(provider="sqlite")
def _set_sqlite_pragmas(connection, _):
    """Enable WAL mode, fast sync, and busy timeout for SQLite concurrency."""
    cursor = connection.cursor()
    cursor.execute("PRAGMA journal_mode = WAL;")
    cursor.execute("PRAGMA synchronous = NORMAL;")
    cursor.execute("PRAGMA busy_timeout = 5000;")
    cursor.close()


if not (Config.DB_HOST and Config.DB_USER and Config.DB_NAME):
    logger.warning("External Database not configured. Using SQLite instead.")
    db.bind(provider="sqlite", filename="data.db", create_db=True)

else:
    bind_kwargs = {
        "provider": "postgres",
        "host": Config.DB_HOST,
        "port": Config.DB_PORT,
        "user": Config.DB_USER,
        "password": Config.DB_PASSWORD or "",
        "database": Config.DB_NAME,
        "min_connections": Config.DB_MIN_CONNECTIONS,
        "max_connections": Config.DB_MAX_CONNECTIONS,
    }
    if Config.DB_SSLMODE:
        bind_kwargs["sslmode"] = Config.DB_SSLMODE

    db.bind(**bind_kwargs)
    logger.info("Postgres Database configured.")

db.generate_mapping(create_tables=True)


def _sync_add_hash(file_hash: str) -> None:
    """Synchronous worker function to commit a new hash to database."""
    with orm.db_session:
        if not FileHashes.exists(hash=file_hash):
            try:
                FileHashes(hash=file_hash)
                db.commit()
            except (orm.IntegrityError, orm.TransactionIntegrityError):
                pass


async def addFileHash(fileHash: str) -> None:
    """Add hash to memory cache instantly and persist to DB in background thread."""
    if not fileHash or fileHash in FILE_HASHES:
        return
    FILE_HASHES.add(fileHash)
    try:
        await asyncio.to_thread(_sync_add_hash, fileHash)
    except Exception as e:
        logger.error("Failed to persist hash %s to database: %s", fileHash, e)


def __loadFileHashes() -> set[str]:
    """Load existing hashes on startup with error handling."""
    global FILE_HASHES
    try:
        with orm.db_session:
            FILE_HASHES = set(orm.select(h.hash for h in FileHashes))
        logger.info("Loaded %d cached hashes from database.", len(FILE_HASHES))
    except Exception as e:
        logger.error("Failed to load hashes from database on startup: %s", e)
        FILE_HASHES = set()
    return FILE_HASHES


def isNSFW(fileHash: str) -> bool:
    """Instant O(1) in-memory check without database latency."""
    return fileHash in FILE_HASHES


def close_db() -> None:
    """Disconnect database connection pool cleanly."""
    try:
        db.disconnect()
        logger.info("Database disconnected cleanly.")
    except Exception as e:
        logger.error("Error disconnecting database: %s", e)


__loadFileHashes()

