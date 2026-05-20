#!/usr/bin/env python3
"""Channel tools: growth tracking, weekly digest, auto-clean, cross-post, anniversary."""

import asyncio
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone

TELEGRAM_CONFIG = os.path.expanduser("~/.codex/telegram-bridge.json")
SESSION_FILE = os.path.expanduser("~/.codex/welcome_session")
WELCOME_DB = os.path.expanduser("~/.codex/welcomed_users.json")
GROWTH_LOG = os.path.expanduser("~/.codex/growth_log.json")
CROSSPOST_CONFIG = os.path.expanduser("~/.codex/crosspost_targets.json")
CHANNEL_USERNAME = "dealwalaindiain"

API_ID_FILE = os.path.expanduser("~/.codex/telegram_api_id")
API_HASH_FILE = os.path.expanduser("~/.codex/telegram_api_hash")

def get_creds():
    api_id = int(open(API_ID_FILE).read().strip())
    api_hash = open(API_HASH_FILE).read().strip()
    phone = os.environ.get("WELCOME_PHONE", "+919730472789")
    with open(TELEGRAM_CONFIG) as f:
        bot_token = json.load(f)["botToken"]
    return api_id, api_hash, phone, bot_token

# ──────────────── 1. GROWTH TRACKING ────────────────

async def track_growth():
    api_id, api_hash, phone, _ = get_creds()
    from telethon import TelegramClient
    from telethon.tl.functions.channels import GetFullChannelRequest

    client = TelegramClient(SESSION_FILE, api_id, api_hash)
    await client.start(phone=phone)
    try:
        channel = await client.get_entity(f"@{CHANNEL_USERNAME}")
        full = await client(GetFullChannelRequest(channel))
        count = getattr(full.full_chat, "participants_count", 0)

        log = {"snapshots": []}
        if os.path.exists(GROWTH_LOG):
            with open(GROWTH_LOG) as f:
                log = json.load(f)

        now = datetime.now(timezone.utc)
        today = now.strftime("%Y-%m-%d")

        log["snapshots"].append({"date": now.isoformat(), "count": count})
        log["snapshots"] = log["snapshots"][-10000:]  # keep last 10k

        # Daily summary
        today_snapshots = [s for s in log["snapshots"] if s["date"].startswith(today)]
        if today_snapshots:
            today_min = min(s["count"] for s in today_snapshots)
            today_max = max(s["count"] for s in today_snapshots)
            log["daily"] = log.get("daily", {})
            log["daily"][today] = {"min": today_min, "max": today_max,
                                   "latest": today_snapshots[-1]["count"]}

        # Calculate 7-day trend
        seven_days_ago = (now - timedelta(days=7)).isoformat()
        week_snapshots = [s for s in log["snapshots"] if s["date"] > seven_days_ago]
        if week_snapshots:
            week_start = week_snapshots[0]["count"]
            week_end = week_snapshots[-1]["count"]
            diff = week_end - week_start
            trend = "📈" if diff > 0 else "📉" if diff < 0 else "➡️"
            log["weekly_trend"] = {"start": week_start, "end": week_end, "diff": diff}

        with open(GROWTH_LOG, "w") as f:
            json.dump(log, f, indent=2)

        print(f"📊 Members: {count}")
        if "weekly_trend" in log:
            w = log["weekly_trend"]
            print(f"   7-day: {w['start']} → {w['end']} ({w['diff']:+d})")
        if today in log.get("daily", {}):
            d = log["daily"][today]
            print(f"   Today: min={d['min']} max={d['max']} current={d['latest']}")

    finally:
        await client.disconnect()

# ──────────────── 2. WEEKLY DEAL DIGEST ────────────────

