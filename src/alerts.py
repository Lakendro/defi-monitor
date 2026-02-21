"""
Alerts Module

Module for sending alerts when thresholds are exceeded.
"""

import os
import smtplib
import json
from typing import Dict, List
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests


class AlertManager:
    """Manages alerts for DeFi protocol data."""

    def __init__(self, config: Dict):
        """
        Initialize alert manager.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.alerts_config = config.get('alerts', {})
        self.enabled = self.alerts_config.get('enabled', False)

        # Load environment variables
        self.discord_webhook_url = os.getenv('DISCORD_WEBHOOK_URL', '')
        self.email_to = os.getenv('ALERT_EMAIL', '')
        self.email_from = os.getenv('ALERT_EMAIL_FROM', '')
        self.smtp_username = os.getenv('SMTP_USERNAME', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')

        # Thresholds
        self.price_threshold = self.alerts_config.get('price_change_threshold', 5.0)
        self.tvl_threshold = self.alerts_config.get('tvl_change_threshold', 10.0)
        self.apy_threshold = self.alerts_config.get('apy_change_threshold', 1.0)

        # Track previous data for comparison
        self.previous_data = {}

    def check_alerts(self, current_data: List[Dict]) -> List[Dict]:
        """
        Check if any alerts should be triggered.

        Args:
            current_data: Current protocol data

        Returns:
            List of alerts to send
        """
        if not self.enabled:
            return []

        alerts = []

        for protocol_data in current_data:
            protocol_name = protocol_data['name']

            # Skip if we don't have previous data
            if protocol_name not in self.previous_data:
                self.previous_data[protocol_name] = protocol_data
                continue

            prev_data = self.previous_data[protocol_name]

            # Check price change
            alert = self._check_price_change(protocol_name, prev_data, protocol_data)
            if alert:
                alerts.append(alert)

            # Check TVL change
            alert = self._check_tvl_change(protocol_name, prev_data, protocol_data)
            if alert:
                alerts.append(alert)

            # Check APY change
            alert = self._check_apy_change(protocol_name, prev_data, protocol_data)
            if alert:
                alerts.append(alert)

        # Update previous data
        for protocol_data in current_data:
            self.previous_data[protocol_data['name']] = protocol_data

        return alerts

    def _check_price_change(self, name: str, prev: Dict, curr: Dict) -> Dict:
        """Check for significant price changes."""
        if prev.get('price') and curr.get('price'):
            change_percent = ((curr['price'] - prev['price']) / prev['price']) * 100

            if abs(change_percent) >= self.price_threshold:
                direction = "📈 INCREASED" if change_percent > 0 else "📉 DECREASED"
                return {
                    'type': 'price',
                    'protocol': name,
                    'severity': 'HIGH' if abs(change_percent) >= 10 else 'MEDIUM',
                    'message': f"{direction} by {abs(change_percent):.2f}%!\n"
                               f"Previous: ${prev['price']:.4f}\n"
                               f"Current: ${curr['price']:.4f}",
                    'timestamp': datetime.now().isoformat()
                }

        return None

    def _check_tvl_change(self, name: str, prev: Dict, curr: Dict) -> Dict:
        """Check for significant TVL changes."""
        if prev.get('tvl') and curr.get('tvl'):
            change_percent = ((curr['tvl'] - prev['tvl']) / prev['tvl']) * 100

            if abs(change_percent) >= self.tvl_threshold:
                direction = "📈 INCREASED" if change_percent > 0 else "📉 DECREASED"
                return {
                    'type': 'tvl',
                    'protocol': name,
                    'severity': 'HIGH' if abs(change_percent) >= 20 else 'MEDIUM',
                    'message': f"{direction} by {abs(change_percent):.2f}%!\n"
                               f"Previous: ${prev['tvl']:,.0f}\n"
                               f"Current: ${curr['tvl']:,.0f}",
                    'timestamp': datetime.now().isoformat()
                }

        return None

    def _check_apy_change(self, name: str, prev: Dict, curr: Dict) -> Dict:
        """Check for significant APY changes."""
        if prev.get('apy') and curr.get('apy'):
            change = curr['apy'] - prev['apy']

            if abs(change) >= self.apy_threshold:
                direction = "📈 INCREASED" if change > 0 else "📉 DECREASED"
                return {
                    'type': 'apy',
                    'protocol': name,
                    'severity': 'MEDIUM',
                    'message': f"{direction} by {abs(change):.2f}%!\n"
                               f"Previous: {prev['apy']:.2f}%\n"
                               f"Current: {curr['apy']:.2f}%",
                    'timestamp': datetime.now().isoformat()
                }

        return None

    def send_alerts(self, alerts: List[Dict]) -> int:
        """
        Send alerts through configured channels.

        Args:
            alerts: List of alert dictionaries

        Returns:
            Number of alerts sent
        """
        if not alerts:
            return 0

        count = 0

        # Console output
        if self.alerts_config.get('console', True):
            self._send_console_alerts(alerts)
            count += len(alerts)

        # Discord webhook
        if self.alerts_config.get('discord_webhook', False) and self.discord_webhook_url:
            if self._send_discord_alerts(alerts):
                count += len(alerts)

        # Email
        if self.alerts_config.get('email', False) and self.email_to:
            if self._send_email_alerts(alerts):
                count += len(alerts)

        return count

    def _send_console_alerts(self, alerts: List[Dict]) -> bool:
        """Send alerts to console."""
        print("\n" + "="*60)
        print("🚨 ALERTS TRIGGERED")
        print("="*60)

        for alert in alerts:
            print(f"\n[{alert['severity']}] {alert['protocol'].upper()} - {alert['type'].upper()}")
            print(alert['message'])
            print(f"Time: {alert['timestamp']}")

        print("="*60 + "\n")
        return True

    def _send_discord_alerts(self, alerts: List[Dict]) -> bool:
        """Send alerts to Discord webhook."""
        try:
            for alert in alerts:
                embed = {
                    "title": f"🚨 DeFi Alert: {alert['protocol'].upper()}",
                    "description": alert['message'],
                    "color": 0xff0000 if alert['severity'] == 'HIGH' else 0xffff00,
                    "fields": [
                        {"name": "Type", "value": alert['type'].upper(), "inline": True},
                        {"name": "Severity", "value": alert['severity'], "inline": True},
                        {"name": "Time", "value": alert['timestamp'], "inline": False}
                    ]
                }

                response = requests.post(
                    self.discord_webhook_url,
                    json={"embeds": [embed]},
                    timeout=10
                )

                response.raise_for_status()

            return True

        except Exception as e:
            print(f"[ERROR] Failed to send Discord alerts: {e}")
            return False

    def _send_email_alerts(self, alerts: List[Dict]) -> bool:
        """Send alerts via email."""
        try:
            if not all([self.email_to, self.email_from, self.smtp_username, self.smtp_password]):
                print("[WARN] Email credentials not fully configured")
                return False

            msg = MIMEMultipart()
            msg['From'] = self.email_from
            msg['To'] = self.email_to
            msg['Subject'] = f"🚨 DeFi Monitor Alerts - {datetime.now().strftime('%Y-%m-%d %H:%M')}"

            body = "The following alerts were triggered:\n\n"
            for alert in alerts:
                body += f"\n{'='*60}\n"
                body += f"[{alert['severity']}] {alert['protocol'].upper()} - {alert['type'].upper()}\n"
                body += alert['message'] + "\n"
                body += f"Time: {alert['timestamp']}\n"

            msg.attach(MIMEText(body, 'plain'))

            smtp_server = self.alerts_config.get('smtp_server', 'smtp.gmail.com')
            smtp_port = self.alerts_config.get('smtp_port', 587)

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            print("[INFO] Email alerts sent successfully")
            return True

        except Exception as e:
            print(f"[ERROR] Failed to send email alerts: {e}")
            return False
