import os, traceback
import httpx

def getFileId(message):
    fileId = None
    if message.document:
        if int(message.document.file_size) > 5245728:
            return None
        mimeType = message.document.mime_type
        if mimeType not in ["image/png", "image/jpeg"]:
            return None
        fileId = message.document.file_id
    if message.sticker:
        if message.sticker.is_animated:
            if not message.sticker.thumbs:
                return None
            fileId = message.sticker.thumbs[0].file_id
        elif message.sticker.is_video:
            if not message.sticker.thumbs:
                return None
            fileId = message.sticker.thumbs[0].file_id
        else:
            fileId = message.sticker.file_id
    if message.photo:
        fileId = message.photo.file_id

    if message.animation:
        if not message.animation.thumbs:
            return None
        fileId = message.animation.thumbs[0].file_id

    if message.video:
        if not message.video.thumbs:
            return None
        fileId = message.video.thumbs[0].file_id
    return fileId

async def upload(file: str):
    res = None
    try:
        with open(file, "rb") as f:
            file_bytes = f.read()
        files = {"file": (os.path.basename(file), file_bytes)}
        async with httpx.AsyncClient(http2=True) as client:
            res = await client.post(
                "https://graph.org/upload",
                files=files
            )
        if res.status_code != 200:
            return None
        resp = res.json()
        if "error" in resp:
            return None
        return 'https://graph.org' + resp[0]['src']
    except Exception as e:
        error_msg = res.text if res is not None else str(e)
        print("Uploading to telegraph failed:", error_msg)
        return None
    finally:
        if os.path.exists(file):
            try:
                os.remove(file)
            except OSError:
                pass
