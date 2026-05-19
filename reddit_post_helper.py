#!/usr/bin/env python3
"""
Reddit Post Helper - Opens Reddit submit pages in browser for easy posting.
Just paste the content and click submit!
"""

import asyncio
import webbrowser
import time
from playwright.async_api import async_playwright

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

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        
        print("🚀 Opening Reddit post pages...\n")
        print("Instructions:")
        print("1. Login to Reddit in the first tab")
        print("2. Then close each tab after posting")
        print("3. The script will wait and open the next post\n")
        
        for i, post in enumerate(POSTS):
            print(f"\n{'='*50}")
            print(f"POST {i+1}/{len(POSTS)}: r/{post['subreddit']}")
            print(f"Title: {post['title']}")
            print(f"{'='*50}")
            print(f"\nCopy this body:\n{post['body']}\n")
            
            url = f"https://www.reddit.com/r/{post['subreddit']}/submit"
            print(f"Opening: {url}")
            
            page = await context.new_page()
            await page.goto(url, wait_until="domcontentloaded")
            await asyncio.sleep(1)
            
            # Try to auto-fill title
            try:
                title_el = await page.query_selector('input[name="title"], textarea[name="title"], input[type="text"]')
                if title_el:
                    await title_el.fill(post['title'])
                    print("✅ Title auto-filled!")
            except:
                print("⚠️ Please fill title manually")
            
            # Try to auto-fill body
            try:
                body_el = await page.query_selector('textarea[name="body"], div[contenteditable="true"]')
                if body_el:
                    tag = await body_el.evaluate('el => el.tagName')
                    if tag == 'DIV':
                        await body_el.click()
                        await page.keyboard.type(post['body'], delay=10)
                    else:
                        await body_el.fill(post['body'])
                    print("✅ Body auto-filled!")
            except:
                print("⚠️ Please paste body manually")
            
            print("\n👉 Review and click 'Post' when ready.")
            print("⏳ Waiting for you to finish posting...")
            print("   (Script will continue when you close this tab)")
            
            # Wait for user to close the tab
            while not page.is_closed():
                await asyncio.sleep(1)
            
            print("✅ Tab closed, moving to next post...")
            await asyncio.sleep(2)
        
        print("\n🎉 All posts done!")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
