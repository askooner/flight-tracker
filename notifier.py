"""
Notification module - sends alerts via email or console.
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from price_tracker import PriceAlert


class Notifier:
    """Send notifications for price alerts."""

    def __init__(
        self,
        email_enabled: bool = False,
        smtp_email: str = "",
        smtp_password: str = "",
        notify_email: str = "",
    ):
        self.email_enabled = email_enabled
        self.smtp_email = smtp_email
        self.smtp_password = smtp_password
        self.notify_email = notify_email

    @classmethod
    def from_env(cls) -> "Notifier":
        """Create notifier from environment variables."""
        return cls(
            email_enabled=os.getenv("EMAIL_ENABLED", "false").lower() == "true",
            smtp_email=os.getenv("SMTP_EMAIL", ""),
            smtp_password=os.getenv("SMTP_PASSWORD", ""),
            notify_email=os.getenv("NOTIFY_EMAIL", ""),
        )

    def send_alert(self, alert: PriceAlert):
        """Send a price drop alert."""
        # Always print to console
        self._console_alert(alert)

        # Send email if enabled
        if self.email_enabled:
            self._email_alert(alert)

    def _console_alert(self, alert: PriceAlert):
        """Print alert to console with formatting."""
        print("\n" + "=" * 50)
        print("🔔 " + str(alert))
        print("=" * 50 + "\n")

    def _email_alert(self, alert: PriceAlert):
        """Send alert via email."""
        if not all([self.smtp_email, self.smtp_password, self.notify_email]):
            print("Email not configured properly, skipping email notification")
            return

        try:
            msg = MIMEMultipart()
            msg["From"] = self.smtp_email
            msg["To"] = self.notify_email
            msg["Subject"] = f"Flight Price Drop! {alert.route} - Save ${alert.drop_amount:.2f}"

            body = f"""
Flight Price Drop Alert!

{str(alert)}

---
This alert was sent by your Flight Price Tracker.
            """

            msg.attach(MIMEText(body, "plain"))

            # Use Gmail SMTP
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(self.smtp_email, self.smtp_password)
                server.send_message(msg)

            print(f"Email alert sent to {self.notify_email}")

        except Exception as e:
            print(f"Failed to send email: {e}")

    def send_summary(self, summary: dict):
        """Send a price tracking summary."""
        print("\n" + "-" * 40)
        print("📊 Price Tracking Summary")
        print("-" * 40)
        print(f"Route: {summary['route']}")
        print(f"Travel Dates: {summary['dates']}")
        print(f"Price Checks: {summary['checks']}")
        print(f"Current Price: ${summary['current']:.2f}")
        print(f"Lowest Price: ${summary['lowest']:.2f}")
        print(f"Highest Price: ${summary['highest']:.2f}")
        print(f"Average Price: ${summary['average']:.2f}")
        print("-" * 40 + "\n")
