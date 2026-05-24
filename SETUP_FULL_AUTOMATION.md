# FULL AUTOMATION SETUP GUIDE

## Prerequisites
Playwright 1.60.0 is installed. Need to ensure Chromium browser is installed.

## Step 1: Install Playwright Chromium

Run this command:
```bash
playwright install chromium
```

Or install all browsers:
```bash
playwright install
```

## Step 2: Run the Automation

```bash
cd /root/dealwalaindia
python3 auto_book_bus.py
```

## What the Automation Does

1. **Opens RedBus** - Pune to Bangalore
2. **Applies Filters** - AC + Sleeper
3. **Sorts** - By Price (Low to High)
4. **Selects Bus** - Cheapest Volvo/AC Sleeper
5. **Chooses Seat** - Best available (lower berth preferred)
6. **Fills Details** - Name: Lalit Chordiya, Age: 44, Gender: Male, Email, Phone
7. **Navigates** - To payment page

## Alternative: If Playwright Browser Issues

### Option A: Install Chromium
```bash
playwright install chromium
```

### Option B: Use Simplified Version

I've also created a simpler version that opens RedBus with all your details
and guides you step by step.

```bash
cd /root/dealwalaindia
python3 auto_book_bus_simple.py
```

## Manual Steps (If Automation Fails)

If the automation doesn't work perfectly, here's what to do:

1. **Open RedBus**: https://www.redbus.in/bus-tickets/pune-to-bangalore?date=26-May-2026

2. **Apply Filters**:
   - Click `AC` (under Bus Type)
   - Click `Sleeper` (under Bus Type)

3. **Sort**:
   - Click "Sort by" → "Price (Low to High)"

4. **Choose Bus**:
   - Look for: KSRTC Airavat, MSRTC Shivneri, IntrCity SmartBus, VRL Travels
   - These are Volvo/AC Sleeper options

5. **View Seats**:
   - Click "View Seats"
   - Choose a lower berth seat (more comfortable for overnight)

6. **Enter Passenger Details**:
   ```
   Name: Lalit Chordiya
   Age: 44
   Gender: Male
   Email: lalitkchordiya@gmail.com
   Phone: 9730472789
   ```

7. **Payment**:
   - Select UPI
   - Enter: `lalitkchordiya-1@oksbi`
   - Complete payment in your UPI app

## Files Created

| File | Purpose |
|------|---------|
| `auto_book_bus.py` | Full Playwright automation (complete) |
| `auto_book_bus_simple.py` | Simplified version (opens browser, guides you) |
| `redbus_booking_guide.py` | Text guide with all details |
| `redbus_booking_data.json` | Saved booking data |

## Quick Commands

```bash
# Install Playwright browsers (run once)
playwright install chromium

# Run full automation
cd /root/dealwalaindia
python3 auto_book_bus.py

# If that fails, try simplified
python3 auto_book_bus_simple.py

# Or just open RedBus manually
python3 redbus_booking_guide.py
```

## Expected Prices (Volvo/AC Sleeper)

| Operator | Price Range | Notes |
|----------|-------------|-------|
| KSRTC Airavat | ₹900-1,500 | Govt, Volvo |
| MSRTC Shivneri | ₹850-1,400 | Govt, Volvo |
| IntrCity SmartBus | ₹1,200-1,800 | Private, Volvo 9600 |
| VRL Travels | ₹1,300-1,900 | Private, Multi-Axle |
| SRS Travels | ₹1,400-2,000 | Private, Volvo/Mercedes |

## Best Days to Book

- **Cheapest**: Monday, Tuesday, Wednesday, Thursday
- **Expensive**: Friday, Saturday, Sunday (+30-50%)
