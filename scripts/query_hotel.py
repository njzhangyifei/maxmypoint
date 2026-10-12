#!/usr/bin/env python3
"""
MaxMyPoint Hotel Query Helper
CLI tool for searching hotels, retrieving details, and querying award availability.
Requires only Python standard library.
"""

import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime

BASE_SERVICE_URL = "https://service.maxmypoint.com"
BASE_WEB_URL = "https://maxmypoint.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Origin": "https://maxmypoint.com",
    "Referer": "https://maxmypoint.com/",
    "Accept": "application/json, text/plain, */*",
}


def http_get(url, timeout=15):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def slugify_hotel_name(name, hotel_id):
    normalized = name.lower()
    normalized = re.sub(r"[^\w\s-]", "", normalized)
    slug = re.sub(r"[\s_]+", "-", normalized).strip("-")
    return f"{slug}-{hotel_id}"


def get_web_url(hotel_name, hotel_id):
    slug = slugify_hotel_name(hotel_name, hotel_id)
    return f"{BASE_WEB_URL}/hotel/{slug}"


def resolve_hotel_id(identifier):
    """
    Resolve identifier to integer hotel_id.
    Identifier can be:
    - Digits: '8616'
    - Full URL: 'https://maxmypoint.com/hotel/alila-ventana-big-sur-8616'
    - Slug: 'alila-ventana-big-sur-8616'
    - Hotel code or name: searches and returns best match ID
    """
    if str(identifier).isdigit():
        return int(identifier)

    # Check for URL or slug ending in digits
    m = re.search(r"-(\d+)(?:[/?#]|$)", str(identifier))
    if m:
        return int(m.group(1))

    # Search by text
    results = search_hotels(str(identifier), limit=1)
    if results:
        return results[0]["id"]

    raise ValueError(f"Could not resolve hotel identifier: {identifier}")


def search_hotels(query, brand=None, limit=10):
    params = {"search": query, "limit": limit}
    if brand:
        # Normalize brand capitalization
        brand_map = {
            "hyatt": "Hyatt",
            "hilton": "Hilton",
            "marriott": "Marriott",
            "ihg": "IHG",
        }
        params["brand"] = brand_map.get(brand.lower(), brand)

    url = f"{BASE_SERVICE_URL}/hotels?{urllib.parse.urlencode(params)}"
    data = http_get(url)
    return data.get("rows", [])


def get_hotel_info(hotel_id):
    url = f"{BASE_SERVICE_URL}/hotel-by-id/{hotel_id}"
    return http_get(url)


def get_hotel_additional_data(hotel_id):
    url = f"{BASE_SERVICE_URL}/hotel-data/{hotel_id}"
    try:
        return http_get(url).get("t_data", {})
    except Exception:
        return {}


def get_hotel_availability(hotel_id, nights=1):
    url = f"{BASE_SERVICE_URL}/hotel-rewards-avail?id={hotel_id}&nights={nights}"
    data = http_get(url, timeout=25)
    return data.get("hra", []), data.get("res_link_pattern", "")


