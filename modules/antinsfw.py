import asyncio
import contextlib
import logging

from kurigram import Client, enums, filters
from kurigram import types as t
from modules.utils.api import isNsfw
from modules.utils.misc import getFileId

LOGGER = logging.getLogger(__name__)

_BG_TASKS: set[asyncio.Task] = set()

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


async def _delete_later(message: t.Message, delay: int = 10):
    """Delete a notice message after a given delay."""
    await asyncio.sleep(delay)
    with contextlib.suppress(Exception):
        await message.delete()


@Client.on_message(MEDIA_FILTER, group=9)
@Client.on_edited_message(MEDIA_FILTER, group=9)
async def NSFW(_: Client, message: t.Message):
    if not message.from_user and not message.sender_chat:
        return

    # Check for anonymous admin posting as chat
    if (
        message.sender_chat
        and message.chat
        and message.sender_chat.id == message.chat.id
    ):
        return

    # Check if user is group admin/owner
    if message.from_user and await is_admin(_, message.chat.id, message.from_user.id):
        return

    fileId = getFileId(message)
    if not fileId:
        return

    file = await _.download_media(fileId, in_memory=True)
    if not file:
        return

    unsafe = await isNsfw(file)
    if unsafe is True:
        try:
            await message.delete()
            mention = message.from_user.mention if message.from_user else "A user"
            notice = await message.reply_text(
                f"⚠️ <b>Removed NSFW content from {mention}.</b>",
                quote=False,
            )
            task = asyncio.create_task(_delete_later(notice, delay=10))
            _BG_TASKS.add(task)
            task.add_done_callback(_BG_TASKS.discard)
        except Exception as e:  # noqa: BLE001
            LOGGER.error("Failed to delete NSFW message: %s", e)
