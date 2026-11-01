# Copyright 2024 Qewertyy, MIT License

from kurigram import Client, filters
from kurigram import types as t

startText = """
An AntiNSFW bot powered by OpenNSFW (ONNX Runtime) to protect your groups from NSFW content.

<b>Commands:</b>
• /start, /help - Show this message
• /stats - View scanning statistics and bot uptime
• /threshold - View or update NSFW sensitivity (admins only)
"""


@Client.on_message(filters.command(["start", "help", "repo", "source"]))
async def start(_: Client, m: t.Message):
    buttons = [
        [
            t.InlineKeyboardButton(
                text="Source", url="https://github.com/Qewertyy/AntiNSFWRobot"
            )
        ]
    ]
    bot_username = _.me.username if _.me else None
    if bot_username:
        buttons.insert(
            0,
            [
                t.InlineKeyboardButton(
                    text="Add to Group",
                    url=f"https://t.me/{bot_username}?startgroup=true",
                )
            ],
        )
    await m.reply_text(
        startText,
        reply_markup=t.InlineKeyboardMarkup(buttons),
    )
