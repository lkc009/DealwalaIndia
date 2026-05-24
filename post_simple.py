#!/usr/bin/env python3
"""
DealwalaIndia - Simple Deal Poster using Bot API
Uses the same approach as post_deals.py: Telegram Bot API via curl
"""

import json
import os
import sys
import time
import random
import subprocess
from datetime import datetime

TELEGRAM_CONFIG = os.path.expanduser("~/.codex/telegram-bridge.json")
CHANNEL_ID = -1003622769806
CHANNEL_NAME = "@dealwalaindiain"
POOL_FILE = "deals_pool.json"
HISTORY_FILE = os.path.expanduser("~/.codex/dealwalaindia_history.json")

REACTIONS = [
    [{"type": "emoji", "emoji": "🔥"}],
    [{"type": "emoji", "emoji": "❤️"}],
    [{"type": "emoji", "emoji": "💯"}],
    [{"type": "emoji", "emoji": "🎉"}],
    [{"type": "emoji", "emoji": "👍"}],
]

def load_json(path):
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return {}

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, default=str)

def get_bot_token():
    cfg = load_json(TELEGRAM_CONFIG)
    return cfg.get('botToken', '')

def add_reaction(token, msg_id):
    url = f"https://api.telegram.org/bot{token}/setMessageReaction"
    reaction = random.choice(REACTIONS)
    data = json.dumps({
        "chat_id": CHANNEL_ID,
        "message_id": msg_id,
        "reaction": reaction,
        "is_big": True
    })
    try:
        r = subprocess.run(
            ["curl", "-s", "-X", "POST", url,
             "-H", "Content-Type: application/json", "-d", data],
            capture_output=True, text=True, timeout=10
        )
        resp = json.loads(r.stdout)
        if resp.get("ok"):
            print(f"   ✨ Reaction: {reaction[0]['emoji']}")
    except:
        pass

def post_to_channel(token, text, buttons=None):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    data = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    
    if buttons:
        keyboard = [{"text": t, "url": u} for t, u in buttons]
        rows = [keyboard[i:i+2] for i in range(0, len(keyboard), 2)]
        data["reply_markup"] = {"inline_keyboard": rows}
    
    try:
        r = subprocess.run(
            ["curl", "-s", "-X", "POST", url,
             "-H", "Content-Type: application/json", "-d", json.dumps(data)],
            capture_output=True, text=True, timeout=15
        )
        resp = json.loads(r.stdout)
        if resp.get("ok"):
            msg_id = resp["result"]["message_id"]
            print(f"   ✅ Posted! MsgID: {msg_id}")
            add_reaction(token, msg_id)
            return msg_id
        else:
            print(f"   ❌ Failed: {resp.get('description', 'unknown error')}")
            return None
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def format_deal(deal, idx):
    title = deal.get('title', 'Deal')
    price = deal.get('price', 0)
    mrp = deal.get('mrp', 0)
    discount = deal.get('discount', 0)
    link = deal.get('link', '')
    source = deal.get('source', 'Deal')
    features = deal.get('features', [])
    
    fire = ["🔥", "⚡", "💥", "🌟", "🎯"][idx % 5]
    
    lines = [f"{fire} <b>{title[:70]}</b>"]
    
    if discount > 0 and mrp:
        savings = mrp - price
        lines.append(f"   💰 ₹{price:,}  (MRP: ₹{mrp:,})")
        lines.append(f"   📉 {discount}% OFF  |  💸 Save ₹{savings:,}")
    elif price > 0:
        lines.append(f"   💰 ₹{price:,}")
    
    if features:
        feat = " • ".join(features[:3])
        lines.append(f"   ✨ {feat}")
    
    lines.append(f"   🔗 <a href=\"{link}\">Buy on {source}</a>")
    lines.append("")
    
    return "\n".join(lines), link

def main():
    print("=" * 60)
    print("DealwalaIndia - Simple Deal Poster (Bot API)")
    print("=" * 60)
    
    # Get bot token
    token = get_bot_token()
    if not token:
        print("ERROR: No bot token found!")
        return
    
    # Load deals
    pool = load_json(POOL_FILE)
    deals = pool.get('deals', [])
    if not deals:
        print("No deals in pool! Run fetch_best_deals.py first.")
        return
    
    print(f"\n📦 Found {len(deals)} deals in pool")
    
    # Load history
    history = load_json(HISTORY_FILE)
    posted = set(history.get('posted', []))
    print(f"📋 {len(posted)} deals in history")
    
    # Filter unposted
    unposted = [d for d in deals if d.get('link', '') not in posted]
    print(f"✨ {len(unposted)} new deals available")
    
    if not unposted:
        print("\nAll deals already posted!")
        return
    
    # Take up to 3 deals
    to_post = unposted[:3]
    print(f"\n📤 Posting {len(to_post)} deals...\n")
    
    # Build message
    now = datetime.now().strftime("%I:%M %p")
    headers = [
        f"🔥 <b>BEST DEALS</b> — {now}",
        f"⚡ <b>FLASH DEALS</b> — {now}",
        f"💰 <b>TODAY'S HOT PICKS</b> — {now}",
    ]
    
    msg_parts = [random.choice(headers), "", "━━━━━━━━━━━━━━━━━━━━━━━", ""]
    buttons = []
    posted_links = []
    
    for i, deal in enumerate(to_post):
        deal_text, link = format_deal(deal, i)
        msg_parts.append(deal_text)
        posted_links.append(link)
        
        # Add button
        source = deal.get('source', 'Shop')
        price = deal.get('price', 0)
        btn_text = f"🛒 ₹{price:,} — {source}" if price else f"🛒 View on {source}"
        buttons.append((btn_text, link))
    
    # Footer
    footers = [
        f"━━━━━━━━━━━━━━━━━━━━━━━\n📢 Join <a href=\"https://t.me/dealwalaindiain\">{CHANNEL_NAME}</a>\n🔔 Never miss a deal!",
        f"━━━━━━━━━━━━━━━━━━━━━━━\n💡 Prices change fast — grab deals NOW!\n📲 Share {CHANNEL_NAME} with friends",
    ]
    msg_parts.append(random.choice(footers))
    
    full_msg = "\n".join(msg_parts)
    
    print(f"📝 Message: {len(full_msg)} chars")
    print("-" * 40)
    print(full_msg[:300] + "..." if len(full_msg) > 300 else full_msg)
    print("-" * 40)
    
    # Post
    msg_id = post_to_channel(token, full_msg, buttons)
    
    if msg_id:
        # Update history
        history.setdefault('posted', []).extend(posted_links)
        history['last_posted'] = datetime.now().isoformat()
        history['last_msg_id'] = msg_id
        save_json(HISTORY_FILE, history)
        
        print(f"\n✅ Done! Posted {len(posted_links)} deals to {CHANNEL_NAME}")
    else:
        print("\n❌ Posting failed!")

if __name__ == "__main__":
    main()
