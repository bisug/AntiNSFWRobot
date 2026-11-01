import traceback

from kurigram import Client, filters
from kurigram import types as t
from modules.utils.api import isNsfw
from modules.utils.misc import getFileId

MEDIA_FILTER = (
    filters.document
    | filters.photo
    | filters.sticker
    | filters.animation
    | filters.video
    | filters.video_note
    | filters.story
    | filters.paid_message
) & ~filters.private


@Client.on_message(MEDIA_FILTER, group=9)
@Client.on_edited_message(MEDIA_FILTER, group=9)
async def NSFW(_: Client, message: t.Message):
    if not message.from_user and not message.sender_chat:
        return
    fileId = getFileId(message)
    if not fileId:
        return
    file = await _.download_media(fileId)
    if not file:
        return
    unsafe = await isNsfw(file)
    if unsafe is True:
        try:
            await message.delete()
        except Exception:  # noqa: BLE001
            traceback.print_exc()
            return
