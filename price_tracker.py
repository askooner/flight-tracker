"""
Price tracking module - stores price history and detects price drops.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, asdict


@dataclass
class PriceRecord:
    """A single price record in history."""
    price: float
    currency: str
    airline: str
    timestamp: str
    route: str
    departure_date: str
    return_date: str


@dataclass
class PriceAlert:
    """Alert when price drops."""
    current_price: float
    previous_price: float
    lowest_price: float
    drop_amount: float
    drop_percent: float
    airline: str
    route: str
    departure_date: str
    return_date: str

    def __str__(self):
        return (
            f"PRICE DROP ALERT!\n"
            f"Route: {self.route}\n"
            f"Dates: {self.departure_date} to {self.return_date}\n"
            f"Airline: {self.airline}\n"
            f"Current Price: ${self.current_price:.2f}\n"
            f"Previous Price: ${self.previous_price:.2f}\n"
            f"You Save: ${self.drop_amount:.2f} ({self.drop_percent:.1f}%)\n"
            f"Lowest Recorded: ${self.lowest_price:.2f}"
        )


class PriceTracker:
    """Track flight prices over time and detect drops."""

    def __init__(self, history_file: str = "price_history.json"):
        self.history_file = Path(history_file)
        self.history: dict = self._load_history()

    def _load_history(self) -> dict:
        """Load price history from file."""
        if self.history_file.exists():
            try:
                with open(self.history_file, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def _save_history(self):
        """Save price history to file."""
        with open(self.history_file, "w") as f:
            json.dump(self.history, f, indent=2)

    def _get_route_key(self, origin: str, destination: str, departure_date: str, return_date: str) -> str:
        """Generate a unique key for this route and dates."""
        return f"{origin}-{destination}_{departure_date}_{return_date}"

    def record_price(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: str,
        price: float,
        currency: str,
        airline: str,
    ) -> Optional[PriceAlert]:
        """
        Record a new price and check for price drops.

        Returns PriceAlert if price dropped, None otherwise.
        """
        route_key = self._get_route_key(origin, destination, departure_date, return_date)
        route_str = f"{origin} → {destination}"

        record = PriceRecord(
            price=price,
            currency=currency,
            airline=airline,
            timestamp=datetime.now().isoformat(),
            route=route_str,
            departure_date=departure_date,
            return_date=return_date,
        )

        if route_key not in self.history:
            self.history[route_key] = {
                "prices": [],
                "lowest_price": price,
                "highest_price": price,
            }

        route_history = self.history[route_key]
        prices = route_history["prices"]

        # Check for price drop
        alert = None
        if prices:
            last_price = prices[-1]["price"]
            lowest_price = route_history["lowest_price"]

            if price < last_price:
                drop_amount = last_price - price
                drop_percent = (drop_amount / last_price) * 100

                alert = PriceAlert(
                    current_price=price,
                    previous_price=last_price,
                    lowest_price=min(lowest_price, price),
                    drop_amount=drop_amount,
                    drop_percent=drop_percent,
                    airline=airline,
                    route=route_str,
                    departure_date=departure_date,
                    return_date=return_date,
                )

        # Update history
        prices.append(asdict(record))
        route_history["lowest_price"] = min(route_history["lowest_price"], price)
        route_history["highest_price"] = max(route_history["highest_price"], price)

        self._save_history()
        return alert

    def get_price_history(self, origin: str, destination: str, departure_date: str, return_date: str) -> list[dict]:
        """Get price history for a specific route."""
        route_key = self._get_route_key(origin, destination, departure_date, return_date)
        if route_key in self.history:
            return self.history[route_key]["prices"]
        return []

    def get_lowest_price(self, origin: str, destination: str, departure_date: str, return_date: str) -> Optional[float]:
        """Get the lowest recorded price for a route."""
        route_key = self._get_route_key(origin, destination, departure_date, return_date)
        if route_key in self.history:
            return self.history[route_key]["lowest_price"]
        return None

    def get_price_summary(self, origin: str, destination: str, departure_date: str, return_date: str) -> Optional[dict]:
        """Get a summary of price tracking for a route."""
        route_key = self._get_route_key(origin, destination, departure_date, return_date)
        if route_key not in self.history:
            return None

        route_history = self.history[route_key]
        prices = [p["price"] for p in route_history["prices"]]

        return {
            "route": f"{origin} → {destination}",
            "dates": f"{departure_date} to {return_date}",
            "checks": len(prices),
            "lowest": route_history["lowest_price"],
            "highest": route_history["highest_price"],
            "current": prices[-1] if prices else None,
            "average": sum(prices) / len(prices) if prices else None,
        }
