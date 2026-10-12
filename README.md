# MaxMyPoint Hotel Query Skill

An Antigravity skill for querying hotel award availability, point values, cash prices, and booking links on [MaxMyPoint](https://maxmypoint.com) across Hyatt, Hilton, Marriott, and IHG programs.

## Features

- **Search**: Find hotels across programs by name, city, airport, brand, or code.
- **Hotel Info**: Retrieve property tier/category, overall annual award space percentage, median & max cpp (cents per point) valuation, address, and coordinates.
- **Award Calendar**: View exact dates with award availability, room types, rate plans, point costs, cash rates, and value.
- **Browser Testing**: Easy URL generation and commands to view and test hotel pages in the browser.

## Quick CLI Usage

```bash
# Search hotels
./scripts/query_hotel.py search "Ventana"
./scripts/query_hotel.py search "Tokyo" --brand Hilton

# Hotel info & valuation
./scripts/query_hotel.py info "Alila Ventana Big Sur"
./scripts/query_hotel.py info 8616

# Award dates and availability
./scripts/query_hotel.py avail 8616 --limit 10
./scripts/query_hotel.py avail "Conrad Tokyo" --start 2026-11-01 --end 2026-11-30 --min-cpp 0.5

# Generate browser URL
./scripts/query_hotel.py url "Alila Ventana Big Sur"
```

## Structure

```
├── SKILL.md                          # Antigravity skill definition
├── scripts/
│   └── query_hotel.py                # Standalone Python CLI helper
├── references/
│   └── api_reference.md              # Detailed API endpoint & data schema docs
└── .agents/
    └── skills/
        └── maxmypoint-hotel-query/   # Workspace skill discovery root
```
