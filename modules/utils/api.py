# Copyright 2024 Qewertyy, MIT License
import asyncio
import hashlib
import io
import logging
import os

from opennsfw_onnx import NSFWClassifier

from modules.database import addFileHash, isNSFW

LOGGER = logging.getLogger(__name__)

# Configurable NSFW threshold (default: 0.6)
NSFW_THRESHOLD = float(os.getenv("NSFW_THRESHOLD", "0.6"))

# Initialize local ONNX classifier session
_classifier = NSFWClassifier(threshold=NSFW_THRESHOLD)


class Stats:
    scanned: int = 0
    nsfw_caught: int = 0
    cache_hits: int = 0


STATS = Stats()


def setThreshold(val: float) -> float:
    global NSFW_THRESHOLD, _classifier
    NSFW_THRESHOLD = max(0.01, min(0.99, val))
    _classifier = NSFWClassifier(threshold=NSFW_THRESHOLD)
    return NSFW_THRESHOLD


def getMediaHash(media: str | bytes | io.BytesIO) -> tuple[str, bytes]:
    """Compute sha256 hash and return (hash_string, raw_bytes)."""
    if isinstance(media, bytes):
        raw_bytes = media
    elif isinstance(media, io.BytesIO):
        raw_bytes = media.getvalue()
    elif isinstance(media, str) and os.path.exists(media):
        with open(media, "rb") as f:
            raw_bytes = f.read()
    else:
        raise ValueError("Unsupported media type for hashing")
    file_hash = hashlib.sha256(raw_bytes).hexdigest()
    return file_hash, raw_bytes


async def Check(media: bytes | io.BytesIO | str) -> bool | None:
    """Classify an image locally in-memory using opennsfw-onnx on ONNX Runtime."""
    try:
        prediction = await asyncio.to_thread(_classifier.classify, media)
        LOGGER.info(
            "Classified media: nsfw=%.4f, sfw=%.4f (is_nsfw=%s)",
            prediction.nsfw,
            prediction.sfw,
            prediction.is_nsfw,
        )
        return prediction.is_nsfw
    except Exception as e:  # noqa: BLE001
        LOGGER.error("Failed to classify image: %s", e)
        return None


async def isNsfw(media: str | bytes | io.BytesIO) -> bool | None:
    """Check if media is NSFW using in-memory hash cache or local ONNX model."""
    if not media:
        return None

    try:
        STATS.scanned += 1
        file_hash, raw_bytes = getMediaHash(media)
        if isNSFW(file_hash) is True:
            STATS.cache_hits += 1
            STATS.nsfw_caught += 1
            return True

        is_unsafe = await Check(raw_bytes)
        if is_unsafe is True:
            STATS.nsfw_caught += 1
            await addNsfwFile(file_hash)
            return True
        elif is_unsafe is False:
            return False
        return None
    except Exception as e:  # noqa: BLE001
        LOGGER.error("Error checking media NSFW status: %s", e)
        return None
    finally:
        if isinstance(media, str) and os.path.exists(media):
            try:
                os.remove(media)
            except OSError:
                pass


async def addNsfwFile(fileHash: str):
    return await addFileHash(fileHash)
