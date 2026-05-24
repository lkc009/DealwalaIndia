# ================================================
#   COMPREHENSIVE USAGE GUIDE: ALL TRAVEL APIs
# ================================================

## 1. LETSFG (MOST POWERFUL - 400+ AIRLINES)
## ✅ Already installed and tested!

# Search flights (FREE)
letsfg search BOM DEL 2026-06-10 --mode fast
letsfg search PNQ BLR 2026-06-15 --json

# Get API key (free, unlocks GDS/NDC)
letsfg register

# Star GitHub repo (unlimited free access)
# First star: https://github.com/LetsFG/LetsFG
# Then: letsfg star --github YOUR_USERNAME

# Unlock offer (confirms price, reserves 30 min)
letsfg unlock off_xxx

# Book (ticket price only, zero markup)
letsfg book off_xxx \
  -p '{"id":"pas_xxx","given_name":"Lalit","family_name":"Chordiya","born_on":"1981-06-27","gender":"m","title":"mr"}' \
  -e lalitkchordiya@gmail.com

# Python SDK:
# import letsfg
# flights = letsfg.search("BOM", "DEL", "2026-06-10")

---

## 2. FAREEAGLE (INDIA-FOCUSED - FLIGHTS/HOTELS/BUSES)
## ✅ Already tested and working!

# REST API Endpoints:
# https://www.fareeagle.com/api/v1/

# Search flights:
# GET /api/v1/flights/search?from=Pune&to=Delhi&date=2026-06-10&adults=1

# Search hotels:
# GET /api/v1/hotels/search?city=Goa&checkin=2026-06-10&checkout=2026-06-12

# Search buses:
# GET /api/v1/buses/search?from=Pune&to=Bangalore&date=2026-06-10

# MCP Server (add to Claude Desktop):
# URL: https://www.fareeagle.com/mcp/server

# Tools available:
# - search_flights, search_hotels, search_buses
# - prepare_booking, prepare_hotel_booking
# - create_booking, create_hotel_booking
# - check_booking_status, cancel_booking

---

## 3. VALOR TRAVEL (EASIEST - NO SIGNUP, 500/DAY FREE)
## ✅ No API key needed!

# REST API Endpoints:
# https://mcp.valorflights.com/api/

# Search flights:
# GET /api/flights/search?origin=PNQ&destination=DEL&departure_date=2026-06-10

# Cheapest dates:
# GET /api/flights/cheapest?origin=PNQ&destination=DEL&month=2026-06

# Price calendar:
# GET /api/flights/calendar?origin=PNQ&destination=DEL&month=2026-06

# Booking link:
# GET /api/flights/booking-link?origin=PNQ&destination=DEL&departure_date=2026-06-10

# MCP Server (add to Claude Desktop):
# URL: https://mcp.valorflights.com/mcp

# Tools available:
# - search_flights
# - search_cheapest_dates
# - get_price_calendar
# - get_booking_link

---

## 4. NOWAH TRAVEL (FULL TRIP PLANNING - 35+ TOOLS)
## 🔑 Requires OAuth (browser login)

# MCP Server URL:
# https://claw.nowah.xyz/mcp

# Tools available:
# - search_flights, search_hotels, search_locations
# - book_flight, book_hotel, get_offer, get_hotel_quote
# - find_pois, generate_itinerary (116M+ points of interest)
# - get_flight_info, get_airport_delays (live tracking)
# - chat_with_agent (AI travel concierge)
# - weather, currency, visa requirements, safety advisories

---

## 5. SKY SCRAPPER API (SKYSCANNER DATA - RAPIDAPI)
## 📝 Free tier: 100 requests/month

# Setup:
# 1. Go to: https://rapidapi.com/apiheya/api/sky-scrapper
# 2. Subscribe to BASIC plan (FREE, no credit card)
# 3. Copy your X-RapidAPI-Key

# Endpoints:
# - /api/v1/flights/searchAirport (resolve city to skyId)
# - /api/v1/flights/searchFlights (search flights)
# - /api/v1/flights/getPriceCalendar (cheapest per day)
# - /api/v1/flights/getFlightDetails (full itinerary)
# - /api/v1/hotels/searchHotels (hotel search)
# - /api/v1/cars/searchCars (car rental)

