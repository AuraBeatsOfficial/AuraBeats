# AuraBeats

Premium AI-powered Telegram music bot.
Zero-latency streaming - Live effects - AI playlists - Premium UI.

Links:
- Bot: https://t.me/AuraBeatsOfficialBot
- Assistant: https://t.me/AuraBeatsOfficial
- Updates: https://t.me/Vip_Sakil_Bio
- Developer: https://t.me/YO_UR_OFFICIAL_CRUSH

Status:
- Structure: DONE
- Code: Phase 2 in progress

Project Structure:

  AuraBeats/
    AuraBeats         (entry - python AuraBeats)
    config.py
    core/             (bot, userbot, calls, database, settings)
    database/         (users, chats, playlists, queue_db, settings_db, stats)
    plugins/          (start, help, play, vplay, controls, queue, effects,
                       download, playlist, ai, lyrics, inline, admin,
                       sudo, stats, settings, callback)
    utils/            (formatters, decorators, logger, yt_helper, streamer,
                       ffmpeg, throttle, keyboard, inline_ui, errors)
    strings/          (en, hi)
    assets/           (images, fonts, emoji.json)
    docs/             (FEATURES, SETUP, DEPLOY, API)
    scripts/          (start.sh, deploy.sh)
    .github/workflows/

Deploy on Termux:

  pkg install python git ffmpeg -y
  git clone https://github.com/AuraBeatsOfficial/AuraBeats.git
  cd AuraBeats
  pip install -r requirements.txt
  cp .env.example .env
  nano .env
  python AuraBeats

Deploy on Docker:

  cp .env.example .env
  nano .env
  docker compose up -d --build

License: MIT (c) AuraBeats
