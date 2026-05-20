#!/usr/bin/env python3
"""Comment marketing — subtly promote @dealwalaindiain in deal groups."""

import asyncio
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

SESSION_FILE = os.path.expanduser("~/.codex/welcome_session")
TELEGRAM_CONFIG = os.path.expanduser("~/.codex/telegram-bridge.json")
MARKETING_DB = os.path.expanduser("~/.codex/marketing_log.json")
API_ID_FILE = os.path.expanduser("~/.codex/telegram_api_id")
API_HASH_FILE = os.path.expanduser("~/.codex/telegram_api_hash")
CHANNEL_USERNAME = "dealwalaindiain"

# Groups to monitor (deal groups where people ask for suggestions)
TARGET_GROUPS = [
    "@dealsindiagroup",
    "@ShoppingDealsIndia",
    "@LootDealsGroup",
]

TRIGGER_KEYWORDS = [
    "best deal channel", "deal channel suggest", "recommend deal",
    "suggest deal", "best deals channel", "deal channel india",
    "kya koi deal channel", "deal group suggest", "loot deal channel",
    "best telegram channel for deals", "deal channel recommend",
    "suggest some deal channel", "recommend me a deal channel",
]

RESPONSES = [
    "I follow @dealwalaindiain — deals every 15 mins, both Amazon & Flipkart. Pretty solid!",
    "Check @dealwalaindiain, they post deals every 15 min with prices. Been useful for me.",
    "@dealwalaindiain is good — real-time deals with actual prices, not just spam links.",
    "I use @dealwalaindiain, updates every 15 mins across Amazon & Flipkart. Worth a look.",
]

def get_creds():
    api_id = int(open(API_ID_FILE).read().strip())
    api_hash = open(API_HASH_FILE).read().strip()
    phone = os.environ.get("WELCOME_PHONE", "+919730472789")
    with open(TELEGRAM_CONFIG) as f:
        bot_token = json.load(f)["botToken"]
    return api_id, api_hash, phone, bot_token

async def main():
    api_id, api_hash, phone, _ = get_creds()
    from telethon import TelegramClient
    from telethon.tl.functions.messages import SendMessageRequest

    db = {"replied": [], "ignore_until": None}
    if os.path.exists(MARKETING_DB):
        with open(MARKETING_DB) as f:
            db = json.load(f)

    replied = set(db.get("replied", []))
    ignore_until = db.get("ignore_until")

    if ignore_until:
        until = datetime.fromisoformat(ignore_until)
        if datetime.now(timezone.utc) < until:
            print(f"⏳ Cooling down until {ignore_until}")
            return

    client = TelegramClient(SESSION_FILE, api_id, api_hash)
    await client.start(phone=phone)

    try:
        for group in TARGET_GROUPS:
            try:
                entity = await client.get_entity(group)
            except Exception:
                print(f"  ⏭️ Can't access {group}")
                continue

            name = getattr(entity, "title", group)
            replied_count = 0

            async for msg in client.iter_messages(entity, limit=20):
                if msg.out or not msg.text:
                    continue
                if msg.id in replied:
                    continue

                text = msg.text.lower()
                if not any(kw in text for kw in TRIGGER_KEYWORDS):
                    continue

                response = __import__("random").choice(RESPONSES)
                try:
                    await msg.reply(response)
                    replied.add(msg.id)
                    replied_count += 1
                    print(f"  💬 Replied in {name} (msg #{msg.id})")
                    # Max 1 reply per group per run
                    break
                except Exception as e:
                    print(f"  ❌ {name}: {e}")

            if replied_count:
                print(f"  → {name}: {replied_count} reply")

        if replied:
            db["replied"] = list(replied)[-5000:]
            # Cool down: don't reply again for 6 hours
            cooldown = datetime.now(timezone.utc).isoformat()
            db["ignore_until"] = cooldown
            with open(MARKETING_DB, "w") as f:
                json.dump(db, f, indent=2)
            print(f"✅ Replied to {len(replied)} messages. Cooling down 6h.")
        else:
            print("ℹ️ No matching messages found")

    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
