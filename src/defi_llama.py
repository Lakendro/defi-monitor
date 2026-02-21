"""
DefiLlama API Integration

Module for fetching DeFi protocol data from DefiLlama API.
"""

import time
import requests
from typing import Dict, List, Optional


class DefiLlamaAPI:
    """DefiLlama API client."""

    def __init__(self, config: Dict):
        """
        Initialize DefiLlama API client.

        Args:
            config: Configuration dictionary
        """
        self.base_url = config.get('base_url', 'https://api.llama.fi')
        self.rate_limit = config.get('rate_limit', 100)
        self.last_request_time = 0
        self.min_request_interval = 60 / self.rate_limit

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'DeFi-Monitor/1.0'
        })

    def _make_request(self, endpoint: str) -> Optional[Dict]:
        """
        Make a rate-limited request to DefiLlama API.

        Args:
            endpoint: API endpoint

        Returns:
            Response data or None on error
        """
        # Rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)

        url = f"{self.base_url}{endpoint}"

        try:
            response = self.session.get(url, timeout=30)
            self.last_request_time = time.time()

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] DefiLlama API request failed: {e}")
            return None

    def get_protocol_tvl(self, slug: str) -> Optional[Dict]:
        """
        Get TVL data for a specific protocol.

        Args:
            slug: Protocol slug (e.g., 'aave-v3')

        Returns:
            TVL data dictionary
        """
        data = self._make_request(f"/protocol/{slug}")

        if data and 'tvl' in data:
            return {
                'tvl': data.get('tvl'),
                'change_1h': data.get('change_1h'),
                'change_24h': data.get('change_24h'),
                'change_7d': data.get('change_7d'),
                'chainTvls': data.get('chainTvls', {}),
                'symbol': data.get('symbol'),
                'name': data.get('name')
            }

        return None

    def get_protocol_yields(self, slug: str) -> Optional[List[Dict]]:
        """
        Get yield data for a specific protocol.

        Args:
            slug: Protocol slug

        Returns:
            List of yield pools
        """
        # Get all yields
        all_yields = self._make_request("/yields")

        if not all_yields or 'data' not in all_yields:
            return None

        # Filter by protocol slug
        protocol_yields = [
            pool for pool in all_yields['data']
            if pool.get('project') == slug
        ]

        return protocol_yields if protocol_yields else None

    def get_protocol_history(self, slug: str) -> Optional[List[Dict]]:
        """
        Get historical TVL data for a protocol.

        Args:
            slug: Protocol slug

        Returns:
            List of historical data points
        """
        return self._make_request(f"/protocol/{slug}")

    def get_protocols_list(self) -> Optional[List[Dict]]:
        """
        Get list of all protocols on DefiLlama.

        Returns:
            List of protocol data
        """
        return self._make_request("/protocols")

    def get_chain_tvl(self, chain: str) -> Optional[Dict]:
        """
        Get TVL data for a specific chain.

        Args:
            chain: Chain name (e.g., 'ethereum')

        Returns:
            Chain TVL data
        """
        return self._make_request(f"/v2/chains/{chain}")

    def search_protocols(self, query: str) -> Optional[List[Dict]]:
        """
        Search for protocols.

        Args:
            query: Search query

        Returns:
            List of matching protocols
        """
        protocols = self.get_protocols_list()
        if not protocols:
            return None

        query_lower = query.lower()
        return [
            p for p in protocols
            if query_lower in p.get('name', '').lower() or
               query_lower in p.get('symbol', '').lower()
        ]
