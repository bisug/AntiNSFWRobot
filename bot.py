# Copyright 2024 Qewertyy, MIT License

try:
    import uvloop

    uvloop.install()
except (ImportError, AttributeError):
    pass
import asyncio
import datetime
import logging
import signal
import sys

from config import Config
from kurigram import Client, enums

# Get logging configurations
logging.basicConfig(
    format="%(asctime)s - [BOT] - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs.txt"), logging.StreamHandler()],
    level=logging.INFO,
)
logging.getLogger("kurigram").setLevel(logging.WARNING)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("onnxruntime").setLevel(logging.WARNING)
LOGGER = logging.getLogger(__name__)

StartTime = datetime.datetime.now()


class Bot(Client):
    def __init__(self):
        super().__init__(
            "AntiNSFWRobot",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            plugins={"root": "modules"},
            max_concurrent_transmissions=3,
            max_topic_cache_size=1000,
            max_message_cache_size=2000,
            fetch_topics=True,
            fetch_stories=True,
            skip_updates=True,
            sleep_threshold=30,
            parse_mode=enums.ParseMode.HTML,
        )
        self._is_stopping = False

    async def start(self):
        LOGGER.info("Starting AntiNSFWRobot...")
        await super().start()
        try:
            me = await self.get_me()
            LOGGER.info(
                "Bot started successfully as @%s (ID: %s)",
                me.username or "unknown",
                me.id,
            )
        except Exception as e:
            LOGGER.warning("Could not retrieve bot user info: %s", e)

        from modules.database import FILE_HASHES

        LOGGER.info("Database cache ready with %d NSFW hashes.", len(FILE_HASHES))

    async def stop(self):
        if self._is_stopping:
            return
        self._is_stopping = True
        LOGGER.info("Initiating graceful shutdown...")

        # 1. Stop client session first (shuts down network listeners & MTProto tasks cleanly)
        try:
            await super().stop()
        except Exception as e:
            LOGGER.error("Error stopping Telegram client: %s", e)

        # 2. Disconnect database pool after all message processing has ceased
        try:
            from modules.database import close_db

            close_db()
        except Exception as e:
            LOGGER.error("Failed to cleanly disconnect DB: %s", e)

        # 3. Cancel any lingering background tasks
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        for t in tasks:
            t.cancel()

        LOGGER.info("All services stopped cleanly.")


@Client.on_error()
async def on_update_error(client: Client, update, exception: Exception):
    LOGGER.error("Error processing update: %s", exception, exc_info=exception)


async def main():
    try:
        Config.validate()
    except ValueError as e:
        LOGGER.critical("Configuration error: %s", e)
        sys.exit(1)

    bot = Bot()
    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop_event.set)
        except NotImplementedError:
            pass

    try:
        await bot.start()
        LOGGER.info("Bot is running. (Press Ctrl+C or send SIGTERM to stop)")
        await stop_event.wait()
    except Exception as e:
        LOGGER.critical("Fatal runtime exception: %s", e, exc_info=e)
    finally:
        await bot.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass

