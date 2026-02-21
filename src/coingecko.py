"""
CoinGecko API Integration

Module for fetching token price and market data from CoinGecko API.
"""

import time
import requests
from typing import Dict, List, Optional


class CoinGeckoAPI:
    """CoinGecko API client."""

    def __init__(self, config: Dict):
        """
        Initialize CoinGecko API client.

        Args:
            config: Configuration dictionary
        """
        self.base_url = config.get('base_url', 'https://api.coingecko.com/api/v3')
        self.api_key = config.get('api_key', '')
        self.rate_limit = config.get('rate_limit', 30)
        self.last_request_time = 0
        self.min_request_interval = 60 / self.rate_limit

        self.session = requests.Session()
        headers = {'User-Agent': 'DeFi-Monitor/1.0'}
        if self.api_key:
            headers['x-cg-demo-api-key'] = self.api_key
        self.session.headers.update(headers)

    def _make_request(self, endpoint: str) -> Optional[Dict]:
        """
        Make a rate-limited request to CoinGecko API.

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

            # Rate limit hit (429)
            if response.status_code == 429:
                print("[WARN] CoinGecko API rate limit hit. Waiting 60 seconds...")
                time.sleep(60)
                return self._make_request(endpoint)

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] CoinGecko API request failed: {e}")
            return None

    def get_token_price(self, coin_id: str, vs_currency: str = 'usd') -> Optional[Dict]:
        """
        Get current price for a token.

        Args:
            coin_id: CoinGecko coin ID (e.g., 'bitcoin', 'ethereum', 'aave')
            vs_currency: Currency to compare against (default: 'usd')

        Returns:
            Price data dictionary
        """
        data = self._make_request(
            f"/simple/price?ids={coin_id}&vs_currencies={vs_currency}&"
            f"include_24hr_change=true&include_market_cap=true"
        )

        if data and coin_id in data:
            return {
                'price': data[coin_id].get(vs_currency),
                'change_24h': data[coin_id].get(f'{vs_currency}_24h_change'),
                'market_cap': data[coin_id].get(f'{vs_currency}_market_cap')
            }

        return None

    def get_token_details(self, coin_id: str) -> Optional[Dict]:
        """
        Get detailed information about a token.

        Args:
            coin_id: CoinGecko coin ID

        Returns:
            Token details dictionary
        """
        return self._make_request(f"/coins/{coin_id}")

    def get_token_market_data(self, coin_id: str, days: int = 7) -> Optional[List[Dict]]:
        """
        Get market chart data for a token.

        Args:
            coin_id: CoinGecko coin ID
            days: Number of days of data (1, 7, 30, etc.)

        Returns:
            List of [timestamp, price] pairs
        """
        data = self._make_request(f"/coins/{coin_id}/market_chart?vs_currency=usd&days={days}")

        if data and 'prices' in data:
            return data['prices']

        return None

    def get_token_contract_data(self, contract_address: str, platform: str = 'ethereum') -> Optional[Dict]:
        """
        Get token data by contract address.

        Args:
            contract_address: Token contract address
            platform: Blockchain platform (default: 'ethereum')

        Returns:
            Token data dictionary
        """
        return self._make_request(
            f"/coins/{platform}/contract/{contract_address}"
        )

    def get_top_tokens(self, vs_currency: str = 'usd', per_page: int = 50, page: int = 1) -> Optional[List[Dict]]:
        """
        Get top tokens by market cap.

        Args:
            vs_currency: Currency to compare against
            per_page: Number of results per page
            page: Page number

        Returns:
            List of token data
        """
        data = self._make_request(
            f"/coins/markets?vs_currency={vs_currency}&order=market_cap_desc&"
            f"per_page={per_page}&page={page}&sparkline=false"
        )

        return data if isinstance(data, list) else None

    def search_tokens(self, query: str) -> Optional[List[Dict]]:
        """
        Search for tokens.

        Args:
            query: Search query

        Returns:
            List of matching tokens
        """
        data = self._make_request(f"/search?query={query}")

        if data and 'coins' in data:
            return data['coins']

        return None

    def get_exchange_rate(self, from_currency: str, to_currency: str = 'usd') -> Optional[float]:
        """
        Get exchange rate between currencies.

        Args:
            from_currency: Source currency code (e.g., 'btc', 'eth')
            to_currency: Target currency code

        Returns:
            Exchange rate
        """
        data = self.get_token_price(from_currency, to_currency)

        if data:
            return data.get('price')

        return None
