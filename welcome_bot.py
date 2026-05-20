#!/usr/bin/env python3
"""Channel welcome bot — polls members every 5 min, greets newcomers via DM."""

import asyncio
import json
import os
import subprocess
import sys

TELEGRAM_CONFIG = os.path.expanduser("~/.codex/telegram-bridge.json")
WELCOME_DB = os.path.expanduser("~/.codex/welcomed_users.json")
SESSION_FILE = os.path.expanduser("~/.codex/welcome_session")
CHANNEL_USERNAME = "dealwalaindiain"

WELCOME_TEXT = (
    "👋 <b>Welcome to @dealwalaindiain!</b>\n\n"
    "🔥 You've joined India's fastest deal channel!\n"
    "✅ New deals posted <b>every 15 minutes</b>\n"
    "🛒 Amazon + Flipkart best deals with affiliate savings\n\n"
    "📌 <b>Tip:</b> Tap 🔔 and turn on <b>Notifications</b> to never miss a deal!\n"
    "📤 Share with friends who love saving money!"
)

def load_db():
    if os.path.exists(WELCOME_DB):
        with open(WELCOME_DB) as f:
            return json.load(f)
    return {"known": [], "welcomed": []}

def save_db(db):
    os.makedirs(os.path.dirname(WELCOME_DB), exist_ok=True)
    with open(WELCOME_DB, "w") as f:
        json.dump(db, f)

def send_dm(token, user_id):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = json.dumps({
        "chat_id": user_id,
        "text": WELCOME_TEXT,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }).encode()
    r = subprocess.run(["curl", "-s", "-X", "POST", url,
        "-H", "Content-Type: application/json", "-d", data.decode()],
        capture_output=True, text=True, timeout=10)
    resp = json.loads(r.stdout)
    if resp.get("ok"):
        return True
    if resp.get("error_code") == 403:
        return "blocked"
    return False

async def main():
    from telethon import TelegramClient
    from telethon.tl.functions.channels import GetParticipantsRequest
    from telethon.tl.types import ChannelParticipantsRecent

    api_id_file = os.path.expanduser("~/.codex/telegram_api_id")
    api_hash_file = os.path.expanduser("~/.codex/telegram_api_hash")
    if not os.path.exists(api_id_file) or not os.path.exists(api_hash_file):
        print("Missing api credentials")
        return

    api_id = int(open(api_id_file).read().strip())
    api_hash = open(api_hash_file).read().strip()

    phone = os.environ.get("WELCOME_PHONE")
    if not phone:
        print("Missing WELCOME_PHONE env var")
        return

    with open(TELEGRAM_CONFIG) as f:
        bot_token = json.load(f)["botToken"]

    db = load_db()
    known = set(db.get("known", []))
    welcomed = set(db.get("welcomed", []))

    client = TelegramClient(SESSION_FILE, api_id, api_hash)
    await client.start(phone=phone)

    try:
        channel = await client.get_entity(f"@{CHANNEL_USERNAME}")
        participants = await client(GetParticipantsRequest(
            channel, ChannelParticipantsRecent(), offset=0, limit=200, hash=0
        ))

        current_ids = set()
        new_count = 0

        for user in participants.users:
            uid = user.id
            current_ids.add(uid)
            if user.bot or user.deleted:
                continue
            if uid in known:
                continue
            if uid in welcomed:
                known.add(uid)
                continue

            name = getattr(user, "first_name", "") or str(uid)
            result = send_dm(bot_token, uid)
            if result is True:
                print(f"  ✅ {name} ({uid})")
                new_count += 1
            elif result == "blocked":
                print(f"  ⏭️ {name} ({uid}) — blocked")
            else:
                print(f"  ❌ {name} ({uid}) — failed")
            known.add(uid)
            welcomed.add(uid)

        if new_count:
            db["known"] = list(known)[-5000:]
            db["welcomed"] = list(welcomed)[-5000:]
            save_db(db)
            print(f"📬 Welcomed {new_count} new member(s)!")
        else:
            diff = current_ids - known
            if diff:
                known |= diff
                db["known"] = list(known)[-5000:]
                save_db(db)
                print(f"ℹ️ Synced {len(diff)} members")
            else:
                print("ℹ️ No new members")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
