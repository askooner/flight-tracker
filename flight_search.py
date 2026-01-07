"""
Flight search module using SerpApi's Google Flights integration.
"""

import requests
from typing import Optional
from dataclasses import dataclass


@dataclass
class FlightResult:
    """Represents a flight search result."""
    price: float
    currency: str
    airline: str
    departure_time: str
    arrival_time: str
    duration: str
    stops: int
    has_carry_on: bool
    outbound_date: str
    return_date: str
    booking_link: Optional[str] = None

    def __str__(self):
        stops_str = "nonstop" if self.stops == 0 else f"{self.stops} stop(s)"
        return (
            f"{self.airline} - ${self.price:.2f} {self.currency}\n"
            f"  Departure: {self.departure_time} | Duration: {self.duration} | {stops_str}\n"
            f"  Carry-on included: {'Yes' if self.has_carry_on else 'No'}"
        )


class FlightSearcher:
    """Search for flights using SerpApi Google Flights."""

    SERPAPI_URL = "https://serpapi.com/search"

    # Airport codes
    AIRPORT_CODES = {
        "toronto": "YYZ",
        "vancouver": "YVR",
    }

    def __init__(self, api_key: str):
        self.api_key = api_key

    def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str] = None,
        adults: int = 1,
        bags: int = 1,  # Carry-on bags
    ) -> list[FlightResult]:
        """
        Search for flights between two cities.

        Args:
            origin: Origin city or airport code
            destination: Destination city or airport code
            departure_date: Departure date (YYYY-MM-DD)
            return_date: Return date for round trip (YYYY-MM-DD), None for one-way
            adults: Number of adult passengers
            bags: Number of carry-on bags (affects pricing)

        Returns:
            List of FlightResult objects sorted by price
        """
        # Convert city names to airport codes if needed
        origin_code = self.AIRPORT_CODES.get(origin.lower(), origin.upper())
        dest_code = self.AIRPORT_CODES.get(destination.lower(), destination.upper())

        params = {
            "engine": "google_flights",
            "departure_id": origin_code,
            "arrival_id": dest_code,
            "outbound_date": departure_date,
            "adults": adults,
            "bags": bags,
            "currency": "CAD",
            "hl": "en",
            "api_key": self.api_key,
        }

        if return_date:
            params["return_date"] = return_date
            params["type"] = "1"  # Round trip
        else:
            params["type"] = "2"  # One way

        try:
            response = requests.get(self.SERPAPI_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            return self._parse_results(data, departure_date, return_date)

        except requests.RequestException as e:
            print(f"Error searching flights: {e}")
            return []

    def _parse_results(
        self, data: dict, departure_date: str, return_date: Optional[str]
    ) -> list[FlightResult]:
        """Parse SerpApi response into FlightResult objects."""
        results = []

        # Check for best flights first, then other flights
        flights_data = data.get("best_flights", []) + data.get("other_flights", [])

        for flight in flights_data:
            try:
                # Get the first leg info
                legs = flight.get("flights", [])
                if not legs:
                    continue

                first_leg = legs[0]
                airline = first_leg.get("airline", "Unknown")
                departure_time = first_leg.get("departure_airport", {}).get("time", "")
                arrival_time = legs[-1].get("arrival_airport", {}).get("time", "")

                # Calculate total duration and stops
                total_duration = flight.get("total_duration", 0)
                hours, mins = divmod(total_duration, 60)
                duration_str = f"{hours}h {mins}m"
                stops = len(legs) - 1

                # Get price
                price = flight.get("price", 0)

                # Check if carry-on is included (bags info)
                extensions = flight.get("extensions", [])
                has_carry_on = any("carry-on" in ext.lower() for ext in extensions)

                results.append(
                    FlightResult(
                        price=float(price),
                        currency="CAD",
                        airline=airline,
                        departure_time=departure_time,
                        arrival_time=arrival_time,
                        duration=duration_str,
                        stops=stops,
                        has_carry_on=has_carry_on,
                        outbound_date=departure_date,
                        return_date=return_date or "",
                        booking_link=flight.get("booking_token"),
                    )
                )
            except (KeyError, TypeError) as e:
                print(f"Error parsing flight: {e}")
                continue

        # Sort by price
        results.sort(key=lambda x: x.price)
        return results

    def get_cheapest_flight(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str] = None,
        adults: int = 1,
        bags: int = 1,
    ) -> Optional[FlightResult]:
        """Get the cheapest flight for the given route."""
        results = self.search_flights(
            origin, destination, departure_date, return_date, adults, bags
        )
        return results[0] if results else None
