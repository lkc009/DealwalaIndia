#!/usr/bin/env python3
"""
Reddit Auto-Poster for DealwalaIndia v2
Uses Playwright with CAPTCHA handling and anti-detection.
"""

import asyncio
import json
import random
import os
import time
from playwright.async_api import async_playwright

REDDIT_USERNAME = "LKC520741"
REDDIT_PASSWORD = "lkc@520741781"
SCREENSHOT_DIR = "/root/dealwalaindia/screenshots"

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
    {
        "subreddit": "IndianDankMeme",
        "title": "POV: You buy a phone at MRP while your friend gets it at 40% off",
        "body": """You: *buys phone at ₹15,999*
Friend: *buys same phone at ₹9,999*

You: "WHAT?!"
Friend: "Deal channel pe aaya tha, 15 min mein grab kar liya 😎"

You: "Kaunsa channel??"
Friend: *smiles*

https://t.me/dealwalaindiain

Now YOU be the friend 😏""",
    },
]


async def login_reddit(page):
    print("🔐 Attempting auto-login...")
    
    try:
        # Check if already logged in
        try:
            user_btn = await page.query_selector('div[data-testid="user-menu-button"]')
            if user_btn:
                name = await user_btn.inner_text()
                if name and name.strip():
                    print(f"✅ Already logged in: {name.strip()}")
                    return True
        except:
            pass
        
        # Go to login
        await page.goto("https://www.reddit.com/login", wait_until="domcontentloaded")
        await asyncio.sleep(2)
        
        # Fill username
        username_field = await page.query_selector('input[name="username"]')
        if not username_field:
            username_field = await page.query_selector('input[type="text"]')
        if username_field:
            await username_field.click()
            await asyncio.sleep(0.5)
            await username_field.fill(REDDIT_USERNAME)
            print("   ✅ Username filled")
        
        await asyncio.sleep(1)
        
        # Fill password
        password_field = await page.query_selector('input[name="password"]')
        if not password_field:
            password_field = await page.query_selector('input[type="password"]')
        if password_field:
            await password_field.click()
            await asyncio.sleep(0.5)
            await password_field.fill(REDDIT_PASSWORD)
            print("   ✅ Password filled")
        
        await asyncio.sleep(1)
        
        # Click login
        login_btn = await page.query_selector('button:has-text("Log In")')
        if not login_btn:
            buttons = await page.query_selector_all('button')
            for btn in buttons:
                text = await btn.inner_text()
                if "Log In" in text or "Log in" in text:
                    login_btn = btn
                    break
        
        if login_btn:
            await login_btn.click()
            print("   📤 Login submitted...")
        else:
            await page.keyboard.press("Enter")
            print("   📤 Pressed Enter to login...")
        
        await asyncio.sleep(5)
        
        # Check for CAPTCHA - take screenshot
        await asyncio.sleep(2)
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        await page.screenshot(path=f"{SCREENSHOT_DIR}/after_login.png")
        print(f"   📸 Screenshot saved: {SCREENSHOT_DIR}/after_login.png")
        
        # Check if logged in
        try:
            user_btn = await page.query_selector('div[data-testid="user-menu-button"]')
            if user_btn:
                name = await user_btn.inner_text()
                if name and name.strip():
                    print(f"✅ Logged in: {name.strip()}")
                    return True
        except:
            pass
        
        # Wait for manual CAPTCHA solving
        print("   🔐 If CAPTCHA appeared, please solve it in the browser window...")
        print("   ⏳ Waiting up to 180 seconds...")
        
        for i in range(180):
            try:
                user_btn = await page.query_selector('div[data-testid="user-menu-button"]')
                if user_btn:
                    name = await user_btn.inner_text()
                    if name and name.strip():
                        print(f"✅ Login complete: {name.strip()}")
                        await page.screenshot(path=f"{SCREENSHOT_DIR}/logged_in.png")
                        return True
            except:
                pass
            if i % 15 == 0:
                print(f"   Still waiting... ({i}s)")
            await asyncio.sleep(1)
        
        print("❌ Login timeout!")
        return False
        
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        return False