async def weekly_digest():
    api_id, api_hash, phone, bot_token = get_creds()
    from telethon import TelegramClient
    from telethon.tl.functions.messages import GetHistoryRequest

    client = TelegramClient(SESSION_FILE, api_id, api_hash)
    await client.start(phone=phone)
    try:
        channel = await client.get_entity(f"@{CHANNEL_USERNAME}")
        cutoff = datetime.now(timezone.utc) - timedelta(days=7)

        deals = []
        async for msg in client.iter_messages(channel, limit=500):
            if msg.date.replace(tzinfo=timezone.utc) < cutoff:
                break
            if msg.text and ("Buy on Amazon" in msg.text or "Buy on Flipkart" in msg.text):
                title = msg.text.split("\n")[0][:80] if msg.text else ""
                price = ""
                for line in msg.text.split("\n"):
                    if "₹" in line:
                        price = line.strip()[:30]
                        break
                deals.append({"title": title, "price": price, "date": msg.date.strftime("%b %d"), "id": msg.id})

        if not deals:
            print("No deals found in the last 7 days")
            return

        # Group by day
        by_day = {}
        for d in deals:
            by_day.setdefault(d["date"], []).append(d)

        text = f"📅 <b>WEEKLY DEAL DIGEST</b>\n━━━━━━━━━━━━━━━━━\n\n"
        for day in sorted(by_day.keys(), reverse=True):
            text += f"<b>{day}</b> — {len(by_day[day])} deals\n"
            for d in by_day[day][:3]:
                text += f"  • {d['title'][:50]}\n"
            text += "\n"

        text += f"━━━━━━━━━━━━━━━━━\n📊 <b>Total deals: {len(deals)}</b>\n🔔 <b>@dealwalaindiain</b>"

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = json.dumps({
            "chat_id": -1003622769806, "text": text, "parse_mode": "HTML",
            "disable_web_page_preview": True
        }).encode()
        r = subprocess.run(["curl", "-s", "-X", "POST", url,
            "-H", "Content-Type: application/json", "-d", data.decode()],
            capture_output=True, text=True, timeout=10)
        resp = json.loads(r.stdout)
        if resp.get("ok"):
            print(f"✅ Digest posted (MsgID: {resp['result']['message_id']})")
        else:
            print(f"❌ Digest failed: {resp.get('description')}")

    finally:
        await client.disconnect()

# ──────────────── 3. AUTO-CLEAN OLD POSTS ────────────────

async def auto_clean():
    """Delete deal posts older than 24 hours using user account (admin)."""
    api_id, api_hash, phone, _ = get_creds()
    from telethon import TelegramClient
    from telethon.tl.functions.messages import DeleteMessagesRequest

    client = TelegramClient(SESSION_FILE, api_id, api_hash)
    await client.start(phone=phone)
    try:
        channel = await client.get_entity(f"@{CHANNEL_USERNAME}")
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        deleted = 0

        async for msg in client.iter_messages(channel, limit=200):
            if msg.date.replace(tzinfo=timezone.utc) > cutoff:
                continue
            if not msg.text or ("Buy on Amazon" not in msg.text and "Buy on Flipkart" not in msg.text and "WELCOME" not in msg.text and "DIGEST" not in msg.text):
                continue
            try:
                await client(DeleteMessagesRequest(channel, [msg.id]))
                deleted += 1
            except Exception as e:
                print(f"  Skipped msg {msg.id}: {e}")

        print(f"🧹 Cleaned {deleted} old deal(s)")

    finally:
        await client.disconnect()

# ──────────────── 4. CROSS-POSTING ────────────────

async def crosspost():
    """Forward latest deals to configured target channels/groups."""
    if not os.path.exists(CROSSPOST_CONFIG):
        print("No crosspost targets configured. Create ~/.codex/crosspost_targets.json")
        return

    with open(CROSSPOST_CONFIG) as f:
        targets = json.load(f).get("targets", [])

    if not targets:
        print("No targets in config")
        return

    api_id, api_hash, phone, _ = get_creds()
    from telethon import TelegramClient
    from telethon.tl.functions.messages import ForwardMessagesRequest

    client = TelegramClient(SESSION_FILE, api_id, api_hash)
    await client.start(phone=phone)
    try:
        channel = await client.get_entity(f"@{CHANNEL_USERNAME}")

        # Get latest 3 deal messages
        deal_msgs = []
        async for msg in client.iter_messages(channel, limit=30):
            if msg.text and ("Buy on Amazon" in msg.text or "Buy on Flipkart" in msg.text):
                deal_msgs.append(msg.id)
                if len(deal_msgs) >= 3:
                    break

        if not deal_msgs:
            print("No deals to cross-post")
            return

        for target in targets:
            try:
                entity = await client.get_entity(target)
                await client(ForwardMessagesRequest(
                    from_peer=channel,
                    id=deal_msgs,
                    to_peer=entity,
                    drop_author=True
                ))
                name = getattr(entity, "title", getattr(entity, "username", str(target)))
                print(f"📤 Forwarded {len(deal_msgs)} deals to {name}")
            except Exception as e:
                print(f"  ❌ {target}: {e}")

    finally:
        await client.disconnect()

