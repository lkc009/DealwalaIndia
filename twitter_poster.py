#!/usr/bin/env python3
"""
DealwalaIndia - Twitter/X Auto-Poster
Posts deals from Flipkart & Amazon to your Twitter/X account.
Uses Twitter API v2 (Free tier - 1,500 posts/month).
"""

import json
import os
import re
import random
import subprocess
import time
import urllib.parse
import tweepy
from datetime import datetime

TWITTER_CREDENTIALS = os.path.expanduser("~/.codex/twitter_dealwala.json")
DEALS_HISTORY = os.path.expanduser("~/.codex/dealwalaindia_history.json")

AFFILIATE_ID = "lalitkcho"
AMAZON_TAG = "123450005-21"

CHANNEL_LINK = "https://t.me/dealwalaindiain"

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

def load_twitter_config():
    with open(TWITTER_CREDENTIALS) as f:
        return json.load(f)

def get_twitter_client():
    config = load_twitter_config()
    return tweepy.Client(
        consumer_key=config["api_key"],
        consumer_secret=config["api_secret"],
        access_token=config["access_token"],
        access_token_secret=config["access_token_secret"],
        bearer_token=config["bearer_token"]
    )

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

def extract_flipkart_products(content, price_limit=None):
    deals = []
    seen = set()
    
    for m in re.finditer(r'(https?://[^\s"\'<>]*flipkart\.com/[^\s"\'<>]+/p/[^\s"\'<>]+)', content):
        link = m.group(1).split('"')[0].split("'")[0].split('>')[0]
        if link in seen:
            continue
        seen.add(link)
        
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
        })
    
    return deals

def extract_amazon_deals(content):
    deals = []
    seen = set()
    
    for m in re.finditer(r'class="a-price-whole"[^>]*>([\d,]+)', content):
        try:
            price = int(m.group(1).replace(',', ''))
        except:
            continue
        
        before = content[max(0,m.start()-2000):m.start()]
        link_m = re.search(r'href="(/[^\s"]*dp/[A-Z0-9]{10}[^\s"]*)', before)
        
        if not link_m:
            continue
        
        raw_link = link_m.group(1)
        base = raw_link.split("?")[0]
        if base in seen:
            continue
        seen.add(base)
        
        title_m = re.search(r'alt="([^"]{20,150})"', before)
        if not title_m:
            title_m = re.search(r'class="[^"]*a-size-medium[^"]*"[^>]*>([^<]{20,150})<', before)
        if not title_m:
            title_m = re.search(r'class="[^"]*a-text-normal[^"]*"[^>]*>([^<]{20,150})<', before)
        
        if title_m:
            title = title_m.group(1).strip()
        else:
            title_path = base.split("/dp/")[0].lstrip("/")
            title = title_path.replace("-", " ").replace("_", " ")
            title = re.sub(r"\s+", " ", title).strip()
        
        if price < 500 or len(title) < 15:
            continue
        
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
        })
    
    return deals

def fetch_product_price(product_link):
    c = curl(product_link, timeout=8)
    if not c:
        return 0, None, 0
    
    price_m = re.search(r'"price"\s*:\s*"?(\d+)"?', c)
    mrp_m = re.search(r'"mrp"\s*:\s*"?(\d+)"?', c)
    
    if price_m:
        price = int(price_m.group(1))
        mrp = int(mrp_m.group(1)) if mrp_m else None
        discount = 0
        if mrp and mrp > price:
            discount = int(((mrp - price) / mrp) * 100)
        return price, mrp, discount
    
    return 0, None, 0

def scrape_deals(queries):
    deals = []
    print("  [Flipkart] ", end="", flush=True)
    
    for q, price_limit in queries:
        url = f"https://www.flipkart.com/search?q={urllib.parse.quote(q)}&sort=_discount"
        c = curl(url)
        if c:
            products = extract_flipkart_products(c, price_limit)
            deals.extend(products[:4])
    
    print(f"found {len(deals)}, enriching...", end="", flush=True)
    for d in deals[:6]:
        price, mrp, discount = fetch_product_price(d["link"])
        d["price"] = price
        d["mrp"] = mrp
        d["discount"] = discount
        time.sleep(0.3)
    print(" done")
    
    print("  [Amazon] ", end="", flush=True)
    for q, price_limit in queries:
        url = f"https://www.amazon.in/s?k={urllib.parse.quote(q)}&s=price-asc-rank"
        c = curl(url, timeout=10, use_amazon_headers=True)
        if c:
            products = extract_amazon_deals(c)
            deals.extend(products[:5])
    print(f"found total {len(deals)}")
    
    return deals