async def post_to_reddit(page, post, index):
    sub = post["subreddit"]
    title = post["title"]
    body = post["body"]
    
    print(f"\n📝 [{index+1}] Posting to r/{sub}...")
    
    try:
        url = f"https://www.reddit.com/r/{sub}/submit"
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(3)
        
        # Take screenshot of submit page
        await page.screenshot(path=f"{SCREENSHOT_DIR}/submit_{sub}.png")
        
        # Find and fill title
        title_filled = False
        title_selectors = [
            'input[name="title"]',
            'textarea[name="title"]',
            'input[type="text"][placeholder*="title" i]',
            'input[type="text"]',
        ]
        
        for sel in title_selectors:
            try:
                el = await page.query_selector(sel)
                if el:
                    await el.click()
                    await asyncio.sleep(0.5)
                    await el.fill(title)
                    title_filled = True
                    print(f"   ✅ Title filled")
                    break
            except:
                continue
        
        if not title_filled:
            print("   ❌ Could not find title field")
            return False
        
        await asyncio.sleep(1)
        
        # Find and fill body
        body_filled = False
        body_selectors = [
            'textarea[name="body"]',
            'div[contenteditable="true"]',
            'div[role="textbox"]',
            'textarea[placeholder*="body" i]',
            'textarea',
        ]
        
        for sel in body_selectors:
            try:
                el = await page.query_selector(sel)
                if el:
                    tag = await el.evaluate('el => el.tagName')
                    if tag == 'DIV':
                        await el.click()
                        await asyncio.sleep(0.5)
                        await page.keyboard.type(body, delay=15)
                    else:
                        await el.click()
                        await asyncio.sleep(0.5)
                        await el.fill(body)
                    body_filled = True
                    print(f"   ✅ Body filled ({len(body)} chars)")
                    break
            except:
                continue
        
        await asyncio.sleep(2)
        
        # Take screenshot before submit
        await page.screenshot(path=f"{SCREENSHOT_DIR}/before_submit_{sub}.png")
        
        # Find and click submit
        submit_selectors = [
            'button[type="submit"]',
            'button:has-text("Post")',
            'button:has-text("Submit")',
            'button:has-text("submit")',
        ]
        
        for sel in submit_selectors:
            try:
                btn = await page.query_selector(sel)
                if btn:
                    await btn.click()
                    print(f"   🚀 Submitted to r/{sub}!")
                    await asyncio.sleep(5)
                    await page.screenshot(path=f"{SCREENSHOT_DIR}/after_submit_{sub}.png")
                    return True
            except:
                continue
        
        print("   ⚠️ Could not find submit button. Check screenshot.")
        return False
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


async def main():
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-web-security',
            ]
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="en-US",
        )
        
        # Anti-detection scripts
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            window.chrome = { runtime: {} };
            navigator.plugins.length = 5;
        """)
        
        page = await context.new_page()
        
        print("🌐 Opening Reddit...")
        await page.goto("https://www.reddit.com", wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(2)
        
        logged_in = await login_reddit(page)
        
        if not logged_in:
            print("❌ Not logged in. Exiting.")
            await browser.close()
            return
        
        print("\n🚀 Starting automated posting...\n")
        
        results = []
        for i, post in enumerate(POSTS):
            success = await post_to_reddit(page, post, i)
            results.append({"post": post["subreddit"], "success": success})
            
            if success:
                print(f"   ✅ Post {i+1} SUCCESS!")
            else:
                print(f"   ❌ Post {i+1} FAILED")
            
            if i < len(POSTS) - 1:
                wait_time = random.randint(30, 60)
                print(f"   ⏳ Waiting {wait_time}s before next post...")
                await asyncio.sleep(wait_time)
        
        print("\n📊 Results:")
        for r in results:
            status = "✅" if r["success"] else "❌"
            print(f"  {status} r/{r['post']}")
        
        print(f"\n📸 Screenshots saved to: {SCREENSHOT_DIR}/")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
