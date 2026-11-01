"""Kurigram shim providing direct `kurigram` namespace imports."""

import sys

try:
    import pyrogram

    sys.modules.setdefault("kurigram", pyrogram)
    for _mod_name, _mod in list(sys.modules.items()):
        if _mod_name == "pyrogram" or _mod_name.startswith("pyrogram."):
            sys.modules.setdefault(_mod_name.replace("pyrogram", "kurigram", 1), _mod)

    from pyrogram import Client, enums, errors, filters, handlers, types  # noqa: F401
except ImportError:
    pass
