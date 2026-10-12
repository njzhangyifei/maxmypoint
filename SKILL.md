---
name: maxmypoint-hotel-query
description: >-
  Query hotel award availability, points pricing, cash rates, and redemption valuations (cpp)
  on MaxMyPoint (https://maxmypoint.com) across Hyatt, Hilton, Marriott, and IHG.
  Use when searching for award space, finding points rates for specific hotels or destinations,
  checking award calendar dates, or looking up hotel loyalty availability.
---

# MaxMyPoint Hotel Query Skill

Query award availability, points pricing, cash rates, cents-per-point (cpp) valuations, and direct booking links on [MaxMyPoint](https://maxmypoint.com) for Hyatt, Hilton, Marriott, and IHG properties.

## Quick Start (CLI Helper)

The bundled CLI script [`scripts/query_hotel.py`](./scripts/query_hotel.py) runs with Python standard library (no extra dependencies required).

### 1. Search Hotels
Search by hotel name, city, airport, or region. Optionally filter by brand (`Hyatt`, `Hilton`, `Marriott`, `IHG`):

```bash
python3 scripts/query_hotel.py search "Ventana"
python3 scripts/query_hotel.py search "Tokyo" --brand Hilton
python3 scripts/query_hotel.py search "Kyoto" --brand Marriott --limit 5
```

Output includes:
- Hotel ID (e.g. `8616`)
- Hotel Name
- Brand / Loyalty program
- Chain property code (e.g. `sjcal`)
- City / Country
- Total award availability percentage over the upcoming year (e.g. `2%`, `84%`)

### 2. Inspect Hotel Details & Point Valuations
Retrieve category tier, minimum stay requirements, median/peak point values (cpp), address, and web link:

```bash
# By Hotel ID:
python3 scripts/query_hotel.py info 8616

# By Hotel Name / Search query:
python3 scripts/query_hotel.py info "Alila Ventana Big Sur"

# By MaxMyPoint URL or slug:
python3 scripts/query_hotel.py info "https://maxmypoint.com/hotel/alila-ventana-big-sur-8616"
```

### 3. Query Award Availability Calendar & Dates
Inspect exact dates with award availability, required points, cash rates, redemption value (cpp), room types, and booking links:

```bash
# Query all upcoming reward dates:
python3 scripts/query_hotel.py avail 8616

# Filter by date range (e.g., November 2026):
python3 scripts/query_hotel.py avail 3877 --start 2026-11-01 --end 2026-11-30

# Filter by minimum redemption value (cpp):
python3 scripts/query_hotel.py avail 8616 --min-cpp 3.0

# Filter by room type or rate plan (e.g., Standard vs Suite):
python3 scripts/query_hotel.py avail 3877 --room-type "Std"

# Query multi-night consecutive availability (e.g., 2 nights):
python3 scripts/query_hotel.py avail 8616 --nights 2
```

### 4. Output Raw JSON for Programmatic Analysis
Pass `--json` to any subcommand:

```bash
python3 scripts/query_hotel.py avail 8616 --start 2026-10-01 --end 2026-12-31 --json
```

---

## Browser Testing Workflow

To test or view a hotel page in the browser:

1. **Generate the Web URL**:
   ```bash
   python3 scripts/query_hotel.py url "Conrad Tokyo"
   # Output: https://maxmypoint.com/hotel/conrad-tokyo-3877
   ```

2. **Open in Default Browser (macOS)**:
   ```bash
   open $(python3 scripts/query_hotel.py url "Alila Ventana Big Sur")
   ```

3. **Interactive In-Chat Browsing**:
   - You can use the `/browser` slash command to open, inspect, and interact with the page live inside the chat environment.
   - On the web page, verify:
     - The **Availability Calendar** (green days show open award inventory).
     - The **Points vs Cash** toggle at the top of the calendar.
     - The **Alerts** drawer for setting up notifications when new award inventory opens.

---

## API Details

For low-level endpoint schemas, query parameters, and data structures, see the [API Reference](./references/api_reference.md).
