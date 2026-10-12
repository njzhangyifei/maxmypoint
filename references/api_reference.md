# MaxMyPoint API & Web Reference

MaxMyPoint (`https://maxmypoint.com`) tracks award availability, point costs, and cash valuations across Hyatt, Hilton, Marriott, and IHG.

## Web Architecture

The frontend is a React SPA communicating with backend services:
- **Web App**: `https://maxmypoint.com`
- **Data Service**: `https://service.maxmypoint.com`
- **Hotel Web Route**: `https://maxmypoint.com/hotel/{normalized-name}-{hotel_id}`
  - Example: `https://maxmypoint.com/hotel/alila-ventana-big-sur-8616`
  - Slug normalization logic:
    ```javascript
    slug = (name || "").normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase()
      .replace(/[^a-z0-9\s]/g, "")
      .trim()
      .replace(/\s+/g, "-");
    url = `https://maxmypoint.com/hotel/${slug}-${hotel_id}`;
    ```

---

## Service API Endpoints

All endpoints use `GET` requests with standard headers:
```http
User-Agent: Mozilla/5.0 ...
Origin: https://maxmypoint.com
Referer: https://maxmypoint.com/
Accept: application/json, text/plain, */*
```

### 1. Search Hotels: `/hotels`
- **URL**: `https://service.maxmypoint.com/hotels`
- **Parameters**:
  - `search` (string): Keyword matching hotel name, city, or destination (e.g. `Ventana`, `Tokyo`, `Bora Bora`).
  - `brand` (string, case-sensitive): `Hyatt`, `Hilton`, `Marriott`, or `IHG`.
  - `limit` (int): Number of items to return (default: `12`).
  - `page` (int): 1-indexed page number.
  - `sort_by` (string): Sorting order (default: `popularity`).
  - `min_points`, `max_points` (int): Point range filters.
- **Response**:
  ```json
  {
    "rows": [
      {
        "id": 8616,
        "name": "Alila Ventana Big Sur",
        "brand": "Hyatt",
        "code": "sjcal",
        "caption": "Big Sur, CA, US",
        "availability": "2%",
        "category": "8"
      }
    ],
    "total": 2
  }
  ```

### 2. Hotel Metadata: `/hotel-by-id/{hotel_id}`
- **URL**: `https://service.maxmypoint.com/hotel-by-id/{hotel_id}`
- **Response**:
  - `id`: Hotel ID (int)
  - `name`: Hotel Name
  - `brand`: Loyalty program (`Hyatt`, `Hilton`, `Marriott`, `IHG`)
  - `code`: Chain hotel code (e.g. `sjcal`, `TYOCICI`)
  - `category`: Award category or tier
  - `caption`: City, State, Country
  - `availability`: Percentage of days with award space in the coming year (e.g. `2%`, `53%`)
  - `min_night`: Minimum stay requirement
  - `median_value`: Median cent-per-point (cpp) value
  - `max_point_value`: Peak cpp redemption value
  - `calendar_updated_at`: Timestamp dict of last calendar refreshes

### 3. Hotel Location & Amenities: `/hotel-data/{hotel_id}`
- **URL**: `https://service.maxmypoint.com/hotel-data/{hotel_id}`
- **Response**:
  - `t_data.address`: Physical address
  - `t_data.amenities`: Pool, dining, accessibility, activities

### 4. Reward Availability Calendar: `/hotel-rewards-avail`
- **URL**: `https://service.maxmypoint.com/hotel-rewards-avail?id={hotel_id}&nights={nights}`
- **Parameters**:
  - `id` (int, required): The MaxMyPoint hotel ID.
  - `nights` (int, optional): Consecutive nights length (default: `1`).
- **Response**:
  - `hra`: Array of available date records.
    - `avail_date`: Check-in date in `YYYY-MM-DD` format.
    - `points_rate`: Points required (e.g. `90.0K`, `130.0K`).
    - `pay_rate_usd`: Cash rate (e.g. `$3,051`).
    - `point_value`: Value in cents per point (cpp) (e.g. `3.39`).
    - `rate_plan`: Plan name (e.g. `Standard Room`, `Premium Suite`).
    - `room_type`: Room description (e.g. `Big Sur Spa Suite`).
    - `rooms_avail`: Number of rooms available.
    - `res_link`: Deep link to book directly with the hotel chain.
  - `res_link_pattern`: Base link template.