def format_table(rows, headers):
    if not rows:
        return "No data found."
    widths = [len(h) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            widths[i] = max(widths[i], len(str(val)))

    header_str = " | ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
    separator_str = "-+-".join("-" * widths[i] for i in range(len(headers)))
    row_strs = [
        " | ".join(str(val).ljust(widths[i]) for i, val in enumerate(row))
        for row in rows
    ]
    return "\n".join([header_str, separator_str] + row_strs)


def cmd_search(args):
    hotels = search_hotels(args.query, brand=args.brand, limit=args.limit)
    if args.json:
        print(json.dumps(hotels, indent=2))
        return

    if not hotels:
        print(f"No hotels found matching '{args.query}'")
        return

    table_data = []
    for h in hotels:
        table_data.append([
            h.get("id"),
            h.get("name", "N/A"),
            h.get("brand", "N/A"),
            h.get("code", "N/A"),
            h.get("caption", "N/A"),
            h.get("availability", "N/A"),
        ])
    headers = ["ID", "Hotel Name", "Brand", "Code", "Location", "Avail %"]
    print(format_table(table_data, headers))


def cmd_info(args):
    hotel_id = resolve_hotel_id(args.hotel)
    info = get_hotel_info(hotel_id)
    extra = get_hotel_additional_data(hotel_id)

    if args.json:
        combined = {**info, "extra": extra}
        print(json.dumps(combined, indent=2))
        return

    name = info.get("name", "Unknown Hotel")
    brand = info.get("brand", "Unknown")
    code = info.get("code", "N/A")
    avail = info.get("availability", "N/A")
    category = info.get("category", "N/A")
    location = info.get("caption", "N/A")
    min_nights = info.get("min_night", 1)
    median_val = info.get("median_value", "N/A")
    max_val = info.get("max_point_value", "N/A")
    web_url = get_web_url(name, hotel_id)

    print("=" * 60)
    print(f"Hotel: {name} (ID: {hotel_id})")
    print(f"Brand: {brand} | Code: {code} | Category: {category}")
    print(f"Location: {location}")
    print(f"Availability Rate: {avail}")
    print(f"Min Nights: {min_nights}")
    print(f"Median Point Value: {median_val} cpp | Max Point Value: {max_val} cpp")
    print(f"Web URL: {web_url}")
    if extra.get("address"):
        print(f"Address: {extra.get('address')}")
    print("=" * 60)


def cmd_avail(args):
    hotel_id = resolve_hotel_id(args.hotel)
    info = get_hotel_info(hotel_id)
    name = info.get("name", "Hotel")
    avail_list, res_pattern = get_hotel_availability(hotel_id, nights=args.nights)

    # Filtering
    filtered = []
    for item in avail_list:
        date_str = item.get("avail_date")
        if not date_str:
            continue

        if args.start and date_str < args.start:
            continue
        if args.end and date_str > args.end:
            continue

        if args.min_cpp is not None:
            pv = item.get("point_value")
            try:
                if float(pv) < args.min_cpp:
                    continue
            except (ValueError, TypeError):
                continue

        if args.room_type:
            rt = str(item.get("room_type", "")).lower()
            rp = str(item.get("rate_plan", "")).lower()
            query = args.room_type.lower()
            if query not in rt and query not in rp:
                continue

        filtered.append(item)

    if args.json:
        print(json.dumps(filtered, indent=2))
        return

    print(f"\n{name} (ID: {hotel_id}) - {len(filtered)} available reward dates found:")
    print(f"MaxMyPoint URL: {get_web_url(name, hotel_id)}")
    print("-" * 60)

    if not filtered:
        print("No availability matched the specified criteria.")
        return

    table_data = []
    for item in filtered[:args.limit]:
        date = item.get("avail_date")
        pts = item.get("points_rate") or "-"
        cash = item.get("pay_rate_usd") or "-"
        cpp = f"{item.get('point_value')} cpp" if item.get("point_value") else "-"
        plan = (item.get("rate_plan") or "")[:20]
        room = (item.get("room_type") or "")[:25]
        link = item.get("res_link") or "-"
        table_data.append([date, pts, cash, cpp, plan, room])

    headers = ["Date", "Points", "Cash Rate", "Value", "Rate Plan", "Room Type"]
    print(format_table(table_data, headers))

    if len(filtered) > args.limit:
        print(f"\n... and {len(filtered) - args.limit} more dates. Use --limit to show more.")


def cmd_url(args):
    hotel_id = resolve_hotel_id(args.hotel)
    info = get_hotel_info(hotel_id)
    name = info.get("name", "Hotel")
    url = get_web_url(name, hotel_id)
    print(url)


def main():
    parser = argparse.ArgumentParser(description="MaxMyPoint Hotel Query Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Search
    p_search = subparsers.add_parser("search", help="Search hotels by name, location, or keyword")
    p_search.add_argument("query", help="Search keyword (hotel name, city, etc.)")
    p_search.add_argument("--brand", choices=["Hyatt", "Hilton", "Marriott", "IHG", "hyatt", "hilton", "marriott", "ihg"], help="Filter by loyalty program")
    p_search.add_argument("--limit", type=int, default=10, help="Max results to display")
    p_search.add_argument("--json", action="store_true", help="Output raw JSON")
    p_search.set_defaults(func=cmd_search)

    # Info
    p_info = subparsers.add_parser("info", help="Get hotel details and point valuation")
    p_info.add_argument("hotel", help="Hotel ID, slug, URL, or name query")
    p_info.add_argument("--json", action="store_true", help="Output raw JSON")
    p_info.set_defaults(func=cmd_info)

    # Avail
    p_avail = subparsers.add_parser("avail", help="Query reward availability calendar")
    p_avail.add_argument("hotel", help="Hotel ID, slug, URL, or name query")
    p_avail.add_argument("--nights", type=int, default=1, help="Number of consecutive nights (default: 1)")
    p_avail.add_argument("--start", help="Start date filter (YYYY-MM-DD)")
    p_avail.add_argument("--end", help="End date filter (YYYY-MM-DD)")
    p_avail.add_argument("--min-cpp", type=float, help="Minimum point value in cents per point")
    p_avail.add_argument("--room-type", help="Filter by room type or rate plan keyword (e.g. Standard, Suite)")
    p_avail.add_argument("--limit", type=int, default=30, help="Max rows to display in table")
    p_avail.add_argument("--json", action="store_true", help="Output raw JSON")
    p_avail.set_defaults(func=cmd_avail)

    # URL
    p_url = subparsers.add_parser("url", help="Get MaxMyPoint web URL for browser viewing")
    p_url.add_argument("hotel", help="Hotel ID, slug, URL, or name query")
    p_url.set_defaults(func=cmd_url)

    args = parser.parse_args()
    try:
        args.func(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
