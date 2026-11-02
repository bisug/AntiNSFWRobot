import datetime

from bot import StartTime
from kurigram import Client, enums, filters
from kurigram import types as t
from modules.database import FILE_HASHES
from modules.utils.api import NSFW_THRESHOLD, STATS, setThreshold
from modules.utils.misc import is_admin


def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]
    while count < 4:
        count += 1
        if count < 3:
            remainder, result = divmod(seconds, 60)
        else:
            remainder, result = divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)
    for i in range(len(time_list)):
        time_list[i] = str(time_list[i]) + time_suffix_list[i]
    if len(time_list) == 4:
        ping_time += f"{time_list.pop()}, "
    time_list.reverse()
    ping_time += ":".join(time_list)
    return ping_time or "0s"


@Client.on_message(filters.command(["stats", "status"]))
async def stats_command(_: Client, m: t.Message):
    uptime_sec = int((datetime.datetime.now() - StartTime).total_seconds())
    uptime_str = get_readable_time(uptime_sec)

    hit_rate = (STATS.cache_hits / STATS.scanned * 100) if STATS.scanned > 0 else 0.0

    text = (
        "📊 <b>AntiNSFW Bot Statistics</b>\n\n"
        f"⏱ <b>Uptime:</b> <code>{uptime_str}</code>\n"
        f"🎯 <b>NSFW Threshold:</b> <code>{NSFW_THRESHOLD:.2f}</code>\n"
        f"💾 <b>Cached Hashes (DB):</b> <code>{len(FILE_HASHES):,}</code>\n"
        f"🔍 <b>Media Scanned:</b> <code>{STATS.scanned:,}</code>\n"
        f"🚫 <b>NSFW Blocked:</b> <code>{STATS.nsfw_caught:,}</code>\n"
        f"⚡ <b>Cache Hit Rate:</b> <code>{hit_rate:.1f}%</code>"
    )
    await m.reply_text(text)


@Client.on_message(filters.command(["threshold", "setthreshold"]))
async def threshold_command(_: Client, m: t.Message):
    if len(m.command) < 2:
        await m.reply_text(
            f"🎯 <b>Current NSFW Threshold:</b> <code>{NSFW_THRESHOLD:.2f}</code>\n\n"
            "<i>To update, pass a value between 0.05 and 0.95:\n"
            "e.g. <code>/threshold 0.65</code></i>"
        )
        return

    # Check if command sender is group admin in group chats
    if m.chat.type != enums.ChatType.PRIVATE and m.from_user:
        if not await is_admin(_, m.chat.id, m.from_user.id):
            await m.reply_text(
                "❌ <b>Only group administrators can adjust the threshold.</b>"
            )
            return

    try:
        new_val = float(m.command[1])
        if not (0.05 <= new_val <= 0.95):
            await m.reply_text(
                "⚠️ Threshold must be between <code>0.05</code> and <code>0.95</code>."
            )
            return
        updated = setThreshold(new_val)
        await m.reply_text(
            f"✅ <b>NSFW Threshold updated to:</b> <code>{updated:.2f}</code>"
        )
    except ValueError:
        await m.reply_text(
            "⚠️ Invalid number format. Example: <code>/threshold 0.65</code>"
        )