def clean_title(title):
    title = re.sub(r'\s*[-–|].*?(?:DesiDime|Deal|Loot|Coupon|Offer|Buy).*', '', title, flags=re.IGNORECASE)
    return re.sub(r'\s+', ' ', title).strip()[:60]

def score_deal(d):
    score = 0
    p = d.get("price", 0)
    mrp = d.get("mrp", 0)
    discount = d.get("discount", 0)
    savings = mrp - p if mrp and p else 0
    title = d.get("title", "").lower()
    source = d.get("source", "")

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

    if discount >= 70:
        score += 60
    elif discount >= 60:
        score += 50
    elif discount >= 50:
        score += 40
    elif discount >= 40:
        score += 25
    elif discount >= 30:
        score += 15
    elif discount >= 20:
        score += 5
    elif discount == 0 and source == "Amazon":
        score += 10

    if savings >= 10000:
        score += 50
    elif savings >= 5000:
        score += 40
    elif savings >= 3000:
        score += 30
    elif savings >= 1500:
        score += 20
    elif savings >= 500:
        score += 10

    if 199 <= p <= 999:
        score += 35
    elif 999 <= p <= 2999:
        score += 30
    elif 2999 <= p <= 9999:
        score += 25
    elif 9999 <= p <= 19999:
        score += 20
    elif 19999 <= p <= 39999:
        score += 15
    elif p > 50000:
        score -= 10

    if any(x in title for x in ["samsung", "iphone", "apple", "oneplus", "xiaomi", "redmi", "poco", "realme", "oppo", "vivo"]):
        score += 20
    elif any(x in title for x in ["sony", "lg", "whirlpool", "hp", "dell", "lenovo", "asus", "acer"]):
        score += 15
    elif any(x in title for x in ["boat", "jbl", "noise", "realme", "mi"]):
        score += 10

    if discount < 15 and discount > 0:
        score -= 50
    if p == 0:
        score -= 30
    if "accessory" in title or "cover" in title or "case" in title:
        score -= 20

    return score

MIN_SCORE_THRESHOLD = 45

TWEET_TEMPLATES = [
    # Single deal tweet
    lambda d: (
        f"🔥 {d['title']}\n"
        f"💰 ₹{d['price']:,}"
        + (f" <s>₹{d['mrp']:,}</s>" if d.get('mrp') and d['mrp'] > d['price'] else "")
        + (f"\n🏷️ -{d['discount']}% OFF" if d.get('discount', 0) > 0 else "")
        + (f"  (Save ₹{d['mrp'] - d['price']:,}!)" if d.get('mrp') and d['mrp'] - d['price'] > 1000 else "")
        + f"\n\n🛒 Buy: {d['link']}"
        + f"\n\n📲 More deals: {CHANNEL_LINK}"
    ),
    # Deal with hook
    lambda d: (
        f"💥 DEAL ALERT!\n\n"
        f"{d['title']}\n"
        + (f"₹{d['mrp']:,} → ₹{d['price']:,}" if d.get('mrp') and d['mrp'] > d['price'] else f"₹{d['price']:,}")
        + (f"\n🔥 -{d['discount']}% OFF!" if d.get('discount', 0) > 0 else "")
        + (f"\n💸 You save ₹{d['mrp'] - d['price']:,}!" if d.get('mrp') and d['mrp'] - d['price'] > 1000 else "")
        + f"\n\n👉 {d['link']}"
        + f"\n\n📲 Join for daily deals: {CHANNEL_LINK}"
    ),
    # Short + punchy
    lambda d: (
        f"📱 {d['title']}\n"
        f"₹{d['price']:,}"
        + (f" (-{d['discount']}%)" if d.get('discount', 0) > 0 else "")
        + f"\n\n🛒 {d['link']}"
        + f"\n\n🔔 Follow + Join: {CHANNEL_LINK}"
    ),
]

