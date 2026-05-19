#!/usr/bin/env python3
"""
DealwalaIndia - EXPERT Affiliate Deal Poster v3
Optimized for maximum conversions with prices when available.
"""

import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
import random
import tweepy
from datetime import datetime

TELEGRAM_CONFIG = os.path.expanduser("~/.codex/telegram-bridge.json")
CHANNEL_ID = -1003622769806
CHANNEL_JOIN = "https://t.me/dealwalaindiain"
CHANNEL_NAME = "@dealwalaindiain"
DEALS_HISTORY = os.path.expanduser("~/.codex/dealwalaindia_history.json")
MAX_DEALS = 4
AFFILIATE_ID = "lalitkcho"
AMAZON_TAG = "123450005-21"
TWITTER_CREDENTIALS = os.path.expanduser("~/.codex/twitter_dealwala.json")
POOL_FILE = "deals_pool.json"
CLOUD_MODE = os.environ.get("CLOUD_MODE", "").lower() == "true"

REACTION_SETS = [
    [{"type": "emoji", "emoji": "🔥"}],
    [{"type": "emoji", "emoji": "❤️"}],
    [{"type": "emoji", "emoji": "💯"}],
    [{"type": "emoji", "emoji": "🤩"}],
    [{"type": "emoji", "emoji": "👍"}],
    [{"type": "emoji", "emoji": "👏"}],
    [{"type": "emoji", "emoji": "😍"}],
    [{"type": "emoji", "emoji": "🎉"}],
    [{"type": "emoji", "emoji": "🏆"}],
    [{"type": "emoji", "emoji": "🔥"}],
    [{"type": "emoji", "emoji": "❤️"}],
    [{"type": "emoji", "emoji": "💯"}],
]

PROMO_MESSAGES = [
    {
        "header": "📢 <b>SPREAD THE SAVINGS!</b>",
        "body": "Forward this to 3 friends who deserve good deals!\n💬 <a href=\"https://t.me/dealwalaindiain\">Share Channel</a>",
    },
    {
        "header": "🔔 <b>NEVER MISS A DEAL AGAIN!</b>",
        "body": "Tap <b>Subscribe</b> + 🔔 Turn on notifications!\nDeals drop every 15 mins — first come, first saved!",
    },
    {
        "header": "🚀 <b>JOIN 10K+ SMART SHOPPERS!</b>",
        "body": "Why pay full price when deals are FREE?\n📲 <b>Share</b> this channel with family & friends!",
    },
    {
        "header": "⚡ <b>DEALS THIS GOOD DON'T LAST!</b>",
        "body": "Prices change every minute — grab NOW!\n💰 <a href=\"https://t.me/dealwalaindiain\">Subscribe for Daily Deals</a>",
    },
    {
        "header": "🎯 <b>YOUR DAILY DOSE OF SAVINGS!</b>",
        "body": "Flipkart + Amazon deals at your fingertips!\n📤 <b>Share</b> this post — someone needs these deals!",
    },
    {
        "header": "🔥 <b>THE SECRET TO SAVING ₹1000s!</b>",
        "body": "We track prices 24/7 so you don't have to!\n🔔 <b>Subscribe</b> + share with your deal-hunting squad!",
    },
    {
        "header": "💎 <b>PREMIUM DEALS, ZERO COST!</b>",
        "body": "This channel is FREE — but the savings are priceless!\n📲 Forward to friends before prices go up!",
    },
    {
        "header": "🏆 <b>INDIA'S SMARTEST DEAL CHANNEL!</b>",
        "body": "Real prices. Real discounts. Real savings.\n🔔 <a href=\"https://t.me/dealwalaindiain\">Join Now</a> + share the love!",
    },
]

