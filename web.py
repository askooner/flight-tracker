#!/usr/bin/env python3
"""
Flight Price Tracker - Web Dashboard
"""

import os
from datetime import datetime
from flask import Flask, render_template_string, jsonify, redirect, url_for
from dotenv import load_dotenv

from flight_search import FlightSearcher
from price_tracker import PriceTracker
from notifier import Notifier
from config import FLIGHT_CONFIG, PRICE_TARGET

load_dotenv()

app = Flask(__name__)

# Initialize components
api_key = os.getenv("SERPAPI_KEY", "")
searcher = FlightSearcher(api_key) if api_key else None
tracker = PriceTracker()
notifier = Notifier.from_env()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Flight Price Tracker</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #fff;
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { text-align: center; margin-bottom: 10px; font-size: 2em; }
        .route { text-align: center; color: #8892b0; margin-bottom: 30px; font-size: 1.1em; }

        .card {
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
        }

        .price-display {
            text-align: center;
            padding: 40px;
        }
        .current-price {
            font-size: 4em;
            font-weight: 700;
            color: #64ffda;
        }
        .price-label { color: #8892b0; margin-top: 10px; }

        .stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            text-align: center;
        }
        .stat-value { font-size: 1.8em; font-weight: 600; color: #fff; }
        .stat-label { color: #8892b0; font-size: 0.9em; margin-top: 5px; }
        .stat-low { color: #64ffda; }
        .stat-high { color: #ff6b6b; }

        .history { margin-top: 20px; }
        .history-item {
            display: flex;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .history-item:last-child { border-bottom: none; }
        .history-price { font-weight: 600; }
        .history-time { color: #8892b0; }

        .btn {
            display: inline-block;
            background: #64ffda;
            color: #1a1a2e;
            padding: 12px 24px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            border: none;
            cursor: pointer;
            font-size: 1em;
        }
        .btn:hover { background: #4fd1b0; }
        .btn-container { text-align: center; margin: 30px 0; }

        .target {
            text-align: center;
            padding: 15px;
            background: rgba(100, 255, 218, 0.1);
            border-radius: 8px;
            margin-top: 20px;
        }
        .target-reached {
            background: rgba(100, 255, 218, 0.3);
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }

        .last-check { text-align: center; color: #8892b0; margin-top: 20px; font-size: 0.9em; }
        .no-data { text-align: center; color: #8892b0; padding: 40px; }

        .alert {
            background: rgba(100, 255, 218, 0.2);
            border: 1px solid #64ffda;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>✈️ Flight Tracker</h1>
        <p class="route">{{ config.origin }} → {{ config.destination }}<br>
        {{ config.departure_date }} to {{ config.return_date }}</p>

        {% if alert %}
        <div class="alert">
            🔔 Price dropped ${{ "%.2f"|format(alert.drop_amount) }}! Now ${{ "%.2f"|format(alert.current_price) }}
        </div>
        {% endif %}

        {% if summary %}
        <div class="card price-display">
            <div class="current-price">${{ "%.0f"|format(summary.current) }}</div>
            <div class="price-label">Current Price (CAD)</div>

            <div class="target {% if summary.current <= target %}target-reached{% endif %}">
                {% if summary.current <= target %}
                    🎯 Target price of ${{ "%.0f"|format(target) }} reached!
                {% else %}
                    Target: ${{ "%.0f"|format(target) }} (need ${{ "%.0f"|format(summary.current - target) }} more drop)
                {% endif %}
            </div>
        </div>

        <div class="card">
            <div class="stats">
                <div>
                    <div class="stat-value stat-low">${{ "%.0f"|format(summary.lowest) }}</div>
                    <div class="stat-label">Lowest</div>
                </div>
                <div>
                    <div class="stat-value">${{ "%.0f"|format(summary.average) }}</div>
                    <div class="stat-label">Average</div>
                </div>
                <div>
                    <div class="stat-value stat-high">${{ "%.0f"|format(summary.highest) }}</div>
                    <div class="stat-label">Highest</div>
                </div>
            </div>
        </div>

        <div class="card">
            <h3 style="margin-bottom: 15px;">Price History</h3>
            <div class="history">
                {% for record in history[-10:]|reverse %}
                <div class="history-item">
                    <span class="history-price">${{ "%.2f"|format(record.price) }} - {{ record.airline }}</span>
                    <span class="history-time">{{ record.timestamp[:16].replace('T', ' ') }}</span>
                </div>
                {% endfor %}
            </div>
        </div>

        <p class="last-check">{{ summary.checks }} price checks recorded</p>

        {% else %}
        <div class="card no-data">
            <p>No price data yet. Click below to check prices!</p>
        </div>
        {% endif %}

        <div class="btn-container">
            <a href="/check" class="btn">🔄 Check Prices Now</a>
        </div>
    </div>
</body>
</html>
"""


@app.route("/")
def index():
    """Main dashboard page."""
    config = FLIGHT_CONFIG

    summary = tracker.get_price_summary(
        config["origin"],
        config["destination"],
        config["departure_date"],
        config["return_date"],
    )

    history = tracker.get_price_history(
        config["origin"],
        config["destination"],
        config["departure_date"],
        config["return_date"],
    )

    return render_template_string(
        HTML_TEMPLATE,
        config=config,
        summary=summary,
        history=history,
        target=PRICE_TARGET,
        alert=None,
    )


@app.route("/check")
def check_prices():
    """Check current prices and redirect back to dashboard."""
    if not searcher:
        return "API key not configured", 500

    config = FLIGHT_CONFIG

    flight = searcher.get_cheapest_flight(
        origin=config["origin"],
        destination=config["destination"],
        departure_date=config["departure_date"],
        return_date=config["return_date"],
        adults=config["adults"],
        bags=config["bags"],
    )

    if flight:
        alert = tracker.record_price(
            origin=config["origin"],
            destination=config["destination"],
            departure_date=config["departure_date"],
            return_date=config["return_date"],
            price=flight.price,
            currency=flight.currency,
            airline=flight.airline,
        )

        # Send notification if price dropped
        if alert:
            notifier.send_alert(alert)

    return redirect(url_for("index"))


@app.route("/api/prices")
def api_prices():
    """API endpoint for price data."""
    config = FLIGHT_CONFIG

    summary = tracker.get_price_summary(
        config["origin"],
        config["destination"],
        config["departure_date"],
        config["return_date"],
    )

    history = tracker.get_price_history(
        config["origin"],
        config["destination"],
        config["departure_date"],
        config["return_date"],
    )

    return jsonify({
        "summary": summary,
        "history": history,
        "config": config,
        "target": PRICE_TARGET,
    })


if __name__ == "__main__":
    print("\n🌐 Starting Flight Price Tracker Web Dashboard")
    print("   Open http://localhost:5000 in your browser\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
