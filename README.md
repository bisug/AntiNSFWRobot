# AntiNSFWRobot

### A simple telegram bot to remove NSFW content from your groups powered by local [OpenNSFW ONNX](https://github.com/yahoo/open_nsfw) & [Kurigram](https://kurigram.icu)
#### Demo [Protect your groups bot](https://telegram.me/ProtectYourGroupsRobot)

## Deploy on VPS
fill `.env` with proper values
```bash
git clone https://github.com/Qewertyy/AntiNSFWRobot && cd AntiNSFWRobot
python3 -m venv venv
source venv/bin/activate # Linux
.\venv\Scripts\activate # Windows
pip install -r requirements.txt
python3 bot.py
```

## Deploy to Heroku
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://dashboard.heroku.com/new?template=https://github.com/Qewertyy/AntiNSFWRobot)