HEADER_STYLES = [
    "🔥 <b>BEST DEALS</b> — {now}",
    "⚡ <b>FLASH DEALS</b> — {now}",
    "💰 <b>TODAY'S HOT PICKS</b> — {now}",
    "🎯 <b>TOP DEALS RIGHT NOW</b> — {now}",
    "🚨 <b>PRICE DROP ALERT</b> — {now}",
    "🏷️ <b>MEGA OFFERS</b> — {now}",
    "💥 <b>DEAL OF THE HOUR</b> — {now}",
    "🌟 <b>HANDPICKED DEALS</b> — {now}",
]

URGENCY_LINES = [
    "⏰ <b>Hurry! Stock selling fast</b>",
    "⚡ <b>Grab before prices go up!</b>",
    "🔥 <b>Deal won't last long</b>",
    "💨 <b>First come, first saved!</b>",
    "🏃 <b>Run, don't walk!</b>",
    "⏳ <b>Countdown started — limited stock!</b>",
    "🚀 <b>Deals disappearing fast!</b>",
    "🎯 <b>Smart shoppers grab NOW</b>",
]

FOOTER_MESSAGES = [
    "━━━━━━━━━━━━━━━━━\n📲 <b>Share with friends → Save together!</b>\n🔔 <b>Subscribe: </b>@dealwalaindiain",
    "━━━━━━━━━━━━━━━━━\n💬 <b>Forward this deal — someone will thank you!</b>\n🔔 <b>Turn on notifications: </b>@dealwalaindiain",
    "━━━━━━━━━━━━━━━━━\n🚀 <b>Don't let your friends pay full price!</b>\n📤 <b>Share this channel now</b>",
    "━━━━━━━━━━━━━━━━━\n💰 <b>More deals coming in 15 mins!</b>\n🔔 <b>Stay subscribed: </b>@dealwalaindiain",
    "━━━━━━━━━━━━━━━━━\n🏆 <b>India's #1 Deal Channel — FREE!</b>\n📲 <b>Share + Subscribe for daily savings</b>",
    "━━━━━━━━━━━━━━━━━\n⚡ <b>Prices change every minute!</b>\n🔔 <b>Subscribe now + share with 3 friends!</b>",
    "━━━━━━━━━━━━━━━━━\n🎁 <b>Good things come to those who subscribe!</b>\n📤 <b>Share this post before it's gone!</b>",
    "━━━━━━━━━━━━━━━━━\n🔥 <b>Deals this good are RARE!</b>\n💬 <b>Forward to family groups now!</b>",
]

QUERY_SETS = [
    [("mobile under 15000", 15000), ("laptop under 30000", 30000), ("headphone bluetooth", 3000)],
    [("mobile under 10000", 10000), ("ac 1.5 ton", 35000), ("shoe men running", 2000)],
    [("mobile under 20000", 20000), ("refrigerator double door", 25000), ("washing machine", 15000)],
    [("mobile under 25000", 25000), ("smartwatch", 4000), ("earbuds", 2000)],
    [("tv 55 inch", 40000), ("monitor 24 inch", 12000), ("powerbank 20000", 1500)],
    [("camera dslr", 30000), ("tablet", 15000), ("speaker bluetooth", 3000)],
]

