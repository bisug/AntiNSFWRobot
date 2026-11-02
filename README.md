# AntiNSFWRobot

A Telegram bot to detect and remove NSFW media from groups, powered by local [OpenNSFW ONNX](https://github.com/yahoo/open_nsfw) inference and [Kurigram](https://kurigram.icu).

## Features

- **Local Inference**: Scans media in-memory using OpenNSFW on ONNX Runtime without external API latency or fees.
- **Fast In-Memory Cache**: Caches known NSFW SHA-256 hashes for instant $O(1)$ lookup.
- **Flexible Storage**: Uses embedded SQLite by default; supports remote PostgreSQL for multi-instance deployments.
- **Media Support**: Scans photos, documents (PNG, JPEG, WEBP, BMP), stickers, animations, video thumbs, video notes, stories, and paid media.
- **Admin Immunity**: Skips messages sent by group owners and administrators.
- **Graceful Lifecycle**: Handles `SIGINT`/`SIGTERM` cleanly with non-blocking DB writes and task draining.

## Commands

- `/start`, `/help` - Show bot information and group invitation button.
- `/stats`, `/status` - Display uptime, threshold, hash cache size, total scans, and cache hit rate.
- `/threshold [0.05-0.95]` - View or update NSFW sensitivity (group administrators only).

## Prerequisites

- Python 3.10 or newer
- Telegram `API_ID` and `API_HASH` from [my.telegram.org](https://my.telegram.org)
- Telegram `BOT_TOKEN` from [@BotFather](https://t.me/BotFather)

## Quickstart

1. **Clone repository**:
   ```bash
   git clone https://github.com/Qewertyy/AntiNSFWRobot && cd AntiNSFWRobot
   ```

2. **Create and activate virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate       # Linux/macOS
   # .\venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.sample .env
   # Edit .env with your credentials
   ```

5. **Start bot**:
   ```bash
   python3 bot.py
   ```

## Configuration

Set the following variables in `.env` or system environment:

| Variable | Required | Default | Description |
|---|---|---|---|
| `BOT_TOKEN` | Yes | - | Telegram Bot token from @BotFather |
| `API_ID` | Yes | - | Telegram API ID from my.telegram.org |
| `API_HASH` | Yes | - | Telegram API Hash from my.telegram.org |
| `NSFW_THRESHOLD` | No | `0.6` | Detection sensitivity between `0.05` and `0.95` |
| `DATABASE_URL` | No | - | PostgreSQL URI (`postgresql://user:pass@host:5432/dbname`) |
| `DB_HOST` | No | - | PostgreSQL host (used if `DATABASE_URL` is unset) |
| `DB_PORT` | No | `5432` | PostgreSQL port |
| `DB_USER` | No | - | PostgreSQL username |
| `DB_PASSWORD` | No | - | PostgreSQL password |
| `DB_NAME` | No | - | PostgreSQL database name |
| `DB_SSLMODE` | No | `prefer` | PostgreSQL SSL mode (`disable`, `prefer`, `require`) |
| `DB_MIN_CONNECTIONS` | No | `1` | Minimum database pool connections |
| `DB_MAX_CONNECTIONS` | No | `10` | Maximum database pool connections |

> **Note**: If PostgreSQL credentials are not provided, the bot automatically uses embedded SQLite (`modules/database/data.db`) with WAL mode enabled.

## Deployment

### Heroku
Deploy using the one-click template:

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://dashboard.heroku.com/new?template=https://github.com/Qewertyy/AntiNSFWRobot)

### Systemd Service (Linux VPS)
Create `/etc/systemd/system/antinsfw.service`:

```ini
[Unit]
Description=AntiNSFW Telegram Bot
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/AntiNSFWRobot
ExecStart=/path/to/AntiNSFWRobot/venv/bin/python3 bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now antinsfw
```

## License

This project is licensed under the [MIT License](LICENSE).

