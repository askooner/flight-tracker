#!/usr/bin/env python3
"""
Flight Price Tracker - Main runner script.

Monitors flight prices and sends alerts when prices drop.

Usage:
    python tracker.py              # Run once
    python tracker.py --continuous # Run continuously
    python tracker.py --history    # Show price history
"""

import os
import sys
import argparse
import time
from datetime import datetime

from dotenv import load_dotenv
import schedule

from flight_search import FlightSearcher
from price_tracker import PriceTracker
from notifier import Notifier
from config import (
    FLIGHT_CONFIG,
    CHECK_INTERVAL_HOURS,
    MIN_DROP_ALERT,
    PRICE_TARGET,
)


def check_prices(searcher: FlightSearcher, tracker: PriceTracker, notifier: Notifier):
    """Check current prices and record them."""
    config = FLIGHT_CONFIG
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Checking prices...")
    print(f"Route: {config['origin']} → {config['destination']}")
    print(f"Dates: {config['departure_date']} to {config['return_date']}")
    print(f"Bags: {config['bags']} carry-on")

    # Search for flights
    flight = searcher.get_cheapest_flight(
        origin=config["origin"],
        destination=config["destination"],
        departure_date=config["departure_date"],
        return_date=config["return_date"],
        adults=config["adults"],
        bags=config["bags"],
    )

    if not flight:
        print("No flights found. API may be unavailable or check your API key.")
        return

    print(f"\nCheapest flight found:")
    print(flight)

    # Record price and check for drops
    alert = tracker.record_price(
        origin=config["origin"],
        destination=config["destination"],
        departure_date=config["departure_date"],
        return_date=config["return_date"],
        price=flight.price,
        currency=flight.currency,
        airline=flight.airline,
    )

    # Send alert if price dropped significantly
    if alert and alert.drop_amount >= MIN_DROP_ALERT:
        notifier.send_alert(alert)

    # Special alert if price is below target
    if flight.price <= PRICE_TARGET:
        print(f"\n🎯 PRICE TARGET REACHED! Current price ${flight.price:.2f} is at or below your target of ${PRICE_TARGET:.2f}")

    # Show summary
    summary = tracker.get_price_summary(
        config["origin"],
        config["destination"],
        config["departure_date"],
        config["return_date"],
    )
    if summary:
        notifier.send_summary(summary)


def show_history(tracker: PriceTracker):
    """Display price history for the configured route."""
    config = FLIGHT_CONFIG

    history = tracker.get_price_history(
        config["origin"],
        config["destination"],
        config["departure_date"],
        config["return_date"],
    )

    if not history:
        print("No price history recorded yet.")
        return

    print(f"\nPrice History: {config['origin']} → {config['destination']}")
    print(f"Dates: {config['departure_date']} to {config['return_date']}")
    print("-" * 60)

    for record in history:
        timestamp = record["timestamp"][:16].replace("T", " ")
        print(f"{timestamp} | ${record['price']:.2f} | {record['airline']}")

    print("-" * 60)

    summary = tracker.get_price_summary(
        config["origin"],
        config["destination"],
        config["departure_date"],
        config["return_date"],
    )
    if summary:
        print(f"Lowest: ${summary['lowest']:.2f} | Highest: ${summary['highest']:.2f} | Avg: ${summary['average']:.2f}")


def main():
    parser = argparse.ArgumentParser(description="Flight Price Tracker")
    parser.add_argument(
        "--continuous", "-c",
        action="store_true",
        help="Run continuously and check prices periodically"
    )
    parser.add_argument(
        "--history", "-H",
        action="store_true",
        help="Show price history"
    )
    args = parser.parse_args()

    # Load environment variables
    load_dotenv()

    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        print("Error: SERPAPI_KEY not set in .env file")
        print("Get a free API key at https://serpapi.com")
        sys.exit(1)

    # Initialize components
    searcher = FlightSearcher(api_key)
    tracker = PriceTracker()
    notifier = Notifier.from_env()

    if args.history:
        show_history(tracker)
        return

    if args.continuous:
        print(f"Starting continuous price tracking (every {CHECK_INTERVAL_HOURS} hours)")
        print("Press Ctrl+C to stop\n")

        # Run immediately first
        check_prices(searcher, tracker, notifier)

        # Schedule periodic checks
        schedule.every(CHECK_INTERVAL_HOURS).hours.do(
            check_prices, searcher, tracker, notifier
        )

        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute if scheduled task should run
        except KeyboardInterrupt:
            print("\nStopping price tracker...")
    else:
        # Single check
        check_prices(searcher, tracker, notifier)


if __name__ == "__main__":
    main()
