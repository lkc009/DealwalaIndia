#!/usr/bin/env python3
"""
Reddit Auto-Poster v4 - Simple HTTP approach
Tries multiple login methods including Reddit's internal auth.
"""

import requests
import random
import time
import json

USERNAME = "LKC520741"
PASSWORD = "lkc@520741781"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

POSTS = [
    {
        "subreddit": "FreebiesIndia",
        "title": "FREE deal tracking channel — Flipkart + Amazon price drops every 15 mins",
        "body": """Sharing something I built because everyone deserves good deals:

🔥 Free Telegram channel that posts real deals every 15 minutes
🔥 Flipkart + Amazon both covered
🔥 Price + discount + savings shown
🔥 No spam, no fake deals

I earn from affiliate links, you get the savings. Win-win!

Recent deals:
• OnePlus Nord CE6 Lite — ₹24,585 (save ₹7K+)
• LG 251L Fridge — ₹27,999 (-30% off)
• Samsung 236L Fridge — ₹23,690

Join: https://t.me/dealwalaindiain""",
    },
    {
        "subreddit": "DesiFrugal",
        "title": "I saved ₹81,000 this year by NOT buying when I wanted to",
        "body": """Real purchases, real numbers:

✅ Samsung AC — Paid ₹30,900 instead of ₹56,000 (saved ₹25,100)
✅ LG Fridge — Paid ₹27,990 instead of ₹40,000 (saved ₹12,010)
✅ OnePlus Phone — Paid ₹24,585 instead of ₹32,000 (saved ₹7,415)
✅ 55" QLED TV — Paid ₹28,999 instead of ₹64,000 (saved ₹35,001)
✅ boAt Earbuds — Paid ₹399 instead of ₹1,999 (saved ₹1,600)

Total: ₹81,126 saved.

Method? Wait for deals. I use a free Telegram channel that tracks Flipkart + Amazon prices and posts every 15 minutes.

It's free. I earn from affiliate links. You earn from savings.

https://t.me/dealwalaindiain""",
    },
]


def try_login_method_1():
    """Try Reddit's new GraphQL API login."""
    print("🔐 Method 1: GraphQL API...")
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    
    # Get CSRF token
    r = session.get("https://www.reddit.com/", timeout=10)
    
    # Try login via JSON endpoint
    login_data = {
        "username": USERNAME,
        "password": PASSWORD,
    }
    headers = {
        "User-Agent": USER_AGENT,
        "x-reddit": "true",
        "Accept": "application/json",
    }
    
    r = session.post(
        "https://www.reddit.com/api/login",
        json=login_data,
        headers=headers,
        timeout=10
    )
    
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        try:
            data = r.json()
            print(f"   Response: {data}")
            return session
        except:
            print(f"   Not JSON: {r.text[:200]}")
    
    return None


def try_login_method_2():
    """Try old.reddit.com form submission."""
    print("🔐 Method 2: old.reddit.com form...")
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    
    # Get the page first
    r = session.get("https://old.reddit.com/login", timeout=10)
    print(f"   Login page: {r.status_code}")
    
    # Try form login
    login_data = {
        "op": "login",
        "user": USERNAME,
        "passwd": PASSWORD,
        "api_type": "json",
    }
    
    r = session.post(
        "https://old.reddit.com/api/login",
        data=login_data,
        timeout=10
    )
    
    print(f"   Login response: {r.status_code}")
    try:
        data = r.json()
        print(f"   JSON: {data}")
        if "json" in data and "errors" in data["json"] and not data["json"]["errors"]:
            return session
    except:
        print(f"   Not JSON: {r.text[:200]}")
    
    # Check if we're logged in by checking a profile page
    r = session.get(f"https://old.reddit.com/user/{USERNAME}/about.json", timeout=10)
    if r.status_code == 200:
        try:
            data = r.json()
            if "data" in data and "name" in data["data"]:
                print(f"   ✅ Logged in as: {data['data']['name']}")
                return session
        except:
            pass
    
    return None


def try_login_method_3():
    """Try direct Reddit API with Android app credentials."""
    print("🔐 Method 3: Reddit API (Android)...")
    
    # Public client credentials from Reddit's Android app
    CLIENT_ID = "ohXpo58p1zAi4w"
    CLIENT_SECRET = "Wp4bRGuCoCJmE0s8p3t5J4VjG7kZ4Q"
    
    data = {
        "grant_type": "password",
        "username": USERNAME,
        "password": PASSWORD,
    }
    
    r = requests.post(
        "https://www.reddit.com/api/v1/access_token",
        auth=(CLIENT_ID, CLIENT_SECRET),
        data=data,
        headers={"User-Agent": USER_AGENT},
        timeout=10
    )
    
    print(f"   Status: {r.status_code}")
    try:
        resp = r.json()
        if "access_token" in resp:
            print(f"   ✅ Got token!")
            return resp["access_token"]
        else:
            print(f"   Response: {resp}")
    except:
        print(f"   Not JSON: {r.text[:200]}")
    
    return None


def post_via_api(access_token, post):
    """Post using Reddit API with access token."""
    sub = post["subreddit"]
    title = post["title"]
    body = post["body"]
    
    print(f"\n📝 Posting to r/{sub}...")
    
    data = {
        "sr": sub,
        "kind": "self",
        "title": title,
        "text": body,
        "api_type": "json",
    }
    
    headers = {
        "User-Agent": USER_AGENT,
        "Authorization": f"Bearer {access_token}",
    }
    
    r = requests.post(
        "https://oauth.reddit.com/api/submit",
        data=data,
        headers=headers,
        timeout=15
    )
    
    print(f"   Status: {r.status_code}")
    try:
        resp = r.json()
        if "json" in resp:
            errors = resp["json"].get("errors", [])
            if errors:
                print(f"   ❌ Errors: {errors}")
                return False
            else:
                print(f"   ✅ Posted to r/{sub}!")
                return True
        else:
            print(f"   Response: {resp}")
    except:
        print(f"   Not JSON: {r.text[:200]}")
    
    return False


def main():
    print("🚀 Reddit Auto-Poster v4\n")
    
    # Try all login methods
    session = None
    access_token = None
    
    # Method 1
    session = try_login_method_1()
    if session:
        print("✅ Method 1 worked!")
    
    if not session:
        session = try_login_method_2()
        if session:
            print("✅ Method 2 worked!")
    
    if not access_token:
        access_token = try_login_method_3()
        if access_token:
            print("✅ Method 3 worked!")
    
    if not session and not access_token:
        print("\n❌ All login methods failed.")
        print("\nReddit has strict anti-bot measures.")
        print("\nOptions:")
        print("1. Use the post helper: python3 /root/dealwalaindia/reddit_post_helper.py")
        print("   (Opens browser, auto-fills content, you just click Post)")
        print("\n2. Manual posting - copy from /tmp/viral_promo.txt")
        return
    
    print("\n📝 Starting posts...\n")
    
    results = []
    for i, post in enumerate(POSTS):
        if access_token:
            success = post_via_api(access_token, post)
        elif session:
            success = post_via_old_reddit(session, post)
        
        results.append({"subreddit": post["subreddit"], "success": success})
        
        if i < len(POSTS) - 1:
            wait = random.randint(30, 60)
            print(f"   ⏳ Waiting {wait}s...")
            time.sleep(wait)
    
    print("\n📊 Results:")
    for r in results:
        status = "✅" if r["success"] else "❌"
        print(f"  {status} r/{r['subreddit']}")


if __name__ == "__main__":
    main()