def format_tweet(d):
    template = random.choice(TWEET_TEMPLATES)
    tweet = template(d)
    
    # Twitter limit is 280 chars
    if len(tweet) > 280:
        # Truncate title
        d['title'] = d['title'][:30] + "..."
        tweet = template(d)
        if len(tweet) > 280:
            # Shortest version
            tweet = (
                f"🔥 {d['title'][:35]}\n"
                f"₹{d['price']:,}"
                + (f" (-{d['discount']}%)" if d.get('discount', 0) > 0 else "")
                + f"\n\n🛒 {d['link']}"
                + f"\n\n📲 {CHANNEL_LINK}"
            )
            if len(tweet) > 280:
                tweet = tweet[:277] + "..."
    
    return tweet

def load_posted_tweets():
    if os.path.exists(DEALS_HISTORY):
        with open(DEALS_HISTORY) as f:
            h = json.load(f)
        return set(h.get("tweets", []))
    return set()

def save_tweet_history(link):
    if os.path.exists(DEALS_HISTORY):
        with open(DEALS_HISTORY) as f:
            h = json.load(f)
    else:
        h = {"posted": [], "tweets": [], "last": None}
    
    h["tweets"] = list(set(h.get("tweets", []) + [link]))[-2000:]
    h["last"] = datetime.now().isoformat()
    with open(DEALS_HISTORY, "w") as f:
        json.dump(h, f, indent=2)

def main():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🐦 Twitter Auto-Poster")
    
    try:
        client = get_twitter_client()
        me = client.get_me()
        print(f"✅ Logged in as: @{me.data.username}")
    except Exception as e:
        print(f"❌ Twitter API error: {e}")
        print("\n📋 Setup required:")
        print("1. Go to: https://developer.twitter.com/en/portal/dashboard")
        print("2. Create a Project + App (Free tier)")
        print("3. Generate API keys and access tokens")
        print("4. Save to: ~/.codex/twitter_dealwala.json")
        print("\nFormat:")
        print('{')
        print('  "api_key": "...",')
        print('  "api_secret": "...",')
        print('  "bearer_token": "...",')
        print('  "access_token": "...",')
        print('  "access_token_secret": "..."')
        print('}')
        return
    
    posted_tweets = load_posted_tweets()
    queries = get_query_set()
    
    all_deals = scrape_deals(queries)
    
    seen = set()
    unique = []
    for d in all_deals:
        base = d["link"].split("?")[0]
        if base in posted_tweets:
            continue
        seen.add(base)
        d["title"] = clean_title(d["title"])
        if d["title"]:
            unique.append(d)
    
    unique.sort(key=score_deal, reverse=True)
    top_deals = [d for d in unique if score_deal(d) >= MIN_SCORE_THRESHOLD]
    top_deals = top_deals[:6]
    
    print(f"\n📊 {len(unique)} total | 🏆 {len(top_deals)} tweet-worthy")
    
    if not top_deals:
        print("No tweet-worthy deals found.")
        return
    
    for i, d in enumerate(top_deals[:6]):
        print(f"  #{i+1} Score:{score_deal(d):3d} | {d['source']:8s} | ₹{d['price']:,} | -{d['discount']}% | {d['title'][:40]}")
    
    print("\n📝 Posting tweets...\n")
    posted_count = 0
    
    for d in top_deals[:6]:
        tweet = format_tweet(d)
        
        print(f"Tweet: {tweet[:80]}...")
        print(f"  Length: {len(tweet)} chars")
        
        try:
            response = client.create_tweet(text=tweet)
            tweet_id = response.data['id']
            print(f"  ✅ Posted! Tweet ID: {tweet_id}")
            save_tweet_history(d["link"].split("?")[0])
            posted_count += 1
            time.sleep(5)
        except Exception as e:
            print(f"  ❌ Failed: {e}")
            if "429" in str(e) or "rate" in str(e).lower():
                print("  ⚠️ Rate limited. Stopping.")
                break
    
    print(f"\n📊 Posted {posted_count} tweets to X!")

if __name__ == "__main__":
    main()
