# Copyright 2024 Qewertyy, MIT License

try:
    import uvloop

    uvloop.install()
except (ImportError, AttributeError):
    pass
import datetime
import logging

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

    async def start(self):
        await super().start()
        LOGGER.info("Bot Started")

    async def stop(self):
        await super().stop()
        LOGGER.info("Stopped Services")


@Client.on_error()
async def on_update_error(client: Client, update, exception: Exception):
    LOGGER.error("Error processing update: %s", exception, exc_info=exception)


if __name__ == "__main__":
    Bot().run()
