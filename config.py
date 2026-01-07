"""
Flight tracker configuration.

Edit these settings to track your specific flights.
"""

# Your flight search configuration
FLIGHT_CONFIG = {
    # Route
    "origin": "YYZ",           # Toronto Pearson
    "destination": "YVR",      # Vancouver International

    # Travel dates (YYYY-MM-DD format)
    "departure_date": "2026-07-29",
    "return_date": "2026-08-05",

    # Passengers and bags
    "adults": 1,
    "bags": 0,                 # Checked bags (0 = carry-on only, which is usually included)
}

# How often to check prices (in hours)
CHECK_INTERVAL_HOURS = 6

# Minimum price drop to trigger alert (in dollars)
# Set to 0 to get alerts for any price drop
MIN_DROP_ALERT = 10.0

# Price target - get special alert when price drops below this
PRICE_TARGET = 400.0