# Example Python:
# import requests
# url = "https://sky-scrapper.p.rapidapi.com/api/v1/flights/searchFlights"
# querystring = {
#     "originSkyId": "PUNE",
#     "destinationSkyId": "DELH",
#     "date": "2026-06-10",
#     "adults": "1",
#     "currency": "INR"
# }
# headers = {
#     "X-RapidAPI-Key": "YOUR_KEY",
#     "X-RapidAPI-Host": "sky-scrapper.p.rapidapi.com"
# }
# response = requests.get(url, headers=headers, params=querystring)

---

## 6. GOOGLE FLIGHTS MCP SERVERS
## 📝 Some require SerpAPI key

# Option A: andreacappelletti97/google-flights-mcp (FREE)
# npx google-flights-mcp
# Tools: search_flights, search_multi_city, lookup_airport,
#        find_nearby_airports, get_flight_url, analyze_layovers
# Features: price tracking, calendar heatmap, CO2 emissions,
#           price context (low/typical/high), layover analysis

# Option B: RuairidhT/flights-mcp (SerpAPI)
# Requires SerpAPI key (free tier: 100 searches/month)
# Tools: 14+ tools including flexible dates, price insights,
#        multi-city, open-jaw, stopover planning

---

## 7. STABLETRAVEL.DEV (PAY-PER-REQUEST)
## 💲 Micropayments via USDC (Base/Solana/Tempo)

# Data sources:
# - Google Flights (price discovery: $0.02/search)
# - Amadeus GDS (booking: $0.05/search, $0.03/price confirm)
# - FlightAware (live tracking: $0.005/status)

# Endpoints:
# - /api/google-flights/search ($0.02)
# - /api/flights/search ($0.05)
# - /api/flights/price ($0.03)
# - /api/hotels/search ($0.03)
# - /api/flightaware/flights/ (tracking)

---

## ================================================
##   RECOMMENDATION SUMMARY
## ================================================

| Priority | API | Best For | Cost | Setup |
|----------|-----|----------|------|-------|
| 🥇 1 | LetsFG | Global flights, best prices | FREE | Done |
| 🥈 2 | FareEagle | India (flights/hotels/buses) | FREE | Done |
| 🥉 3 | Valor Travel | Quick searches, no signup | 500/day FREE | Done |
| 4 | Sky Scrapper | Skyscanner data | 100/mo FREE | RapidAPI |
| 5 | Google Flights MCP | Price insights | FREE/SerpAPI | npx |

---

## ================================================
##   FALLBACK CHAIN (AUTOMATIC ALTERNATIVES)
## ================================================

# If one API fails, automatically try the next:

# FLIGHT SEARCH FALLBACK:
# 1. LetsFG (400+ airlines, GDS/NDC)
# 2. FareEagle (India-focused, booking URLs)
# 3. Valor Travel (500/day free, no signup)
# 4. Sky Scrapper (RapidAPI, 100/mo free)

# BUS SEARCH FALLBACK (India):
# 1. FareEagle (search_buses API)
# 2. RedBus (via web or LetsFG if available)

# HOTEL SEARCH FALLBACK:
# 1. FareEagle (search_hotels API)
# 2. LetsFG (300,000+ hotels)
# 3. Valor Travel (if available)

---

## ================================================
##   QUICK START COMMANDS
## ================================================

# Test everything:
python3 /root/dealwalaindia/test_all_travel_apis.py

# Search with LetsFG:
letsfg search BOM DEL 2026-06-10 --mode fast --json

# Search with FareEagle (Python):
# import requests
# r = requests.get("https://www.fareeagle.com/api/v1/flights/search?from=Pune&to=Delhi&date=2026-06-10")
# print(r.json())

# Search with Valor Travel (Python):
# import requests
# r = requests.get("https://mcp.valorflights.com/api/flights/search?origin=BOM&destination=DEL&departure_date=2026-06-10")
# print(r.json())

