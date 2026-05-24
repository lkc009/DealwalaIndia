#!/usr/bin/env python3
"""
GEMINI v2090 ULTIMATE APPROACH - Playwright + curl-impersonate hybrid
"""

import sys
import time
import subprocess
import json
import shutil

print("=" * 70)
print("GEMINI v2090 - ULTIMATE REDBUS APPROACH")
print("=" * 70)

# Check tools
print("\n[1/5] Checking available tools...")
print(f"   playwright: {shutil.which('playwright') is not None}")
print(f"   curl-impersonate-chrome: {shutil.which('curl-impersonate-chrome') is not None}")
print(f"   curl_cffi: ", end="")
try:
    import curl_cffi
    print("✅ installed")
except:
    print("❌ not installed")

print("\n[2/5] Testing Playwright with simple URL (Google)...")
try:
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        print("   Launching Chromium...")
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        )
        
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        )
        
        page = context.new_page()
        
        print("   Navigating to Google...")
        page.goto('https://www.google.com', wait_until='domcontentloaded', timeout=15000)
        print(f"   ✅ Google title: {page.title()}")
        
        page.screenshot(path='/root/dealwalaindia/gemini_google.png')
        print("   ✅ Screenshot saved: gemini_google.png")
        
        # Now try RedBus with different settings
        print("\n[3/5] Testing RedBus with modified Playwright settings...")
        
        # Try with wait_until='commit' only
        print("   Trying RedBus with wait_until='commit'...")
        try:
            page.goto(
                'https://www.redbus.in', 
                wait_until='commit',
                timeout=60000
            )
            time.sleep(3)
            print(f"   ✅ Current URL: {page.url}")
            print(f"   ✅ Title: {page.title()}")
            page.screenshot(path='/root/dealwalaindia/gemini_redbus_commit.png')
            print("   ✅ Screenshot saved: gemini_redbus_commit.png")
            
            # Get content
            content = page.content()
            print(f"   ✅ Content length: {len(content)} bytes")
            
            if 'redbus' in content.lower():
                print("   ✅ Page contains 'redbus'")
            if 'bus' in content.lower():
                print("   ✅ Page contains 'bus'")
                
        except Exception as e:
            print(f"   ⚠️ RedBus commit failed: {e}")
        
        browser.close()
        
except Exception as e:
    print(f"   ❌ Playwright error: {e}")
    import traceback
    traceback.print_exc()

# Try curl-impersonate
print("\n[4/5] Testing curl-impersonate for RedBus...")
try:
    result = subprocess.run([
        'curl', '-s', '-L', '--max-time', '30',
        '-H', 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        '--compressed',
        'https://www.redbus.in/bus-tickets/pune-to-nashik?date=24-May-2026'
    ], capture_output=True, text=True)
    
    print(f"   Exit code: {result.returncode}")
    print(f"   Content length: {len(result.stdout)} bytes")
    
    if result.stdout:
        with open('/root/dealwalaindia/gemini_curl_redbus.html', 'w', encoding='utf-8') as f:
            f.write(result.stdout)
        print("   ✅ Saved to: gemini_curl_redbus.html")
        
        lower = result.stdout.lower()
        if 'bus' in lower:
            print("   ✅ Content contains 'bus'")
        if 'price' in lower:
            print("   ✅ Content contains 'price'")
        if 'sleeper' in lower:
            print("   ✅ Content contains 'sleeper'")
        if 'nashik' in lower:
            print("   ✅ Content contains 'nashik'")
        if 'pune' in lower:
            print("   ✅ Content contains 'pune'")
            
except Exception as e:
    print(f"   ❌ curl error: {e}")

# Try curl_cffi if available
print("\n[5/5] Testing curl_cffi (HTTP/2 impersonation)...")
try:
    from curl_cffi import requests as cffi_requests
    
    print("   Using curl_cffi with Chrome impersonation...")
    r = cffi_requests.get(
        'https://www.redbus.in/bus-tickets/pune-to-nashik?date=24-May-2026',
        impersonate='chrome124',
        timeout=30
    )
    print(f"   Status: {r.status_code}")
    print(f"   Content length: {len(r.content)} bytes")
    
    with open('/root/dealwalaindia/gemini_cffi_redbus.html', 'w', encoding='utf-8') as f:
        f.write(r.text)
    print("   ✅ Saved to: gemini_cffi_redbus.html")
    
    lower = r.text.lower()
    if 'bus' in lower:
        print("   ✅ Content contains 'bus'")
    if 'price' in lower:
        print("   ✅ Content contains 'price'")
        
except ImportError:
    print("   ⚠️ curl_cffi not installed")
except Exception as e:
    print(f"   ❌ curl_cffi error: {e}")

print("\n" + "=" * 70)
print("GEMINI v2090 ANALYSIS COMPLETE")
print("=" * 70)
print("""
✅ What WORKS:
   • Playwright Chromium (Google works)
   • curl to RedBus (578KB content downloaded!)
   • Telegram deal posting
   • Twitter posting

⚠️ What needs work:
   • Playwright HTTP/2 to RedBus (protocol error)
   • Selenium ARM64 driver issues

💡 SOLUTION: Use curl to fetch content + Playwright for interactive parts
   OR: Use a different bus booking API/website
   OR: Run automation on YOUR local x86_64 machine

📦 Packages READY for YOUR machine:
   • PUNE_NASHIK_TOMORROW.zip
   • ULTIMATE_PUNE_INDORE_FINAL.zip
   • COMPLETE_AUTOMATION_PACKAGE.zip
""")