# ──────────────── 5. JOIN ANNIVERSARY DM ────────────────

async def anniversary():
    """Check if any member hit a 1-month milestone and send a special DM."""
    api_id, api_hash, phone, bot_token = get_creds()
    from telethon import TelegramClient
    from telethon.tl.functions.channels import GetParticipantsRequest
    from telethon.tl.types import ChannelParticipantsRecent

    if not os.path.exists(WELCOME_DB):
        print("No welcome DB yet")
        return

    with open(WELCOME_DB) as f:
        db = json.load(f)

    # Track first seen date per user (from welcome_bot)
    first_seen = db.get("first_seen", {})
    sent = set(db.get("anniversary_sent", []))

    client = TelegramClient(SESSION_FILE, api_id, api_hash)
    await client.start(phone=phone)
    try:
        channel = await client.get_entity(f"@{CHANNEL_USERNAME}")
        participants = await client(GetParticipantsRequest(
            channel, ChannelParticipantsRecent(), offset=0, limit=200, hash=0
        ))

        now = datetime.now(timezone.utc)
        celebrated = 0

        for user in participants.users:
            uid = str(user.id)
            if uid in sent:
                continue
            if user.bot or user.deleted:
                continue

            joined = getattr(user, "joined_date", None)
            if not joined and uid in first_seen:
                joined = datetime.fromisoformat(first_seen[uid])

            if not joined:
                first_seen[uid] = now.isoformat()
                continue

            # Check if 30 days passed
            days = (now - joined).days
            if days < 28:
                continue

            name = getattr(user, "first_name", "") or f"User {uid}"

            # Check exact anniversary: 30, 60, 90... days
            milestones = [m for m in [30, 60, 90, 120, 150, 180, 365] if days >= m and days < m + 7]
            if not milestones:
                continue

            milestone = milestones[0]
            text = (
                f"🎉 <b>Happy {milestone}-day anniversary on @dealwalaindiain!</b>\n\n"
                f"Thank you for being part of our community for {milestone} days! 🙏\n\n"
                f"🔥 You've saved thousands on deals we've posted!\n"
                f"📤 Share the channel with friends who love saving money!\n"
                f"🔔 Stay tuned — more deals coming every 15 mins!"
            )

            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = json.dumps({
                "chat_id": int(uid), "text": text, "parse_mode": "HTML",
                "disable_web_page_preview": True
            }).encode()
            r = subprocess.run(["curl", "-s", "-X", "POST", url,
                "-H", "Content-Type: application/json", "-d", data.decode()],
                capture_output=True, text=True, timeout=10)
            resp = json.loads(r.stdout)

            if resp.get("ok"):
                print(f"🎂 {name} ({uid}) — {milestone} days!")
                celebrated += 1
                sent.add(uid)
                db.setdefault("anniversary_sent", [])
                db["anniversary_sent"] = list(set(db["anniversary_sent"] + [uid]))[-5000:]

        db["first_seen"] = {k: v for k, v in first_seen.items()}
        with open(WELCOME_DB, "w") as f:
            json.dump(db, f, indent=2)

        if celebrated:
            print(f"🎉 Celebrated {celebrated} anniversary(ies)!")
        else:
            print("ℹ️ No anniversaries today")

    finally:
        await client.disconnect()

# ──────────────── MAIN ────────────────

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"

    if cmd == "track":
        asyncio.run(track_growth())
    elif cmd == "digest":
        asyncio.run(weekly_digest())
    elif cmd == "cleanup":
        asyncio.run(auto_clean())
    elif cmd == "crosspost":
        asyncio.run(crosspost())
    elif cmd == "anniversary":
        asyncio.run(anniversary())
    elif cmd == "all":
        asyncio.run(track_growth())
        print()
        asyncio.run(auto_clean())
        print()
        asyncio.run(anniversary())
    else:
        print("Usage: python3 channel_tools.py <command>")
        print("  track       — Member growth tracking")
        print("  digest      — Weekly deal digest")
        print("  cleanup     — Auto-clean old posts (>24h)")
        print("  crosspost   — Forward deals to other groups")
        print("  anniversary — Join anniversary DM")
        print("  all         — Run track + cleanup + anniversary")
