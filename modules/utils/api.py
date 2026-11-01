# Copyright 2024 Qewertyy, MIT License
import contextlib
import hashlib
import os

import httpx
from lexica import AsyncClient
from PIL import Image

from modules.database import addFileHash, isNSFW
from modules.utils.misc import upload


def getContentType(url):
    """Get Media Content Type"""
    try:
        with httpx.Client() as client:
            response = client.head(url)
            if response.status_code != 200:
                return None
            return response.headers.get("content-type", "").split("/")[0] or None
    except (TimeoutError, httpx.HTTPError):
        return None


async def Check(file):
    img_url = await upload(file)
    if img_url is None:
        return None
    client = AsyncClient()
    try:
        output = await client.AntiNsfw(img_url)
        return output
    except (TimeoutError, httpx.HTTPError):
        return None
    except Exception as e:  # noqa: BLE001
        print("Failed:", e)
        return None
    finally:
        with contextlib.suppress(Exception):
            await client.close()


def convertToPNG(image):
    with Image.open(image) as im:
        if im.mode not in ("RGB", "RGBA"):
            im = im.convert("RGBA" if "A" in im.mode else "RGB")
        im.save(image, "PNG")


def getFileHash(file):
    hashs = hashlib.sha256()
    with open(file, "rb") as img:
        while chunk := img.read(4096):
            hashs.update(chunk)
    return hashs.hexdigest()


async def isNsfw(file: str):
    """
    Check if file is NSFW
    """
    if not file or not os.path.exists(file):
        return None
    fileHash = getFileHash(file)
    if isNSFW(fileHash) is True:
        if os.path.exists(file):
            try:
                os.remove(file)
            except OSError:
                pass
        return True
    else:
        for ext in [".jpg", ".jpeg", ".webp"]:
            if file.lower().endswith(ext):
                convertToPNG(file)  # cause telegraph acts weird sometimes.
                break
        result = await Check(file)
        if result is None or result.get("code") != 2:
            return None
        sfw = result.get("content", {}).get("sfw")
        if sfw is True:
            return False
        else:
            await addNsfwFile(fileHash)
            return True


async def addNsfwFile(fileHash):
    return await addFileHash(fileHash)
