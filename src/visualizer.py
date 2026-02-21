"""
Visualizer Module

Module for generating visualization reports from DeFi protocol data.
"""

import os
from typing import Dict, List
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import numpy as np


class Visualizer:
    """Creates visualizations for DeFi protocol data."""

    def __init__(self, config: Dict):
        """
        Initialize visualizer.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.viz_config = config.get('visualization', {})
        self.storage_config = config.get('storage', {})

        self.enabled = self.viz_config.get('enabled', True)
        self.chart_theme = self.viz_config.get('chart_theme', 'dark_background')
        self.chart_size = tuple(self.viz_config.get('chart_size', [12, 8]))
        self.save_format = self.viz_config.get('save_format', 'png')
        self.dpi = self.viz_config.get('dpi', 150)

        # Ensure report directory exists
        self.report_dir = self.storage_config.get('report_dir', 'reports')
        os.makedirs(self.report_dir, exist_ok=True)

        # Set matplotlib style
        plt.style.use(self.chart_theme)

    def generate_report(self, data: List[Dict]) -> str:
        """
        Generate a comprehensive visualization report.

        Args:
            data: List of protocol data dictionaries

        Returns:
            Path to the saved report
        """
        if not self.enabled or not data:
            print("[WARN] Visualization disabled or no data available")
            return None

        # Filter out protocols with errors
        valid_data = [d for d in data if d.get('tvl') or d.get('price')]

        if not valid_data:
            print("[WARN] No valid data for visualization")
            return None

        # Create figure with subplots
        fig = plt.figure(figsize=self.chart_size)
        fig.suptitle('DeFi Monitor Report', fontsize=16, fontweight='bold', y=0.98)

        # Create grid layout
        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

        # 1. TVL Comparison (top-left)
        self._plot_tvl_comparison(fig.add_subplot(gs[0, 0]), valid_data)

        # 2. Price Comparison (top-right)
        self._plot_price_comparison(fig.add_subplot(gs[0, 1]), valid_data)

        # 3. APY Comparison (bottom-left)
        self._plot_apy_comparison(fig.add_subplot(gs[1, 0]), valid_data)

        # 4. Summary Table (bottom-right)
        self._plot_summary_table(fig.add_subplot(gs[1, 1]), valid_data)

        # Add timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        fig.text(0.5, 0.02, f'Generated: {timestamp}', ha='center', fontsize=10, alpha=0.7)

        # Save report
        filename = f"defi_report_{datetime.now().strftime('%Y%m%d_%H%M')}.{self.save_format}"
        filepath = os.path.join(self.report_dir, filename)

        plt.savefig(filepath, dpi=self.dpi, bbox_inches='tight', facecolor='auto')
        plt.close()

        print(f"[INFO] Report saved to: {filepath}")
        return filepath

    def _plot_tvl_comparison(self, ax, data: List[Dict]):
        """Plot TVL comparison."""
        protocols = [d['name'].upper() for d in data]
        tvls = [d.get('tvl', 0) / 1e9 for d in data]  # Convert to billions

        colors = ['#00d4aa', '#00a8ff', '#f39c12', '#e74c3c', '#9b59b6'][:len(protocols)]

        bars = ax.bar(protocols, tvls, color=colors, alpha=0.8, edgecolor='white', linewidth=2)

        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'${height:.2f}B',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')

        ax.set_title('Total Value Locked (TVL)', fontsize=12, fontweight='bold', pad=10)
        ax.set_ylabel('TVL (Billion USD)', fontsize=10)
        ax.set_xlabel('Protocol', fontsize=10)
        ax.grid(axis='y', alpha=0.3)

    def _plot_price_comparison(self, ax, data: List[Dict]):
        """Plot price comparison."""
        # Filter protocols with price data
        price_data = [d for d in data if d.get('price')]

        if not price_data:
            ax.text(0.5, 0.5, 'No price data available', ha='center', va='center',
                   fontsize=12, transform=ax.transAxes)
            ax.set_title('Token Price', fontsize=12, fontweight='bold')
            return

        protocols = [d['name'].upper() for d in price_data]
        prices = [d.get('price', 0) for d in price_data]
        colors = ['#00d4aa', '#00a8ff', '#f39c12', '#e74c3c'][:len(protocols)]

        bars = ax.bar(protocols, prices, color=colors, alpha=0.8, edgecolor='white', linewidth=2)

        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'${height:.4f}',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')

        ax.set_title('Token Price', fontsize=12, fontweight='bold', pad=10)
        ax.set_ylabel('Price (USD)', fontsize=10)
        ax.set_xlabel('Protocol', fontsize=10)
        ax.grid(axis='y', alpha=0.3)

    def _plot_apy_comparison(self, ax, data: List[Dict]):
        """Plot APY comparison."""
        # Filter protocols with APY data
        apy_data = [d for d in data if d.get('apy')]

        if not apy_data:
            ax.text(0.5, 0.5, 'No APY data available', ha='center', va='center',
                   fontsize=12, transform=ax.transAxes)
            ax.set_title('Annual Percentage Yield', fontsize=12, fontweight='bold')
            return

        protocols = [d['name'].upper() for d in apy_data]
        apys = [d.get('apy', 0) for d in apy_data]
        colors = ['#00d4aa', '#00a8ff', '#f39c12', '#e74c3c'][:len(protocols)]

        bars = ax.bar(protocols, apys, color=colors, alpha=0.8, edgecolor='white', linewidth=2)

        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}%',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')

        ax.set_title('Annual Percentage Yield (APY)', fontsize=12, fontweight='bold', pad=10)
        ax.set_ylabel('APY (%)', fontsize=10)
        ax.set_xlabel('Protocol', fontsize=10)
        ax.grid(axis='y', alpha=0.3)

    def _plot_summary_table(self, ax, data: List[Dict]):
        """Plot summary table."""
        ax.axis('off')
        ax.set_title('Summary', fontsize=12, fontweight='bold', pad=10, loc='left')

        # Prepare table data
        table_data = []
        headers = ['Protocol', 'TVL', 'Price', 'APY', '24h Change']

        for d in data:
            name = d['name'].upper()
            tvl = f"${d.get('tvl', 0)/1e9:.2f}B" if d.get('tvl') else "N/A"
            price = f"${d.get('price', 0):.4f}" if d.get('price') else "N/A"
            apy = f"{d.get('apy', 0):.2f}%" if d.get('apy') else "N/A"
            change_24h = d.get('change_24h', 0)

            # Color code 24h change
            if change_24h:
                change_str = f"{change_24h:+.2f}%"
            else:
                change_price = d.get('change_24h_price', 0)
                change_str = f"{change_price:+.2f}%" if change_price else "N/A"

            table_data.append([name, tvl, price, apy, change_str])

        # Create table
        table = ax.table(
            cellText=table_data,
            colLabels=headers,
            cellLoc='center',
            loc='center',
            bbox=[0, 0, 1, 1]
        )

        # Style the table
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2)

        # Style header row
        for i in range(len(headers)):
            table[(0, i)].set_facecolor('#00a8ff')
            table[(0, i)].set_text_props(weight='bold', color='white')

        # Alternate row colors
        for i in range(1, len(table_data) + 1):
            if i % 2 == 0:
                for j in range(len(headers)):
                    table[(i, j)].set_facecolor('#1a1a2e')

    def generate_text_report(self, data: List[Dict]) -> str:
        """
        Generate a text-based summary report.

        Args:
            data: List of protocol data dictionaries

        Returns:
            Text report string
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        report = []
        report.append("=" * 60)
        report.append("DeFi Monitor Report")
        report.append("=" * 60)
        report.append(f"Generated: {timestamp}")
        report.append("")

        for d in data:
            report.append(f"\n{'─' * 60}")
            report.append(f"Protocol: {d['name'].upper()} ({d.get('symbol', '')})")
            report.append(f"{'─' * 60}")

            if d.get('tvl'):
                report.append(f"  TVL:           ${d['tvl']:,.0f}")
                if d.get('change_24h'):
                    report.append(f"  24h Change:    {d['change_24h']:+.2f}%")

            if d.get('price'):
                report.append(f"  Price:         ${d['price']:.4f}")
                if d.get('change_24h_price'):
                    report.append(f"  24h Change:    {d['change_24h_price']:+.2f}%")

            if d.get('apy'):
                report.append(f"  APY:           {d['apy']:.2f}%")

            if d.get('market_cap'):
                report.append(f"  Market Cap:    ${d['market_cap']:,.0f}")

            if d.get('error'):
                report.append(f"  Error:         {d['error']}")

        report.append("\n" + "=" * 60)
        report.append("End of Report")
        report.append("=" * 60)

        return "\n".join(report)
