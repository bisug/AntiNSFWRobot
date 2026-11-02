from kurigram import Client, enums

SUPPORTED_DOCUMENT_MIMES = {
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/webp",
    "image/bmp",
}


async def is_admin(client: Client, chat_id: int, user_id: int) -> bool:
    """Check if the user is a chat owner or administrator."""
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in (
            enums.ChatMemberStatus.OWNER,
            enums.ChatMemberStatus.ADMINISTRATOR,
        )
    except Exception:  # noqa: BLE001
        return False


def getFileId(message):
    fileId = None
    if message.document:
        if int(message.document.file_size) > 5245728:
            return None
        mimeType = (message.document.mime_type or "").lower()
        if mimeType not in SUPPORTED_DOCUMENT_MIMES:
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
