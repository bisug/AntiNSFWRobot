import asyncio
import os

import httpx


def _read_file(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()


def getFileId(message):
    fileId = None
    if message.document:
        if int(message.document.file_size) > 5245728:
            return None
        mimeType = message.document.mime_type
        if mimeType not in ["image/png", "image/jpeg"]:
            return None
        fileId = message.document.file_id
    elif message.sticker:
        if message.sticker.is_animated or message.sticker.is_video:
            if not message.sticker.thumbs:
                return None
            fileId = message.sticker.thumbs[0].file_id
        else:
            fileId = message.sticker.file_id
    elif message.photo:
        fileId = message.photo.file_id
    elif message.animation:
        if not message.animation.thumbs:
            return None
        fileId = message.animation.thumbs[0].file_id
    elif message.video:
        if not message.video.thumbs:
            return None
        fileId = message.video.thumbs[0].file_id
    elif message.video_note:
        if message.video_note.thumbs:
            fileId = message.video_note.thumbs[0].file_id
        else:
            fileId = message.video_note.file_id
    elif message.story:
        if message.story.photo:
            fileId = message.story.photo.file_id
        elif message.story.video and message.story.video.thumbs:
            fileId = message.story.video.thumbs[0].file_id
    elif message.paid_media and message.paid_media.media:
        first_item = message.paid_media.media[0]
        if hasattr(first_item, "file_id"):
            fileId = first_item.file_id
        elif hasattr(first_item, "thumbs") and first_item.thumbs:
            fileId = first_item.thumbs[0].file_id
    return fileId


async def upload(file: str):
    res = None
    try:
        file_bytes = await asyncio.to_thread(_read_file, file)
        files = {"file": (os.path.basename(file), file_bytes)}
        async with httpx.AsyncClient(http2=True) as client:
            res = await client.post("https://graph.org/upload", files=files)
        if res.status_code != 200:
            return None
        resp = res.json()
        if "error" in resp:
            return None
        return "https://graph.org" + resp[0]["src"]
    except Exception as e:  # noqa: BLE001
        error_msg = res.text if res is not None else str(e)
        print("Uploading to telegraph failed:", error_msg)
        return None
    finally:
        if os.path.exists(file):
            try:
                os.remove(file)
            except OSError:
                pass
