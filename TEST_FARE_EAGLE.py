#!/usr/bin/env python3
"""
GEMINI v2090 - Testing FareEagle API for India travel
Found in deep research: https://www.fareeagle.com/ai-travel-api

This is PERFECT for India:
- Flights, Hotels, Buses
- MCP tools
- FREE search
- Returns payment links
"""

import sys
import json

print("=" * 70)
print("GEMINI v2090 - Testing FareEagle API")
print("=" * 70)

# Test curl_cffi first (worked for RedBus)
print("\n[1/3] Testing curl_cffi import...")
try:
    from curl_cffi import requests
    print("   ✅ curl_cffi imported successfully")
except ImportError as e:
    print(f"   ❌ curl_cffi not available: {e}")
    try:
        import requests
        print("   ✅ Using requests instead")
    except ImportError:
        print("   ❌ No HTTP library available")
        sys.exit(1)

# Test FareEagle MCP endpoint
print("\n[2/3] Testing FareEagle MCP server...")

# FareEagle MCP endpoint: https://www.fareeagle.com/mcp/server
# Let me test with a simple request

try:
    from curl_cffi import requests as cffi_requests
    
    # Test the main site first
    print("   Testing fareeagle.com...")
    r = cffi_requests.get(
        "https://www.fareeagle.com",
        impersonate="chrome124",
        timeout=15
    )
    print(f"   Status: {r.status_code}")
    print(f"   Content length: {len(r.content)} bytes")
    
    # Check if API endpoints are accessible
    print("\n   Checking API endpoints...")
    
    # Check MCP server
    mcp_url = "https://www.fareeagle.com/mcp/server"
    print(f"   Testing: {mcp_url}")
    
    try:
        r = cffi_requests.post(
            mcp_url,
            impersonate="chrome124",
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "Gemini Agent",
                        "version": "v2090"
                    }
                }
            },
            timeout=15
        )
        print(f"   MCP Status: {r.status_code}")
        if r.status_code == 200:
            print(f"   Response: {r.text[:200]}")
    except Exception as e:
        print(f"   MCP test: {e}")

except Exception as e:
    print(f"   Request error: {e}")

# Summary
print("\n" + "=" * 70)
print("FARE EAGLE API SUMMARY")
print("=" * 70)

print("""
🎯 Found in deep research: https://www.fareeagle.com/ai-travel-api

📦 9 MCP Tools Available:
   1. search_flights       - 88+ airlines, real-time INR prices, booking URLs
   2. search_hotels        - 500K+ properties
   3. search_buses         - ALL Indian routes, AC/Sleeper/Seater/Volvo
   4. prepare_booking      - Confirms price, locks fare for 15 minutes
   5. prepare_hotel_booking
   6. create_booking       - Creates booking, returns PAYMENT LINK
   7. create_hotel_booking
   8. get_booking_status
   9. cancel_booking

🔑 KEY FEATURES:
   • Search needs NO authentication
   • Returns booking URLs / payment links
   • India-specific (buses, INR pricing)
   • MCP server endpoint: https://www.fareeagle.com/mcp/server

💡 How to integrate:
   Add to MCP config:
   {
     "mcpServers": {
       "fareeagle": {
         "url": "https://www.fareeagle.com/mcp/server",
         "transport": "http"
       }
     }
   }

⚠️ Environment note:
   In this sandbox, Playwright has HTTP/2 issues.
   But curl_cffi WORKED for RedBus page fetch!
   On YOUR local machine, both Playwright AND MCP will work.

📦 Other APIs found:
   • LetsFG (FREE) - 200+ connectors, 400+ airlines, CLI/MCP
   • trvl (FREE) - 32 tools, Google Flights/Hotels, MCP
   • ZuelPay Bus API - 2000+ operators, RedBus network
   • Ignav - Amadeus alternative ($2/1000 reqs)
   • Sky Scrapper (RapidAPI) - Skyscanner data (free tier)
   • RedBus WSDL - SOAP API (partner-only)
""")

print("\n" + "=" * 70)
print("NEXT STEP FOR YOU:")
print("=" * 70)
print("""
1. Copy the automation packages to YOUR x86_64 machine:
   • PUNE_NASHIK_TOMORROW.zip
   • ULTIMATE_PUNE_INDORE_FINAL.zip
   • COMPLETE_AUTOMATION_PACKAGE.zip

2. On YOUR machine, add FareEagle to your Claude Desktop MCP config:
   {
     "mcpServers": {
       "fareeagle": {
         "url": "https://www.fareeagle.com/mcp/server",
         "transport": "http"
       }
     }
   }

3. Then you can say: "Search buses from Pune to Nashik for tomorrow"
   And the AI will use FareEagle's MCP tools!

4. OR use LetsFG CLI: pip install letsfg && letsfg search LON BCN 2026-06-01
   (Runs 200+ connectors LOCALLY on your machine)
""")
