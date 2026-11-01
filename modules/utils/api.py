# Copyright 2024 Qewertyy, MIT License
import asyncio
import hashlib
import logging
import os

from opennsfw_onnx import NSFWClassifier

from modules.database import addFileHash, isNSFW

LOGGER = logging.getLogger(__name__)

# Configurable NSFW threshold (default: 0.6)
NSFW_THRESHOLD = float(os.getenv("NSFW_THRESHOLD", "0.6"))

# Initialize local ONNX classifier session
_classifier = NSFWClassifier(threshold=NSFW_THRESHOLD)


def getFileHash(file: str) -> str:
    hasher = hashlib.sha256()
    with open(file, "rb") as f:
        while chunk := f.read(4096):
            hasher.update(chunk)
    return hasher.hexdigest()


async def Check(file: str) -> bool | None:
    """Classify an image locally using opennsfw-onnx on ONNX Runtime."""
    try:
        prediction = await asyncio.to_thread(_classifier.classify, file)
        LOGGER.info(
            "Classified %s: nsfw=%.4f, sfw=%.4f (is_nsfw=%s)",
            os.path.basename(file),
            prediction.nsfw,
            prediction.sfw,
            prediction.is_nsfw,
        )
        return prediction.is_nsfw
    except Exception as e:  # noqa: BLE001
        LOGGER.error("Failed to classify image %s: %s", file, e)
        return None


async def isNsfw(file: str) -> bool | None:
    """Check if file is NSFW using cached database hash or local ONNX model."""
    if not file or not os.path.exists(file):
        return None

    try:
        fileHash = getFileHash(file)
        if isNSFW(fileHash) is True:
            return True

        is_unsafe = await Check(file)
        if is_unsafe is True:
            await addNsfwFile(fileHash)
            return True
        elif is_unsafe is False:
            return False
        return None
    finally:
        if os.path.exists(file):
            try:
                os.remove(file)
            except OSError:
                pass


async def addNsfwFile(fileHash: str):
    return await addFileHash(fileHash)