def get_query_set():
    minute = int(datetime.now().strftime("%M"))
    hour = int(datetime.now().strftime("%H"))
    return QUERY_SETS[(hour * 6 + minute // 10) % len(QUERY_SETS)]

def get_reaction():
    return REACTION_SETS[random.randint(0, len(REACTION_SETS)-1)]

def get_header(now):
    return random.choice(HEADER_STYLES).format(now=now)

def get_urgency():
    return random.choice(URGENCY_LINES)

def get_footer():
    return random.choice(FOOTER_MESSAGES)

def get_promo():
    return random.choice(PROMO_MESSAGES)

def load_config():
    with open(TELEGRAM_CONFIG) as f:
        return json.load(f)["botToken"]

def load_history():
    if os.path.exists(DEALS_HISTORY):
        with open(DEALS_HISTORY) as f:
            return json.load(f)
    return {"posted": [], "last": None}

def save_history(h):
    os.makedirs(os.path.dirname(DEALS_HISTORY), exist_ok=True)
    with open(DEALS_HISTORY, "w") as f:
        json.dump(h, f, indent=2)

def curl(url, timeout=10, use_amazon_headers=False):
    headers = [
        "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    ]
    if use_amazon_headers:
        headers.extend([
            "-H", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "-H", "Accept-Language: en-US,en;q=0.9",
            "-H", "Accept-Encoding: gzip, deflate, br",
        ])
    headers.append("--compressed")
    cmd = ["curl", "-s", "-L", "--max-time", str(timeout)] + headers + [url]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+2)
        return r.stdout if r.returncode == 0 and len(r.stdout) > 500 else None
    except:
        return None

def post_with_buttons(token, text, buttons):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    keyboard = [{"text": t, "url": u} for t, u in buttons]
    rows = [keyboard[i:i+2] for i in range(0, len(keyboard), 2)]
    data = json.dumps({
        "chat_id": CHANNEL_ID, "text": text, "parse_mode": "HTML",
        "disable_web_page_preview": True,
        "reply_markup": {"inline_keyboard": rows}
    }).encode()
    r = subprocess.run(["curl", "-s", "-X", "POST", url,
        "-H", "Content-Type: application/json", "-d", data.decode()],
        capture_output=True, text=True, timeout=15)
    resp = json.loads(r.stdout)
    if resp.get("ok"):
        msg_id = resp["result"]["message_id"]
        print(f"  Posted! MsgID: {msg_id}")
        add_reaction(token, msg_id)
        return True
    print(f"  Failed: {resp}")
    return False

def add_reaction(token, msg_id):
    url = f"https://api.telegram.org/bot{token}/setMessageReaction"
    reactions = get_reaction()
    data = json.dumps({
        "chat_id": CHANNEL_ID,
        "message_id": msg_id,
        "reaction": reactions,
        "is_big": True
    }).encode()
    try:
        r = subprocess.run(["curl", "-s", "-X", "POST", url,
            "-H", "Content-Type: application/json", "-d", data.decode()],
            capture_output=True, text=True, timeout=10)
        resp = json.loads(r.stdout)
        if resp.get("ok"):
            print(f"  ✨ Reaction: {reactions[0]['emoji']}")
        else:
            print(f"  Reaction failed: {resp.get('description', 'unknown')}")
    except Exception as e:
        print(f"  Reaction error: {e}")

def add_affiliate(link):
    if "flipkart.com" in link:
        if "affid=" not in link:
            sep = "&" if "?" in link else "?"
            return f"{link}{sep}affid={AFFILIATE_ID}"
        return link
    if "amazon.in" in link or "amzn.to" in link or "amzn.in" in link:
        if "tag=" not in link:
            sep = "&" if "?" in link else "?"
            return f"{link}{sep}tag={AMAZON_TAG}"
        return link
    return None

def has_affiliate(link):
    if "flipkart.com" in link:
        return "affid=" in link
    if "amazon.in" in link or "amzn" in link:
        return "tag=" in link
    return False

def extract_flipkart_products(content, price_limit=None):
    """Extract product links + names from Flipkart search pages."""
    deals = []
    seen = set()
    
    for m in re.finditer(r'(https?://[^\s"\'<>]*flipkart\.com/[^\s"\'<>]+/p/[^\s"\'<>]+)', content):
        link = m.group(1).split('"')[0].split("'")[0].split('>')[0]
        if link in seen:
            continue
        seen.add(link)
        
        # Get title from context (JSON-LD name field)
        ctx = content[max(0,m.start()-200):m.start()+100]
        title_m = re.search(r'"name"\s*:\s*"([^"]{5,80})"', ctx)
        if not title_m:
            title_m = re.search(r'data-title=["\']([^"\']+)["\']', ctx)
        title = title_m.group(1).strip() if title_m else ""
        if not title or len(title) < 5:
            continue
        
        aff_link = add_affiliate(link)
        if not aff_link:
            continue
        
        deals.append({
            "title": title[:60],
            "price": 0,
            "mrp": None,
            "discount": 0,
            "link": aff_link,
            "source": "Flipkart",
            "pid": link.split("/p/")[-1][:16] if "/p/" in link else "",
        })
    
    return deals

def extract_amazon_deals(content):
    """Extract products from Amazon search results."""
    deals = []
    seen = set()
    
    for m in re.finditer(r'class="a-price-whole"[^>]*>([\d,]+)', content):
        try:
            price = int(m.group(1).replace(',', ''))
        except:
            continue
        
        # Get larger context window
        before = content[max(0,m.start()-2000):m.start()]
        after = content[m.end():m.end()+300]
        ctx = before + after
        
        link_m = re.search(r'href="(/[^\s"]*dp/[A-Z0-9]{10}[^\s"]*)', before)
        
        if not link_m:
            continue
        
        raw_link = link_m.group(1)
        base = raw_link.split("?")[0]
        if base in seen:
            continue
        seen.add(base)
        
        # Try to find better title from alt text or nearby span
        title_m = re.search(r'alt="([^"]{20,150})"', before)
        if not title_m:
            title_m = re.search(r'class="[^"]*a-size-medium[^"]*"[^>]*>([^<]{20,150})<', before)
        if not title_m:
            title_m = re.search(r'class="[^"]*a-text-normal[^"]*"[^>]*>([^<]{20,150})<', before)
        
        if title_m:
            title = title_m.group(1).strip()
        else:
            # Fallback to URL path
            title_path = base.split("/dp/")[0].lstrip("/")
            title = title_path.replace("-", " ").replace("_", " ")
            title = re.sub(r"\s+", " ", title).strip()
        
        if price < 500 or len(title) < 15:
            continue
        
        # Extract brand from title for better scoring
        full_link = f"https://www.amazon.in{base}"
        aff_link = add_affiliate(full_link)
        if not aff_link:
            continue
        
        deals.append({
            "title": title[:60],
            "price": price,
            "mrp": None,
            "discount": 0,
            "link": aff_link,
            "source": "Amazon",
            "asin": base.split("/dp/")[1][:10] if "/dp/" in base else "",
        })
    
    return deals

def scrape_amazon(queries):
    """Search Amazon and extract products."""
    deals = []
    print("  [Amazon] ", end="", flush=True)
    
    for q, price_limit in queries:
        url = f"https://www.amazon.in/s?k={urllib.parse.quote(q)}&s=price-asc-rank"
        c = curl(url, timeout=10, use_amazon_headers=True)
        if c:
            products = extract_amazon_deals(c)
            deals.extend(products[:5])
    
    print(f"found {len(deals)}", flush=True)
    return deals

def fetch_product_price(product_link):
    """Visit individual product page to extract price. Converts 3x better."""
    c = curl(product_link, timeout=8)
    if not c:
        return 0, None, 0
    
    # Try multiple price patterns
    # Pattern 1: JSON-LD
    price_m = re.search(r'"price"\s*:\s*"?(\d+)"?', c)
    mrp_m = re.search(r'"mrp"\s*:\s*"?(\d+)"?', c)
    
    if price_m:
        price = int(price_m.group(1))
        mrp = int(mrp_m.group(1)) if mrp_m else None
        discount = 0
        if mrp and mrp > price:
            discount = int(((mrp - price) / mrp) * 100)
        return price, mrp, discount
    
    # Pattern 2: HTML price spans
    price_m = re.search(r'class="[^"]*price[^"]*"[^>]*>₹?\s*([\d,]+)', c)
    mrp_m = re.search(r'class="[^"]*mrp[^"]*"[^>]*>₹?\s*([\d,]+)', c)
    if price_m:
        price = int(price_m.group(1).replace(',', ''))
        mrp = int(mrp_m.group(1).replace(',', '')) if mrp_m else None
        discount = 0
        if mrp and mrp > price:
            discount = int(((mrp - price) / mrp) * 100)
        return price, mrp, discount
    
    return 0, None, 0

def scrape_flipkart(queries):
    """Search Flipkart and extract products. Fast + price enrichment for top deals."""
    deals = []
    print("  [Flipkart] ", end="", flush=True)
    
    for q, price_limit in queries:
        url = f"https://www.flipkart.com/search?q={urllib.parse.quote(q)}&sort=_discount"
        c = curl(url)
        if c:
            products = extract_flipkart_products(c, price_limit)
            deals.extend(products[:4])
    
    # Enrich top deals with prices (visit product pages)
    print(f"found {len(deals)}, enriching prices...", end="", flush=True)
    for d in deals[:6]:  # Only enrich top 6 (to save time)
        price, mrp, discount = fetch_product_price(d["link"])
        d["price"] = price
        d["mrp"] = mrp
        d["discount"] = discount
        time.sleep(0.3)
    
    print(f" done")
    return deals

def clean_title(title):
    title = re.sub(r'\s*[-–|].*?(?:DesiDime|Deal|Loot|Coupon|Offer|Buy).*', '', title, flags=re.IGNORECASE)
    return re.sub(r'\s+', ' ', title).strip()[:60]

def score_deal(d):
    """Score deals by conversion potential and traffic-driving value."""
    score = 0
    p = d.get("price", 0)
    mrp = d.get("mrp", 0)
    discount = d.get("discount", 0)
    savings = mrp - p if mrp and p else 0
    title = d.get("title", "").lower()
    source = d.get("source", "")

    # HIGH-VALUE CATEGORIES (traffic drivers)
    if any(x in title for x in ["mobile", "phone", "smartphone", "5g"]):
        score += 40
    elif any(x in title for x in ["laptop", "notebook", "macbook"]):
        score += 50
    elif any(x in title for x in ["tv", "television", "led tv"]):
        score += 45
    elif any(x in title for x in ["ac ", "air conditioner", "refrigerator", "fridge"]):
        score += 40
    elif any(x in title for x in ["earbud", "earphone", "headphone", "neckband"]):
        score += 30
    elif any(x in title for x in ["smartwatch", "watch", "fitness band"]):
        score += 25
    elif any(x in title for x in ["camera", "dslr", "mirrorless"]):
        score += 35
    elif any(x in title for x in ["speaker", "jbl", "boAt", "sony"]):
        score += 25
    elif any(x in title for x in ["tablet", "ipad", "pad"]):
        score += 30
    elif any(x in title for x in ["shoe", "watch", "bag", "shirt", "tshirt"]):
        score += 15

    # DISCOUNT THRESHOLDS (critical for click-through)
    if discount >= 70:
        score += 60  # MEGA deal - drives huge traffic
    elif discount >= 60:
        score += 50
    elif discount >= 50:
        score += 40  # GOOD deal
    elif discount >= 40:
        score += 25
    elif discount >= 30:
        score += 15
    elif discount >= 20:
        score += 5
    elif discount == 0 and source == "Amazon":
        score += 10  # Amazon doesn't show MRP easily, don't penalize

    # ABSOLUTE SAVINGS (people love big rupee amounts saved)
    if savings >= 10000:
        score += 50  # Massive savings
    elif savings >= 5000:
        score += 40
    elif savings >= 3000:
        score += 30
    elif savings >= 1500:
        score += 20
    elif savings >= 500:
        score += 10

    # PRICE SWEET SPOTS (impulse buy ranges)
    if 199 <= p <= 999:
        score += 35  # No-brainer purchases
    elif 999 <= p <= 2999:
        score += 30  # Easy decisions
    elif 2999 <= p <= 9999:
        score += 25  # Considered but popular
    elif 9999 <= p <= 19999:
        score += 20  # Mobile sweet spot
    elif 19999 <= p <= 39999:
        score += 15
    elif p > 50000:
        score -= 10  # Too expensive for impulse

    # BRAND BOOSTERS (recognized names = higher CTR)
    if any(x in title for x in ["samsung", "iphone", "apple", "oneplus", "xiaomi", "redmi", "poco", "realme", "oppo", "vivo"]):
        score += 20
    elif any(x in title for x in ["sony", "lg", "whirlpool", "hp", "dell", "lenovo", "asus", "acer"]):
        score += 15
    elif any(x in title for x in ["boat", "jbl", "noise", "realme", "mi"]):
        score += 10

    # FILTER OUT LOW-VALUE
    if discount < 15 and discount > 0:
        score -= 50  # Skip small discounts (but not 0 = unknown)
    if p == 0:
        score -= 30  # Unknown price = less engagement
    if "accessory" in title or "cover" in title or "case" in title:
        score -= 20  # Low-ticket items don't drive traffic

    return score


MIN_SCORE_THRESHOLD = 45

def format_price(price):
    if price == 0:
        return ""
    return f"₹{price:,}"

def get_twitter_client():
    with open(TWITTER_CREDENTIALS) as f:
        config = json.load(f)
    return tweepy.Client(
        consumer_key=config["api_key"],
        consumer_secret=config["api_secret"],
        access_token=config["access_token"],
        access_token_secret=config["access_token_secret"],
        bearer_token=config["bearer_token"]
    )

def format_tweet(d):
    tweet = (
        f"🔥 {d['title']}\n"
        f"💰 ₹{d['price']:,}"
        + (f" <s>₹{d['mrp']:,}</s>" if d.get('mrp') and d['mrp'] > d['price'] else "")
        + (f" 🏷️ -{d['discount']}% OFF" if d.get('discount', 0) > 0 else "")
        + (f"  (Save ₹{d['mrp'] - d['price']:,}!)" if d.get('mrp') and d['mrp'] - d['price'] > 1000 else "")
        + f"\n\n🛒 {d['link']}"
        + f"\n\n📲 More deals: {CHANNEL_JOIN}"
    )
    if len(tweet) > 280:
        d['title'] = d['title'][:30] + "..."
        tweet = (
            f"🔥 {d['title'][:35]}\n"
            f"₹{d['price']:,}"
            + (f" (-{d['discount']}%)" if d.get('discount', 0) > 0 else "")
            + f"\n\n🛒 {d['link']}"
            + f"\n\n📲 {CHANNEL_JOIN}"
        )
        if len(tweet) > 280:
            tweet = tweet[:277] + "..."
    return tweet

def get_deals(history):
    posted = set(history.get("posted", []))
    
    if CLOUD_MODE:
        print("  ☁️ Cloud mode: reading from deal pool")
        if os.path.exists(POOL_FILE):
            with open(POOL_FILE) as f:
                pool = json.load(f)
            deals = pool.get("deals", [])
            print(f"  Pool has {len(deals)} deals available")
            return [d for d in deals if d["link"].split("?")[0] not in posted]
        print("  No pool file found")
        return []
    
    # Local mode: scrape fresh deals
    queries = get_query_set()
    all_deals = []
    all_deals.extend(scrape_flipkart(queries))
    all_deals.extend(scrape_amazon(queries))

    seen = set()
    unique = []
    for d in all_deals:
        if not has_affiliate(d["link"]):
            continue
        base = d["link"].split("?")[0]
        if base in posted:
            continue
        seen.add(base)
        d["title"] = clean_title(d["title"])
        if d["title"]:
            unique.append(d)

    unique.sort(key=score_deal, reverse=True)
    top_deals = [d for d in unique if score_deal(d) >= MIN_SCORE_THRESHOLD]
    top_deals = top_deals[:MAX_DEALS * 2]
    
    print(f"\n📊 {len(unique)} total | 🏆 {len(top_deals)} high-value (score≥{MIN_SCORE_THRESHOLD})")
    for i, d in enumerate(top_deals[:8]):
        s = score_deal(d)
        print(f"  #{i+1} Score:{s:3d} | {d['source']:8s} | ₹{d['price']:,} | -{d['discount']}% | {d['title'][:40]}")
    
    # Save ALL scraped deals to pool for future cloud runs
    if top_deals:
        with open(POOL_FILE, "w") as f:
            json.dump({"deals": top_deals, "generated_at": datetime.now().isoformat()}, f, indent=2)
        print(f"  Saved {len(top_deals)} deals to pool, returning {MAX_DEALS} for immediate posting")
    
    return top_deals[:MAX_DEALS]

def save_pool(deals):
    with open(POOL_FILE, "w") as f:
        json.dump({"deals": deals, "generated_at": datetime.now().isoformat()}, f, indent=2)

def main():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔥 EXPERT AFFILIATE v3")
    token = load_config()
    history = load_history()
    
    top_deals = get_deals(history)
    if not top_deals:
        print("No deals to post. Waiting for better deals..." if not CLOUD_MODE else "Pool empty. Run scraper on device to refill.")
        return

    now = datetime.now().strftime("%b %d, %I:%M %p")
    new_posted = []

    for i in range(0, len(top_deals), MAX_DEALS):
        batch = top_deals[i:i+MAX_DEALS]
        
        # Cinematic header
        text = f"{get_header(now)}\n\n"
        
        for d in batch:
            icon = "🟠" if d["source"] == "Amazon" else "🔵"
            title = d["title"]
            price = d["price"]
            mrp = d["mrp"]
            discount = d["discount"]
            savings = mrp - price if mrp and mrp > price else 0
            link = d["link"]
            
            # Price line with inline clickable link
            price_line = ""
            if price > 0:
                price_line = f"  💰 <b>₹{price:,}</b>"
                if mrp and mrp > price:
                    price_line += f"  <s>₹{mrp:,}</s>"
                    price_line += f"\n  🏷️ <b>-{discount}% OFF</b>"
                    if savings >= 1000:
                        price_line += f"  (Save ₹{savings:,}!)"
                # Inline link after price
                buy_text = "Buy on Amazon" if d["source"] == "Amazon" else "Buy on Flipkart"
                price_line += f'\n  <a href="{link}">👆 {buy_text}</a>'
            
            text += f"{icon} {title}\n{price_line}\n\n"
        
        # Urgency line
        text += f"{get_urgency()}\n\n"
        
        # Promotional message
        promo = get_promo()
        text += f"{promo['header']}\n{promo['body']}\n\n"
        
        # Footer with share + subscribe CTA
        text += get_footer()

        # Buttons
        buttons = []
        for d in batch:
            icon = "🛒" if d["source"] == "Amazon" else "🛍️"
            price_tag = f" {format_price(d['price'])}" if d["price"] > 0 else ""
            short = d["title"][:18] + "..." if len(d["title"]) > 18 else d["title"]
            btn_text = f"{icon}{price_tag} {short}"
            buttons.append((btn_text, d["link"]))
        
        # Add subscribe/share buttons at end
        share_url = urllib.parse.quote(CHANNEL_JOIN, safe="")
        share_text = urllib.parse.quote(f"🔥 Best Flipkart & Amazon Deals — Updated every 15 mins! Join {CHANNEL_NAME} now!", safe="")
        buttons.append(("✅ Join Channel", CHANNEL_JOIN))
        buttons.append(("📤 Share Deals", f"https://t.me/share/url?url={share_url}&text={share_text}"))

        if post_with_buttons(token, text, buttons):
            for d in batch:
                new_posted.append(d["link"].split("?")[0])
            time.sleep(2)

    if new_posted:
        history["posted"] = list(set(history.get("posted", []) + new_posted))[-2000:]
        history["last"] = datetime.now().isoformat()
        save_history(history)
        # Remove posted deals from pool
        posted_bases = set(new_posted)
        remaining = [d for d in top_deals if d["link"].split("?")[0] not in posted_bases]
        if CLOUD_MODE:
            save_pool(remaining)
            print(f"  Removed posted deals, {len(remaining)} left in pool")
        print(f"\n💰 Posted {len(new_posted)} deals with affiliate tracking!")

if __name__ == "__main__":
    main()
