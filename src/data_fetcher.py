"""
Data Fetcher Module

Main data fetching module that coordinates data collection from various sources.
"""

import time
from typing import Dict, List, Optional
from .defi_llama import DefiLlamaAPI
from .coingecko import CoinGeckoAPI
from .web3_integration import Web3Manager


class DataFetcher:
    """Main data fetcher that coordinates multiple data sources."""

    def __init__(self, config: Dict):
        """
        Initialize data fetcher with configuration.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.defillama = DefiLlamaAPI(config.get('apis', {}).get('defillama', {}))
        self.coingecko = CoinGeckoAPI(config.get('apis', {}).get('coingecko', {}))
        self.web3 = Web3Manager(config.get('apis', {}).get('web3', {}))

    def fetch_protocol_data(self, protocol: Dict) -> Dict:
        """
        Fetch all data for a single protocol.

        Args:
            protocol: Protocol configuration dictionary

        Returns:
            Dictionary containing protocol data
        """
        name = protocol['name']
        defillama_slug = protocol.get('defillama_slug')
        coingecko_id = protocol.get('coingecko_id')

        print(f"[INFO] Fetching data for {name.upper()}...")

        data = {
            'name': name,
            'symbol': protocol.get('symbol', ''),
            'description': protocol.get('description', ''),
            'timestamp': time.time(),
            'tvl': None,
            'price': None,
            'apy': None,
            'change_24h': None,
            'error': None
        }

        # Fetch TVL from DefiLlama
        if defillama_slug:
            try:
                tvl_data = self.defillama.get_protocol_tvl(defillama_slug)
                if tvl_data:
                    data['tvl'] = tvl_data.get('tvl')
                    data['change_1h'] = tvl_data.get('change_1h')
                    data['change_24h'] = tvl_data.get('change_24h')
                    data['change_7d'] = tvl_data.get('change_7d')
                    print(f"[INFO]   TVL: ${self._format_number(data['tvl'])}")
            except Exception as e:
                print(f"[ERROR] Failed to fetch TVL for {name}: {e}")
                data['error'] = str(e)

        # Fetch price from CoinGecko
        if coingecko_id:
            try:
                price_data = self.coingecko.get_token_price(coingecko_id)
                if price_data:
                    data['price'] = price_data.get('price')
                    data['change_24h_price'] = price_data.get('change_24h')
                    data['market_cap'] = price_data.get('market_cap')
                    print(f"[INFO]   Price: ${self._format_number(data['price'])}")
            except Exception as e:
                print(f"[ERROR] Failed to fetch price for {name}: {e}")
                data['error'] = str(e)

        # Try to get APY from DefiLlama yields
        if defillama_slug:
            try:
                apy_data = self.defillama.get_protocol_yields(defillama_slug)
                if apy_data and len(apy_data) > 0:
                    # Get the average APY or the first pool's APY
                    apy_values = [pool.get('apy', 0) for pool in apy_data if pool.get('apy')]
                    if apy_values:
                        data['apy'] = sum(apy_values) / len(apy_values)
                        print(f"[INFO]   APY: {data['apy']:.2f}%")
            except Exception as e:
                print(f"[WARN] Failed to fetch APY for {name}: {e}")

        # Add Web3 data if available
        try:
            web3_data = self.web3.get_protocol_info(name.lower())
            if web3_data:
                data['web3'] = web3_data
        except Exception as e:
            print(f"[WARN] Failed to fetch Web3 data for {name}: {e}")

        return data

    def fetch_all_protocols(self, protocols: List[Dict]) -> List[Dict]:
        """
        Fetch data for all configured protocols.

        Args:
            protocols: List of protocol configurations

        Returns:
            List of protocol data dictionaries
        """
        results = []

        for protocol in protocols:
            try:
                data = self.fetch_protocol_data(protocol)
                results.append(data)
            except Exception as e:
                print(f"[ERROR] Error processing {protocol['name']}: {e}")
                results.append({
                    'name': protocol['name'],
                    'error': str(e)
                })

        return results

    def _format_number(self, num: Optional[float]) -> str:
        """Format number for display."""
        if num is None:
            return "N/A"
        if num >= 1e9:
            return f"{num / 1e9:.2f}B"
        elif num >= 1e6:
            return f"{num / 1e6:.2f}M"
        elif num >= 1e3:
            return f"{num / 1e3:.2f}K"
        else:
            return f"{num:.2f}"
