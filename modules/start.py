# Copyright 2024 Qewertyy, MIT License

try:
    from kurigram import Client, filters
    from kurigram import types as t
except ImportError:
    from pyrogram import Client, filters
    from pyrogram import types as t

startText = """
An AntiNSFW bot Powered by @LexicaAPI to protect your groups from NSFW content.
"""


@Client.on_message(filters.command(["start", "help", "repo", "source"]))
async def start(_: Client, m: t.Message):
    await m.reply_text(
        startText,
        reply_markup=t.InlineKeyboardMarkup(
            [
                [
                    t.InlineKeyboardButton(
                        text="Source", url="https://github.com/Qewertyy/AntiNSFWRobot"
                    )
                ]
            ]
        ),
    )
