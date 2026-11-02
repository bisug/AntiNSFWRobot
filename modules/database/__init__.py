import logging

from pony import orm

from config import Config

logger = logging.getLogger(__name__)
db = orm.Database()

FILE_HASHES: set[str] = set()


class FileHashes(db.Entity):
    __table__ = "hashes"
    hash = orm.PrimaryKey(str)


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
    }
    if Config.DB_SSLMODE:
        bind_kwargs["sslmode"] = Config.DB_SSLMODE

    db.bind(**bind_kwargs)
    logger.info("Postgres Database configured.")

db.generate_mapping(create_tables=True)


async def addFileHash(fileHash: str):
    with orm.db_session:
        if not FileHashes.exists(hash=fileHash):
            try:
                FileHashes(hash=fileHash)
                db.commit()
                FILE_HASHES.add(fileHash)
            except (orm.IntegrityError, orm.TransactionIntegrityError):
                return


def __loadFileHashes() -> set[str]:
    global FILE_HASHES
    with orm.db_session:
        FILE_HASHES = set(orm.select(h.hash for h in FileHashes))
    return FILE_HASHES


def isNSFW(fileHash: str) -> bool | None:
    return fileHash in FILE_HASHES


__loadFileHashes()
